"""
Test data template for FoodPanda emails.

This module contains sample email data for testing the FoodPanda extractor.
These templates are simplified and anonymized versions without real customer data.
"""

# Sample email with "Your order has been placed" subject
FOODPANDA_ORDER_CONFIRMATION = {
    "from": "info@mail.foodpanda.ph",
    "subject": "Your order has been placed",
    "date": "2023-01-01 12:00:00",
    "body": """
foodpanda

Order info

Summary:
Order number: test-1234-abc
Order time: 2023-01-01 12:00:00

Hey Test User,

You're all set! Your order from Test Restaurant will be on its way soon.

Need a hand with something?
Just head over to the Help Center for assistance.
Track your order
Until next time,
Your foodpanda team

Qty | Item | Price
1 X | Test Food Item | ₱ 450.00

Subtotal: ₱ 450.00
Incl. delivery fee: ₱ 50.00

Order Total

 ₱
500.00

Including 12.00% tax: ₱ 53.57

Privacy | Terms and Conditions
© 2023 foodpanda
""",
}

# Expected extraction results
EXPECTED_RESULTS = {
    "card_number": "FPND",  # FoodPanda placeholder
    "amount": 500.00,  # Order Total
    "merchant": "Test Restaurant",  # Restaurant name
}


def get_test_data():
    """Returns a dictionary with test email data and expected extraction results"""
    return {"email": FOODPANDA_ORDER_CONFIRMATION, "expected": EXPECTED_RESULTS}
