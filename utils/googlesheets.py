import os
from datetime import datetime

import gspread
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread_formatting import (
    BooleanCondition,
    DataValidationRule,
    set_data_validation_for_cell_range,
)

load_dotenv()


class SheetManager:
    def __init__(self, credentials_path: str):
        """
        Initialize Google Sheets connection

        Args:
            credentials_path (str): Path to Google Service Account credentials JSON file
        """
        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        # Set up credentials
        credentials = Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )

        # Create gspread client
        self.client = gspread.authorize(credentials)

    def create_logger_sheet(
        self,
        spreadsheet_id: str,
        statement_day: int,
    ) -> gspread.Worksheet:
        sheet = self.client.open_by_key(spreadsheet_id)

        if datetime.now().day >= statement_day:
            month = str(datetime.now().month).zfill(2)
            year = datetime.now().year
            WORKSHEET_NAME = f"{year}{month}{statement_day}"
        else:
            month = datetime.now().month
            if month == 1:
                year = datetime.now().year - 1
                month = 12
            else:
                year = datetime.now().year
                month = month - 1

        WORKSHEET_NAME = f"{year}{str(month).zfill(2)}{str(statement_day).zfill(2)}"
        print(f"WORKSHEET_NAME: {WORKSHEET_NAME}")

        try:
            worksheet = sheet.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(WORKSHEET_NAME, rows=1, cols=1)

            # Get all worksheets
            worksheets = sheet.worksheets()

            # Reorder worksheets to move the new sheet to the 2nd position
            new_order = [worksheets[0], worksheet] + worksheets[
                1:
            ]  # Insert new sheet at 2nd place
            new_order.pop(-1)
            sheet.reorder_worksheets(new_order)

            headers = [
                "paid",
                "date",
                "card_number",
                "total_amount",
                "merchant",
                "payer",
                "",
                "",
            ]
            worksheet.update([headers])
            worksheet_widths = [75, 150, 100, 100, 250, 100, 15, 100]
            request_widths = [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": i,  # 0-based index
                            "endIndex": i + 1,
                        },
                        "properties": {
                            "pixelSize": width  # width for 'checked' column
                        },
                        "fields": "pixelSize",
                    }
                }
                for i, width in enumerate(worksheet_widths)
            ]
            request_type_format = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": worksheet.id,
                            "startRowIndex": 0,  # Skip header row
                            "endRowIndex": 1000,  # Adjust this number based on your needs
                            "startColumnIndex": 3,  # 0-based index for total_amount column
                            "endColumnIndex": 4,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "NUMBER",
                                    "pattern": "#,##0.00",  # Format for 2 decimal places
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat",
                    }
                }
            ]

            sheet.batch_update({"requests": request_widths})
            sheet.batch_update({"requests": request_type_format})

        return worksheet

    def update_logger_sheet(
        self,
        worksheet: gspread.Worksheet,
        df: pd.DataFrame,
        end_date: datetime,
    ) -> None:
        """
        Update the logger sheet with the new transactions

        Args:
            worksheet: The worksheet to update
            df: The dataframe containing the new transactions
        """

        if df.empty:
            print("No new transactions to update")
            return

        payer_users: list = os.getenv("PAYER_USERS", "user_1,user_2,others").split(",")

        checkbox_rule = DataValidationRule(
            BooleanCondition("BOOLEAN"),
            showCustomUi=True,  # Shows the checkbox UI in Google Sheets
        )
        validation_rule = DataValidationRule(
            BooleanCondition("ONE_OF_LIST", payer_users),
            showCustomUi=True,  # Shows the dropdown arrow
        )

        # Prepare the data
        data = []
        values_list = worksheet.col_values(5)  # 2 for column E (merchant column)
        last_row = len(
            [x for x in values_list if x.strip() != ""]
        )  # Count non-empty values

        for _, row in df.iterrows():
            data.append(
                [
                    False,
                    row["date"].strftime("%Y-%m-%d %H:%M:%S"),
                    row["card_number"],
                    row["total_paid_amount"],
                    row["merchant"],
                    payer_users[0],
                    "",
                ]
            )

        if data:
            # Check current row count and resize if necessary
            current_rows = worksheet.row_count
            needed_rows = (
                last_row + len(data) + 1
            )  # Current last row + new data + buffer

            # Resize if necessary
            if current_rows < needed_rows:
                worksheet.resize(rows=needed_rows, cols=8)

            # Get current data to find the last row with content
            values_list = worksheet.col_values(5)  # Column E (merchant column)
            last_row = len(
                [x for x in values_list if x.strip() != ""]
            )  # Count non-empty values

            # Update the sheet
            start_range = f"A{last_row + 1}"
            worksheet.update(start_range, data)

            set_data_validation_for_cell_range(worksheet, "A2:A1000", checkbox_rule)
            set_data_validation_for_cell_range(worksheet, "F2:F1000", validation_rule)

        print(f"Successfully uploaded {len(df)} transactions to Google Sheets")
