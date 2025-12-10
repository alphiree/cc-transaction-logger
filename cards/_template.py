## To setup your card details for email filtering, copy this template and save as `cards.py`


class CreditCardName:
    NICKNAME: str = "Bank CC Visa"
    STATEMENT_DATE: str = "1"
    LAST_DIGITS: str = "1234"
    GOOGLE_SHEET_ID: str = "1234qwerty6789asdfghj1234zxcvbn1234qazwsxed"
    LAST_RUN_TIME_ENV_NAME: str = "LAST_RUNTIME_CC_NAME"  # set this up in .env

    MERCHANTS: list = [
        # Accepted merchants can be found in utils/extractors/__init__.py
        "Merchant_1",
        "Merchant_2",
        "Merchant_3",
    ]
