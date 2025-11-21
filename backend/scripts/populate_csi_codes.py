#!/usr/bin/env python3
"""
Populate CSI MasterFormat Codes from Multiple Sources

Loads CSI MasterFormat codes from three sources:
1. Division codes (scraped from CSI widget) - 35 codes
2. Subdivision codes (scraped from CSI widget) - ~400 codes
3. Detail/leaf codes (GitHub outer-labs/masterformat-json 2016) - ~8,774 codes

Total: ~9,210 codes across all hierarchy levels

Sources:
- Scraped data: https://crmservice.csinet.org/widgets/masterformat/numbersandtitles.aspx
- GitHub data: https://github.com/outer-labs/masterformat-json (MIT License)
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import CSICode
from sqlalchemy.exc import IntegrityError


def load_codes_from_file(file_path):
    """
    Load codes from a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        list: List of (code, title) tuples
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    codes = []

    # Handle different JSON structures
    if isinstance(data, dict) and 'codes' in data:
        # Format: {"codes": [{"code": "...", "title": "...", ...}, ...]}
        for item in data['codes']:
            codes.append((item['code'], item['title']))
    elif isinstance(data, list):
        # Check if it's list of [code, title] pairs or list of objects
        if data and isinstance(data[0], list):
            # Format: [["code", "title"], ...] or [["code", "title", "part"], ...]
            # Some titles may be split across multiple elements due to commas
            for entry in data:
                if len(entry) >= 2:
                    code = entry[0]
                    # Join all remaining elements as the title
                    title = ''.join(entry[1:])  # Join without separator since commas are already included
                    codes.append((code, title))
        elif data and isinstance(data[0], dict):
            # Format: [{"code": "...", "title": "...", ...}, ...]
            codes = [(item['code'], item['title']) for item in data]

    return codes


def populate_database(dry_run=False):
    """
    Populate database with all CSI MasterFormat codes from three sources.

    Args:
        dry_run: If True, only preview without making changes
    """
    print("="*70)
    print("CSI MASTERFORMAT CODE POPULATION - ALL LEVELS")
    print("="*70)

    if dry_run:
        print("🔍 DRY RUN MODE - No database changes will be made")
    else:
        print("💾 LIVE MODE - Database will be populated")

    print()

    # Define source files
    files = [
        ("scripts/extracted_data/csi_masterformat_divisions.json", "Division codes (00 00 00, 03 00 00, ...)"),
        ("scripts/extracted_data/csi_masterformat_all.json", "Subdivision codes (03 30 00, 22 07 00, ...)"),
        ("scripts/extracted_data/masterformat-2016-list.json", "Detail codes (03 31 13, 22 07 19, ...) - 2016 Edition"),
    ]

    # Load all codes
    all_codes = []
    for file_path, description in files:
        if not os.path.exists(file_path):
            print(f"⚠️  Warning: {file_path} not found, skipping...")
            continue

        codes = load_codes_from_file(file_path)
        print(f"📄 {description}")
        print(f"   File: {file_path}")
        print(f"   Codes: {len(codes)}")
        all_codes.extend(codes)
        print()

    # Remove duplicates (keep first occurrence)
    seen_codes = set()
    unique_codes = []
    duplicates = 0

    for code, title in all_codes:
        if code not in seen_codes:
            seen_codes.add(code)
            unique_codes.append((code, title))
        else:
            duplicates += 1

    print(f"📊 Summary:")
    print(f"   Total codes loaded: {len(all_codes)}")
    print(f"   Duplicates removed: {duplicates}")
    print(f"   Unique codes to insert: {len(unique_codes)}")
    print()

    if dry_run:
        print("🔍 DRY RUN - Showing first 10 and last 5 codes:")
        for i, (code, title) in enumerate(unique_codes):
            if i < 10:
                print(f"   {code:10s} - {title}")
            elif i == 10:
                print(f"   ... ({len(unique_codes) - 15} more codes) ...")
            elif i >= len(unique_codes) - 5:
                print(f"   {code:10s} - {title}")
        print(f"\n💡 Run without --dry-run to populate database")
        return

    # Populate database
    print("="*70)
    print("POPULATING DATABASE")
    print("="*70)

    db = SessionLocal()
    inserted = 0
    skipped = 0
    failed = 0

    try:
        for i, (code, title) in enumerate(unique_codes, 1):
            # Extract division number
            division = int(code.split()[0]) if code and code.split() else 0

            # Create description
            description = f"CSI MasterFormat {code} - {title}"

            # Check if already exists
            existing = db.query(CSICode).filter(CSICode.code == code).first()
            if existing:
                skipped += 1
                continue

            # Insert code
            try:
                csi_code = CSICode(
                    code=code,
                    division=division,
                    title=title,
                    description=description
                )
                db.add(csi_code)
                db.commit()
                inserted += 1

                # Show progress every 1000 codes
                if inserted % 1000 == 0:
                    print(f"   Progress: {inserted:,} codes inserted...")

            except IntegrityError:
                db.rollback()
                skipped += 1
            except Exception as e:
                db.rollback()
                failed += 1
                if failed <= 5:  # Only show first 5 errors
                    print(f"   ❌ Failed to insert {code}: {e}")

        print(f"\n{'='*70}")
        print("POPULATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total codes processed: {len(unique_codes):,}")
        print(f"  ✅ Inserted: {inserted:,}")
        print(f"  ⏭️  Skipped (existing): {skipped:,}")
        print(f"  ❌ Failed: {failed:,}")
        print(f"{'='*70}")

        # Show division summary
        print(f"\n📊 Codes by Division:")
        divisions = {}
        for code, _ in unique_codes:
            div = int(code.split()[0]) if code and code.split() else 0
            divisions[div] = divisions.get(div, 0) + 1

        for div in sorted(divisions.keys())[:10]:  # Show first 10 divisions
            print(f"   Division {div:02d}: {divisions[div]:4,} codes")
        if len(divisions) > 10:
            print(f"   ... and {len(divisions) - 10} more divisions")

    finally:
        db.close()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Populate CSI MasterFormat codes from all three source files'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without making changes')

    args = parser.parse_args()
    populate_database(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
