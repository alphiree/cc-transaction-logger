import email
import imaplib
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Union

import pytz


class Gmail:
    def __init__(
        self, email_address: str, password: str, test_connection: bool = False
    ):
        """
        Initialize Gmail class with email credentials

        Args:
            email_address (str): Gmail address
            password (str): App-specific password or account password
        """
        self.email_address = email_address
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"

        if test_connection:
            self.test_connection()

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email using Gmail SMTP

        Args:
            to_email (str): Recipient's email address
            subject (str): Email subject
            body (str): Email body content

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.email_address
            message["To"] = to_email
            message["Subject"] = subject

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            # Create SMTP session
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.password)
                server.send_message(message)

            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def read_emails(
        self,
        folder: str = "INBOX",
        limit: int = 5,
        search_string: str = None,
    ) -> List[Dict]:
        """
        Read emails from specified folder

        Args:
            folder (str): Email folder to read from (default: INBOX)
            limit (int): Maximum number of emails to retrieve (default: 5)
            search_string (str): IMAP search criteria (default: None)

        Returns:
            List[Dict]: List of dictionaries containing email information
        """
        try:
            # Connect to IMAP server
            imap_server = imaplib.IMAP4_SSL(self.imap_server)
            imap_server.login(self.email_address, self.password)

            # Select folder
            imap_server.select(folder)

            # Search for emails
            _, message_numbers = imap_server.search(None, search_string)

            email_list = []
            for num in message_numbers[0].split()[-limit:]:
                _, msg_data = imap_server.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Extract email information
                email_info = {
                    "from": email_message["from"],
                    "subject": email_message["subject"],
                    "date": email.utils.parsedate_to_datetime(
                        email_message["date"]
                    ).astimezone(pytz.timezone("Asia/Manila")),
                    "body": "",
                }

                # Get email body with improved content handling
                if email_message.is_multipart():
                    # Try to find text/plain first, then text/html
                    text_content = None
                    html_content = None

                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain" and not text_content:
                            text_content = part.get_payload(decode=True)
                        elif content_type == "text/html" and not html_content:
                            html_content = part.get_payload(decode=True)

                    # Prefer plain text, fall back to HTML if plain text is not available
                    if text_content:
                        try:
                            email_info["body"] = text_content.decode(
                                "utf-8", errors="replace"
                            )
                        except Exception:
                            email_info["body"] = text_content.decode(
                                "latin-1", errors="replace"
                            )
                    elif html_content:
                        try:
                            email_info["body"] = html_content.decode(
                                "utf-8", errors="replace"
                            )
                        except Exception:
                            email_info["body"] = html_content.decode(
                                "latin-1", errors="replace"
                            )
                else:
                    # Handle non-multipart messages
                    content_type = email_message.get_content_type()
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        try:
                            email_info["body"] = payload.decode(
                                "utf-8", errors="replace"
                            )
                        except Exception:
                            email_info["body"] = payload.decode(
                                "latin-1", errors="replace"
                            )

                email_list.append(email_info)

            imap_server.close()
            imap_server.logout()

            return email_list

        except Exception as e:
            print(f"Error reading emails: {str(e)}")
            return []

    def read_emails_filtered(
        self,
        sender: str = None,
        folder: str = "INBOX",
        date_interval: Union[List[datetime], None] = None,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Read emails from specified folder with sender and time filters

        Args:
            sender (str, optional): Filter emails from specific sender
            folder (str): Email folder to read from (default: INBOX)
            date_interval (List[datetime], optional): List containing [from_date, to_date]
                defaults to [yesterday, now]
            limit (int): Maximum number of emails to retrieve (default: 5)

        Returns:
            List[Dict]: List of dictionaries containing filtered email information
        """
        # Set default date interval if none provided
        if date_interval is None:
            now = datetime.now()
            date_interval = [now - timedelta(days=1), now]

        start_timestamp = int(date_interval[0].timestamp())
        end_timestamp = int(date_interval[1].timestamp())

        # Build search criteria
        search_criteria = []

        if sender:
            search_criteria.append(f"from:{sender}")

        # Add date range criteria using timestamps
        search_criteria.append(f"after:{start_timestamp} before:{end_timestamp}")

        # Combine all search criteria
        search_string = (
            'X-GM-RAW "' + " ".join(search_criteria) + '"' if search_criteria else "ALL"
        )

        return self.read_emails(folder, limit, search_string)

    def test_connection(self) -> Dict[str, bool]:
        """
        Test both SMTP and IMAP connections to verify credentials

        Returns:
            Dict[str, bool]: Dictionary with connection test results for SMTP and IMAP
        """
        results = {"smtp": False, "imap": False}

        # Test SMTP connection
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.password)
                results["smtp"] = True
                print("SMTP Connection Successful")
        except Exception as e:
            print(f"SMTP Connection Error: {str(e)}")

        # Test IMAP connection
        try:
            imap_server = imaplib.IMAP4_SSL(self.imap_server)
            imap_server.login(self.email_address, self.password)
            imap_server.logout()
            results["imap"] = True
            print("IMAP Connection Successful")
        except Exception as e:
            print(f"IMAP Connection Error: {str(e)}")

        return results
