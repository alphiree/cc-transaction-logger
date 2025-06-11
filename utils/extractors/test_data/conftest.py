"""
Pytest configuration for email extractor tests.
"""

import importlib
import os
import sys

import pytest

# Add the parent directory to path to allow imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from utils.extractors import EXTRACTOR_REGISTRY
from utils.extractors.test_data import available_tests


@pytest.fixture
def extractor_registry():
    """Fixture to provide the extractor registry."""
    return EXTRACTOR_REGISTRY


@pytest.fixture
def test_data_modules():
    """Fixture to provide access to all test data modules."""
    modules = {}
    for test_module_name in available_tests:
        try:
            module = importlib.import_module(
                f"utils.extractors.test_data.{test_module_name}"
            )
            # Get the extractor name from the module name (e.g., "foodpanda" from "foodpanda_email_template")
            extractor_name = test_module_name.split("_")[0].capitalize()
            modules[extractor_name] = module
        except ImportError as e:
            print(f"Error importing test module {test_module_name}: {e}")

    return modules
