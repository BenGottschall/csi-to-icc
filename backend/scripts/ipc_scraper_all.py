"""
IPC 2018 Multi-Chapter Scraper
Extracts sections from all IPC 2018 chapters (except Chapter 2 - Definitions)
Saves each chapter to its own JSON file with detailed logging
"""
import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class IPCMultiChapterScraper:
    """Scraper for extracting multiple IPC 2018 chapters"""

    def __init__(self, output_dir='scripts/extracted_data/ipc_2018', headless=True):
        self.output_dir = output_dir
        self.logs_dir = os.path.join(output_dir, 'logs')
        self.headless = headless
        self.driver = None

        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("Setting up Chrome WebDriver...")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        print("✓ WebDriver ready")

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def load_chapter_links(self, filepath='scripts/chapter_links.txt'):
        """Load chapter URLs from file"""
        print(f"\nLoading chapter links from: {filepath}")

        with open(filepath, 'r') as f:
            lines = f.readlines()

        chapters = []
        for line in lines:
            line = line.strip()
            if line and line.startswith('http'):
                # Extract chapter number from URL
                # e.g., "chapter-1-scope" -> "1"
                parts = line.split('/')[-1].split('-')
                chapter_num = parts[1] if len(parts) > 1 else "unknown"

                chapters.append({
                    'number': chapter_num,
                    'url': line
                })

        print(f"✓ Found {len(chapters)} chapters")
        return chapters

    def extract_chapter(self, chapter_num, chapter_url):
        """Extract sections from a single chapter"""

        # Setup logging for this chapter
        log_file_path = os.path.join(self.logs_dir, f'chapter_{chapter_num:02d}.log')
        log_file = open(log_file_path, 'w', encoding='utf-8')

        def log(message):
            """Write to both console and log file"""
            print(message)
            log_file.write(message + '\n')
            log_file.flush()

        log("=" * 70)
        log(f"EXTRACTING CHAPTER {chapter_num}")
        log("=" * 70)
        log(f"Started: {datetime.now()}")
        log(f"URL: {chapter_url}")

        try:
            # Navigate to chapter
            log("\nNavigating to chapter...")
            self.driver.get(chapter_url)

            # Wait for page to load
            log("Waiting for content to load (10 seconds)...")
            time.sleep(10)
            log("✓ Page loaded")

            # Parse with BeautifulSoup
            log("\nParsing HTML...")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find all section containers
            all_wrappers = soup.find_all('div', class_='section-action-wrapper')
            log(f"Found {len(all_wrappers)} total wrappers")

            # Filter for actual sections (must have brackets OR decimal point)
            section_wrappers = []
            for wrapper in all_wrappers:
                section_title = wrapper.get('data-section-title', '')
                if '[' in section_title or '.' in section_title:
                    section_wrappers.append(wrapper)

            log(f"Filtered to {len(section_wrappers)} actual sections")

            if len(section_wrappers) == 0:
                log("\n❌ ERROR: No sections found!")
                log_file.close()
                return None

            # Extract data from all sections
            log("\nExtracting section data...")
            log("-" * 70)

            all_sections = []
            success_count = 0
            error_count = 0

            for i, section_wrapper in enumerate(section_wrappers, 1):
                if i % 10 == 0:  # Log progress every 10 sections
                    log(f"\nProgress: {i}/{len(section_wrappers)} sections...")

                try:
                    # Extract section number
                    section_num_elem = section_wrapper.find('span', class_='section_number')
                    section_number = section_num_elem.get_text(strip=True) if section_num_elem else "UNKNOWN"

                    # Extract title - try all possible title levels
                    title = "UNKNOWN"
                    for level_class in ['level2_title', 'level3_title', 'level4_title', 'level5_title']:
                        title_elem = section_wrapper.find('span', class_=level_class)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break

                    # Extract description (first paragraph with text-id)
                    description = ""
                    paragraphs = section_wrapper.find_all('p')
                    for p in paragraphs:
                        if p.get('id') and 'text-id' in p.get('id'):
                            text = p.get_text(strip=True)
                            text = ' '.join(text.split())  # Clean up spacing
                            if text and len(text) > 10:
                                description = text
                                break

                    # Limit description length
                    if len(description) > 500:
                        description = description[:500] + "..."

                    if not description:
                        description = "(No description found)"

                    # Extract actual URL from heading id
                    section_url = chapter_url  # Default fallback
                    for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        heading = section_wrapper.find(heading_tag, id=True)
                        if heading and heading.get('id'):
                            anchor_id = heading.get('id')
                            section_url = f"{chapter_url}#{anchor_id}"
                            break

                    # Build section data
                    section_data = {
                        "section_number": section_number,
                        "title": title,
                        "description": description,
                        "url": section_url,
                        "chapter": str(chapter_num)
                    }

                    all_sections.append(section_data)
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    log(f"\n❌ Error on section {i}: {e}")
                    continue

            # Summary
            log("\n" + "=" * 70)
            log("EXTRACTION COMPLETE")
            log("=" * 70)
            log(f"Total sections found:     {len(section_wrappers)}")
            log(f"Successfully extracted:   {success_count}")
            log(f"Errors:                   {error_count}")
            log(f"Completed: {datetime.now()}")

            log_file.close()
            return all_sections

        except Exception as e:
            log(f"\n❌ FATAL ERROR: {e}")
            import traceback
            log(traceback.format_exc())
            log_file.close()
            return None

    def save_chapter(self, chapter_num, sections, chapter_url):
        """Save chapter data to JSON file"""
        output_file = os.path.join(self.output_dir, f'chapter_{chapter_num:02d}.json')

        data = {
            "code": "IPC",
            "year": 2018,
            "title": f"2018 International Plumbing Code - Chapter {chapter_num}",
            "base_url": "https://codes.iccsafe.org/content/IPC2018P5",
            "chapter_url": chapter_url,
            "chapter_number": chapter_num,
            "total_sections": len(sections),
            "sections": sections
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved to: {output_file}")
        return output_file

    def create_index(self, chapter_results):
        """Create index file with metadata"""
        index_file = os.path.join(self.output_dir, 'index.json')

        index_data = {
            "code": "IPC",
            "year": 2018,
            "title": "2018 International Plumbing Code",
            "base_url": "https://codes.iccsafe.org/content/IPC2018P5",
            "extracted_date": datetime.now().isoformat(),
            "total_chapters": len(chapter_results),
            "total_sections": sum(r['sections'] for r in chapter_results),
            "chapters": chapter_results
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Index saved to: {index_file}")

    def scrape_all(self, skip_chapters=None, only_chapters=None):
        """
        Scrape all chapters

        Args:
            skip_chapters: List of chapter numbers to skip (e.g., [2])
            only_chapters: Only scrape these chapter numbers (for testing)
        """
        if skip_chapters is None:
            skip_chapters = [2]  # Skip definitions by default

        print("\n" + "=" * 70)
        print("IPC 2018 MULTI-CHAPTER SCRAPER")
        print("=" * 70)
        print(f"Output directory: {self.output_dir}")
        print(f"Skipping chapters: {skip_chapters}")
        if only_chapters:
            print(f"Only scraping: {only_chapters}")
        print()

        # Load chapter links
        chapters = self.load_chapter_links()

        # Filter chapters
        chapters_to_scrape = []
        for ch in chapters:
            ch_num = int(ch['number'])
            if ch_num in skip_chapters:
                print(f"⏭️  Skipping Chapter {ch_num} (excluded)")
                continue
            if only_chapters and ch_num not in only_chapters:
                continue
            chapters_to_scrape.append(ch)

        print(f"\n📋 Will scrape {len(chapters_to_scrape)} chapters")
        print("=" * 70)

        # Setup driver
        self.setup_driver()

        # Track results
        chapter_results = []
        start_time = time.time()

        try:
            for i, chapter in enumerate(chapters_to_scrape, 1):
                ch_num = int(chapter['number'])
                ch_url = chapter['url']

                print(f"\n{'='*70}")
                print(f"[{i}/{len(chapters_to_scrape)}] CHAPTER {ch_num}")
                print(f"{'='*70}")

                # Extract sections
                sections = self.extract_chapter(ch_num, ch_url)

                if sections:
                    # Save chapter file
                    output_file = self.save_chapter(ch_num, sections, ch_url)

                    chapter_results.append({
                        "chapter": ch_num,
                        "sections": len(sections),
                        "file": output_file,
                        "status": "success"
                    })

                    print(f"✅ Chapter {ch_num}: {len(sections)} sections extracted")
                else:
                    chapter_results.append({
                        "chapter": ch_num,
                        "sections": 0,
                        "file": None,
                        "status": "failed"
                    })
                    print(f"❌ Chapter {ch_num}: Extraction failed")

                # Estimate time remaining
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(chapters_to_scrape) - i) * avg_time
                print(f"⏱️  Estimated time remaining: {int(remaining/60)} min {int(remaining%60)} sec")

            # Create index
            print("\n" + "=" * 70)
            print("CREATING INDEX...")
            print("=" * 70)
            self.create_index(chapter_results)

            # Final summary
            print("\n" + "=" * 70)
            print("SCRAPING COMPLETE!")
            print("=" * 70)

            total_sections = sum(r['sections'] for r in chapter_results)
            successful = sum(1 for r in chapter_results if r['status'] == 'success')
            failed = sum(1 for r in chapter_results if r['status'] == 'failed')

            print(f"Chapters processed:    {len(chapter_results)}")
            print(f"  Successful:          {successful}")
            print(f"  Failed:              {failed}")
            print(f"Total sections:        {total_sections}")
            print(f"Total time:            {int((time.time() - start_time)/60)} min")
            print(f"\nOutput directory:      {self.output_dir}")
            print("=" * 70)

            return chapter_results

        finally:
            self.close_driver()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape IPC 2018 chapters')
    parser.add_argument('--test', action='store_true', help='Test mode: only scrape chapters 1 and 3')
    parser.add_argument('--chapters', type=str, help='Comma-separated chapter numbers to scrape (e.g., "1,3,4")')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    parser.add_argument('--visible', action='store_true', help='Run with visible browser (opposite of headless)')

    args = parser.parse_args()

    # Determine headless mode
    headless = args.headless and not args.visible

    # Determine which chapters to scrape
    only_chapters = None
    if args.test:
        only_chapters = [1, 3]
        print("🧪 TEST MODE: Only scraping chapters 1 and 3")
    elif args.chapters:
        only_chapters = [int(c.strip()) for c in args.chapters.split(',')]
        print(f"📋 Custom mode: Scraping chapters {only_chapters}")

    # Create scraper and run
    scraper = IPCMultiChapterScraper(headless=headless)
    results = scraper.scrape_all(skip_chapters=[2], only_chapters=only_chapters)

    # Return appropriate exit code
    if results and all(r['status'] == 'success' for r in results):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
