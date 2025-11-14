"""
Populate Database with All IPC 2018 Chapters
Reads JSON files from extracted_data/ipc_2018/ and populates database
"""
import os
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import ICCDocument, ICCSection
from sqlalchemy.exc import IntegrityError


class BulkChapterPopulator:
    """Populate database with multiple IPC chapters"""

    def __init__(self, data_dir='scripts/extracted_data/ipc_2018', dry_run=False):
        self.data_dir = data_dir
        self.dry_run = dry_run
        self.db = None if dry_run else SessionLocal()

    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()

    def load_chapter_files(self):
        """Find all chapter JSON files"""
        print(f"Looking for chapter files in: {self.data_dir}")

        chapter_files = []
        for filename in sorted(os.listdir(self.data_dir)):
            if filename.startswith('chapter_') and filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                chapter_files.append(filepath)

        print(f"✓ Found {len(chapter_files)} chapter files")
        return chapter_files

    def create_or_get_document(self):
        """Create or retrieve the IPC 2018 document record"""
        if self.dry_run:
            print("\n[DRY RUN] Would create ICC Document: IPC 2018")
            return None

        # Check if document already exists
        document = self.db.query(ICCDocument).filter_by(code="IPC", year=2018).first()

        if document:
            print(f"\n✓ Found existing ICC Document: IPC 2018 (ID: {document.id})")
            return document

        # Create new document
        document = ICCDocument(
            code="IPC",
            year=2018,
            title="2018 International Plumbing Code",
            state=None,
            base_url="https://codes.iccsafe.org/content/IPC2018P5"
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        print(f"\n✓ Created ICC Document: IPC 2018 (ID: {document.id})")
        return document

    def populate_chapter(self, filepath, document_id):
        """Populate sections from a single chapter file"""
        print(f"\nProcessing: {os.path.basename(filepath)}")

        # Load chapter data
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        chapter_num = data.get('chapter_number', 'unknown')
        sections = data.get('sections', [])

        print(f"  Chapter {chapter_num}: {len(sections)} sections")

        if self.dry_run:
            print(f"  [DRY RUN] Would insert {len(sections)} sections")
            # Show a few examples
            for i, section in enumerate(sections[:3], 1):
                print(f"    {i}. {section['section_number']} - {section['title']}")
            if len(sections) > 3:
                print(f"    ... and {len(sections) - 3} more")
            return {
                'chapter': chapter_num,
                'total': len(sections),
                'inserted': 0,
                'skipped': 0,
                'failed': 0
            }

        # Insert sections
        inserted = 0
        skipped = 0
        failed = 0

        for section_data in sections:
            try:
                # Check if section already exists
                existing = self.db.query(ICCSection).filter_by(
                    document_id=document_id,
                    section_number=section_data['section_number']
                ).first()

                if existing:
                    skipped += 1
                    continue

                # Create new section
                section = ICCSection(
                    document_id=document_id,
                    section_number=section_data['section_number'],
                    title=section_data['title'],
                    chapter=int(section_data['chapter']),
                    url=section_data['url'],
                    description=section_data.get('description', '')
                )

                self.db.add(section)
                inserted += 1

                # Commit every 50 sections for progress
                if inserted % 50 == 0:
                    self.db.commit()
                    print(f"    Progress: {inserted} sections inserted...")

            except Exception as e:
                failed += 1
                print(f"    ❌ Error inserting section {section_data.get('section_number')}: {e}")
                continue

        # Final commit
        if inserted > 0:
            try:
                self.db.commit()
            except Exception as e:
                print(f"    ❌ Error committing: {e}")
                self.db.rollback()

        print(f"  ✓ Inserted: {inserted}, Skipped: {skipped}, Failed: {failed}")

        return {
            'chapter': chapter_num,
            'total': len(sections),
            'inserted': inserted,
            'skipped': skipped,
            'failed': failed
        }

    def populate_all(self):
        """Populate all chapters"""
        print("\n" + "=" * 70)
        print("IPC 2018 BULK CHAPTER POPULATION")
        print("=" * 70)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No database changes will be made")
        else:
            print("💾 LIVE MODE - Database will be populated")

        print()

        # Load chapter files
        chapter_files = self.load_chapter_files()

        if not chapter_files:
            print("❌ No chapter files found!")
            return False

        # Create or get ICC document
        document = self.create_or_get_document()
        document_id = document.id if document else 1  # Use 1 for dry run

        # Process each chapter
        print("\n" + "=" * 70)
        print("POPULATING SECTIONS")
        print("=" * 70)

        results = []
        for i, filepath in enumerate(chapter_files, 1):
            print(f"\n[{i}/{len(chapter_files)}]", end=" ")
            result = self.populate_chapter(filepath, document_id)
            results.append(result)

        # Summary
        print("\n" + "=" * 70)
        print("POPULATION COMPLETE")
        print("=" * 70)

        total_sections = sum(r['total'] for r in results)
        total_inserted = sum(r['inserted'] for r in results)
        total_skipped = sum(r['skipped'] for r in results)
        total_failed = sum(r['failed'] for r in results)

        print(f"\nChapters processed:    {len(results)}")
        print(f"Total sections:        {total_sections}")
        if not self.dry_run:
            print(f"  Inserted:            {total_inserted}")
            print(f"  Skipped (existing):  {total_skipped}")
            print(f"  Failed:              {total_failed}")

        if self.dry_run:
            print("\n💡 This was a DRY RUN. Run without --dry-run to populate database.")
        else:
            print("\n✅ Database population complete!")

        print("=" * 70)

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Populate database with IPC 2018 chapters')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--data-dir', type=str, default='scripts/extracted_data/ipc_2018',
                        help='Directory containing chapter JSON files')

    args = parser.parse_args()

    populator = BulkChapterPopulator(data_dir=args.data_dir, dry_run=args.dry_run)

    try:
        success = populator.populate_all()
        return 0 if success else 1
    finally:
        populator.close()


if __name__ == "__main__":
    exit(main())
