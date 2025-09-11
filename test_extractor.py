#!/usr/bin/env python3
"""
Generic email extractor test tool.

This script allows you to test any email extractor (Foodpanda, Grab, Metrobank, etc.)
with real emails from your Gmail account.

Usage:
    uv run python test_extractor.py <merchant> [days_back]

Examples:
    uv run python test_extractor.py Foodpanda
    uv run python test_extractor.py Grab 7
    uv run python test_extractor.py Metrobank 14
"""

import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

from utils.extractors import TransactionExtractor, get_extractor_for_merchant, EXTRACTOR_REGISTRY
from utils.gmail import Gmail

load_dotenv()


def test_merchant_extractor(merchant_name, days_back=3):
    """
    Test email extraction for a specific merchant.
    
    Args:
        merchant_name (str): Name of the merchant (e.g., 'Foodpanda', 'Grab', 'Metrobank')
        days_back (int): Number of days to look back for emails (default: 3)
    """
    
    print(f"🔍 Testing {merchant_name} email extraction")
    print(f"📅 Searching emails from last {days_back} days")
    print("=" * 60)
    
    # Validate merchant
    if merchant_name not in EXTRACTOR_REGISTRY:
        print(f"❌ Error: '{merchant_name}' is not a valid merchant")
        print(f"Available merchants: {', '.join(EXTRACTOR_REGISTRY.keys())}")
        return
    
    # Initialize clients
    try:
        gmail_client = Gmail(os.getenv("GMAIL_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
        transaction_extractor = TransactionExtractor()
    except Exception as e:
        print(f"❌ Error initializing clients: {e}")
        print("Make sure your .env file has GMAIL_EMAIL and GMAIL_APP_PASSWORD set correctly")
        return
    
    # Set date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"🕐 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Get extractor and merchant email
    try:
        extractor = get_extractor_for_merchant(merchant_name)
        print(f"📧 Merchant email: {extractor.merchant_email}")
    except Exception as e:
        print(f"❌ Error getting extractor: {e}")
        return
    
    # Fetch emails
    print(f"\n🔎 Fetching emails from {merchant_name}...")
    try:
        emails = gmail_client.read_emails_filtered(
            sender=extractor.merchant_email,
            date_interval=[start_date, end_date],
            limit=20  # Reasonable limit to avoid too many results
        )
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return
    
    if not emails:
        print("❌ No emails found for the specified date range")
        print("\n💡 Troubleshooting tips:")
        print("  • Check if the date range includes when you received emails")
        print("  • Verify Gmail credentials are correct")
        print("  • Ensure the merchant email address is correct")
        return
    
    print(f"✅ Found {len(emails)} emails")
    
    # Analyze each email
    print(f"\n📊 Analyzing emails...")
    print("-" * 60)
    
    valid_extractions = 0
    
    for i, email_data in enumerate(emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"📅 Date: {email_data['date']}")
        print(f"📋 Subject: {email_data['subject']}")
        print(f"📄 Body preview: {email_data['body'][:100].replace(chr(10), ' ')[:100]}...")
        
        # Try extraction
        try:
            result = transaction_extractor.extract_from_email(
                merchant=merchant_name,
                email_body=email_data["body"],
                email_subject=email_data["subject"]
            )
            
            print(f"\n🔍 Extraction Results:")
            print(f"  💳 Card Number: {result.card_number}")
            print(f"  💰 Amount: {result.amount}")
            print(f"  🏪 Merchant: {result.merchant}")
            
            # Check if extraction was successful
            if result.card_number and result.amount:
                print("  ✅ Extraction successful!")
                valid_extractions += 1
            else:
                print("  ❌ Extraction failed - missing required data")
                
        except Exception as e:
            print(f"  ❌ Extraction error: {e}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📈 SUMMARY")
    print(f"📧 Total emails found: {len(emails)}")
    print(f"✅ Valid extractions: {valid_extractions}")
    print(f"❌ Failed extractions: {len(emails) - valid_extractions}")
    
    if valid_extractions > 0:
        print(f"\n🎉 Success! The {merchant_name} extractor is working correctly.")
    else:
        print(f"\n⚠️  No valid extractions found. The {merchant_name} extractor may need updates.")
        print(f"💡 Consider examining the email format and updating the extractor logic.")


def show_usage():
    """Show usage information."""
    print("Usage: python test_extractor.py <merchant> [days_back]")
    print()
    print("Arguments:")
    print("  merchant    : Name of the merchant to test (required)")
    print("  days_back   : Number of days to look back for emails (default: 3)")
    print()
    print("Available merchants:")
    for merchant in EXTRACTOR_REGISTRY.keys():
        print(f"  • {merchant}")
    print()
    print("Examples:")
    print("  python test_extractor.py Foodpanda")
    print("  python test_extractor.py Grab 7")
    print("  python test_extractor.py Metrobank 14")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Merchant name is required")
        print()
        show_usage()
        sys.exit(1)
    
    merchant = sys.argv[1]
    days = 3
    
    if len(sys.argv) > 2:
        try:
            days = int(sys.argv[2])
            if days <= 0:
                raise ValueError("Days must be positive")
        except ValueError as e:
            print(f"❌ Error: Invalid days_back value: {sys.argv[2]}")
            print("Days must be a positive integer")
            sys.exit(1)
    
    test_merchant_extractor(merchant, days)