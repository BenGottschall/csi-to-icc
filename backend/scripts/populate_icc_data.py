"""
Populate Database with ICC Scraped Data
Reads JSON from icc_scraper.py and inserts into the database
"""
import json
import sys
import os

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import ICCDocument, ICCSection


def load_json_data(filename="ipc_2018_scraped.json"):
    """Load scraped JSON data"""
    filepath = os.path.join("scripts", filename)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        print("Run icc_scraper.py first to generate the JSON file.")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded data: {data['code']} {data['year']}")
    print(f"  - {data['chapters_scraped']} chapters")
    print(f"  - {data['total_sections']} sections")

    return data


def create_icc_document(db, data):
    """Create ICC document record"""
    # Check if document already exists
    existing = db.query(ICCDocument).filter(
        ICCDocument.code == data['code'],
        ICCDocument.year == data['year'],
        ICCDocument.state == None
    ).first()

    if existing:
        print(f"\nICC Document already exists (ID: {existing.id})")
        return existing

    # Create new document
    document = ICCDocument(
        code=data['code'],
        year=data['year'],
        title=data['title'],
        state=None,  # Model code, not state-specific
        base_url=data['base_url']
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    print(f"\n✓ Created ICC Document: {document.code} {document.year} (ID: {document.id})")
    return document


def create_sections(db, document, sections):
    """Create ICC section records"""
    print(f"\nInserting {len(sections)} sections...")

    created_count = 0
    skipped_count = 0

    for section_data in sections:
        # Check if section already exists
        existing = db.query(ICCSection).filter(
            ICCSection.document_id == document.id,
            ICCSection.section_number == section_data['section_number']
        ).first()

        if existing:
            skipped_count += 1
            continue

        # Create section
        section = ICCSection(
            document_id=document.id,
            section_number=section_data['section_number'],
            title=section_data['title'],
            chapter=int(section_data['chapter']) if section_data['chapter'].isdigit() else None,
            url=section_data['url'],
            description=section_data['description']
        )

        db.add(section)
        created_count += 1

        # Commit in batches to avoid memory issues
        if created_count % 50 == 0:
            db.commit()
            print(f"  Inserted {created_count} sections...")

    # Final commit
    db.commit()

    print(f"\n✓ Created {created_count} new sections")
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} existing sections")

    return created_count


def populate_database(filename="ipc_2018_scraped.json", dry_run=False):
    """Main function to populate database"""
    print("=" * 60)
    print("ICC Data Population Script")
    print("=" * 60)

    # Load JSON data
    data = load_json_data(filename)
    if not data:
        return False

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made to database")
        print(f"\nWould create:")
        print(f"  - 1 ICC Document: {data['code']} {data['year']}")
        print(f"  - {len(data['sections'])} ICC Sections")
        return True

    # Connect to database
    print("\nConnecting to database...")
    db = SessionLocal()

    try:
        # Create document
        document = create_icc_document(db, data)

        # Create sections
        created = create_sections(db, document, data['sections'])

        print("\n" + "=" * 60)
        print("✓ Database population complete!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - ICC Document ID: {document.id}")
        print(f"  - Sections inserted: {created}")
        print(f"\nYou can now search for ICC sections in the web app!")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Populate database with ICC scraped data')
    parser.add_argument('--file', default='ipc_2018_scraped.json',
                        help='JSON file to load (default: ipc_2018_scraped.json)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')

    args = parser.parse_args()

    success = populate_database(args.file, dry_run=args.dry_run)

    if success:
        print("\n✓ Success!")
        sys.exit(0)
    else:
        print("\n✗ Failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
