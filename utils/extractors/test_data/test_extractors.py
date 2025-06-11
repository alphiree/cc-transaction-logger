"""
Pytest tests for email extractors.

This module contains tests for all email extractors using test data templates.
"""

import pytest


def test_all_extractors_registered(extractor_registry, test_data_modules):
    """Test that all extractors with test data are registered."""
    for extractor_name in test_data_modules:
        assert extractor_name in extractor_registry, (
            f"{extractor_name} extractor is not registered"
        )


@pytest.mark.parametrize(
    "extractor_name",
    [
        pytest.param("Foodpanda", id="foodpanda-extractor"),
        # Add more extractors here as they're implemented
    ],
)
def test_extractor(extractor_name, extractor_registry, test_data_modules):
    """Test individual extractors with their test data."""
    # Skip if the extractor is not in the registry
    if extractor_name not in extractor_registry:
        pytest.skip(f"{extractor_name} extractor not found in registry")

    # Skip if no test data module exists for this extractor
    if extractor_name not in test_data_modules:
        pytest.skip(f"No test data found for {extractor_name}")

    # Get the test data and extractor
    test_module = test_data_modules[extractor_name]
    test_data = test_module.get_test_data()
    extractor_class = extractor_registry[extractor_name].__class__

    # Create an instance of the extractor
    extractor = extractor_class()

    # Extract data from the test email
    email = test_data["email"]
    expected = test_data["expected"]
    result = extractor.extract_payment_info(email["body"], email["subject"])

    # Check extraction results
    assert result.card_number == expected["card_number"], (
        f"Card number mismatch: Expected {expected['card_number']}, got {result.card_number}"
    )

    assert result.amount == expected["amount"], (
        f"Amount mismatch: Expected {expected['amount']}, got {result.amount}"
    )

    assert result.merchant == expected["merchant"], (
        f"Merchant mismatch: Expected {expected['merchant']}, got {result.merchant}"
    )


def test_dynamic_extractors(extractor_registry, test_data_modules):
    """Dynamically test all extractors that have test data."""
    for extractor_name, test_module in test_data_modules.items():
        if extractor_name not in extractor_registry:
            pytest.skip(f"{extractor_name} extractor not found in registry")

        # Get the test data and extractor
        test_data = test_module.get_test_data()
        extractor_class = extractor_registry[extractor_name].__class__

        # Create an instance of the extractor
        extractor = extractor_class()

        # Extract data from the test email
        email = test_data["email"]
        expected = test_data["expected"]
        result = extractor.extract_payment_info(email["body"], email["subject"])

        # Check extraction results
        assert result.card_number == expected["card_number"], (
            f"Card number mismatch for {extractor_name}: Expected {expected['card_number']}, got {result.card_number}"
        )

        assert result.amount == expected["amount"], (
            f"Amount mismatch for {extractor_name}: Expected {expected['amount']}, got {result.amount}"
        )

        assert result.merchant == expected["merchant"], (
            f"Merchant mismatch for {extractor_name}: Expected {expected['merchant']}, got {result.merchant}"
        )
