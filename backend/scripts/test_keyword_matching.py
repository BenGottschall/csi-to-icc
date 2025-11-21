#!/usr/bin/env python3
"""
Test Keyword Matching System

This script tests the keyword-based CSI-to-ICC matching system with real data.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import CSICode, ICCSection
from app.keyword_matcher import KeywordMatcher


def test_keyword_matching():
    """
    Test keyword matching with sample CSI codes.
    """
    db = SessionLocal()

    try:
        print("="*70)
        print("KEYWORD MATCHING TEST")
        print("="*70)
        print()

        # Initialize matcher
        print("Initializing keyword matcher...")
        matcher = KeywordMatcher()
        matcher.initialize(db, icc_document_code="IPC")  # Use IPC sections only
        print()

        # Test cases - CSI codes related to plumbing
        test_codes = [
            "22 00 00",  # Plumbing (division level)
            "22 07 19",  # Plumbing Piping Insulation (detail level)
            "22 40 00",  # Plumbing Fixtures (subdivision level)
            "03 30 00",  # Cast-in-Place Concrete (not plumbing-related)
        ]

        for code_str in test_codes:
            # Get CSI code from database
            csi_code = db.query(CSICode).filter(CSICode.code == code_str).first()

            if not csi_code:
                print(f"⚠️  CSI code '{code_str}' not found in database")
                print()
                continue

            print(f"{'='*70}")
            print(f"Testing: {csi_code.code} - {csi_code.title}")
            print(f"{'='*70}")

            # Find matches
            matches = matcher.find_matches(csi_code, top_n=5, min_score=0.05)

            if not matches:
                print("❌ No matches found")
            else:
                print(f"✓ Found {len(matches)} matches:\n")

                for i, match in enumerate(matches, 1):
                    section = match['section']
                    score = match['score']
                    confidence = match['confidence']
                    keywords = match['matched_keywords']

                    print(f"{i}. IPC {section.section_number} - {section.title}")
                    print(f"   Score: {score:.3f} | Confidence: {confidence}")
                    print(f"   Matched keywords: {', '.join(keywords[:5])}")
                    if section.description:
                        # Show first 100 chars of description
                        desc = section.description[:100]
                        if len(section.description) > 100:
                            desc += "..."
                        print(f"   Description: {desc}")
                    print()

            print()

        # Summary
        print("="*70)
        print("TEST COMPLETE")
        print("="*70)
        print()
        print("Notes:")
        print("- High confidence (≥0.5): Strong match, likely relevant")
        print("- Medium confidence (0.3-0.5): Moderate match, possibly relevant")
        print("- Low confidence (0.15-0.3): Weak match, review carefully")
        print("- Very low confidence (<0.15): May not be relevant")
        print()
        print("💡 See MAPPING_STRATEGIES.md for enhancement options")

    finally:
        db.close()


if __name__ == "__main__":
    test_keyword_matching()
