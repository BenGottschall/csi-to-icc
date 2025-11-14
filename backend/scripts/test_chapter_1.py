"""
Extract All Sections from IPC 2018 Chapter 1
Logs each section to verify functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from datetime import datetime


def extract_all_sections_chapter_1():
    """Extract all sections from Chapter 1"""

    print("=" * 60)
    print("EXTRACT ALL SECTIONS - Chapter 1")
    print("=" * 60)

    # Setup Chrome browser
    print("\n1. Setting up browser...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Uncomment for headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    print("   ✓ Browser ready (VISIBLE mode)")

    # Open log file
    log_file_path = 'scripts/extraction_log.txt'
    log_file = open(log_file_path, 'w', encoding='utf-8')

    def log(message):
        """Write to both console and log file"""
        print(message)
        log_file.write(message + '\n')
        log_file.flush()

    log(f"\nExtraction started: {datetime.now()}")
    log("=" * 60)

    try:
        # Navigate to Chapter 1
        chapter_url = "https://codes.iccsafe.org/content/IPC2018P5/chapter-1-scope-and-administration"
        log(f"\n2. Navigating to Chapter 1...")
        log(f"   URL: {chapter_url}")

        driver.get(chapter_url)

        # Wait for page to load
        log("\n3. Waiting for content to load (10 seconds)...")
        time.sleep(10)
        log("   ✓ Page loaded")

        # Parse with BeautifulSoup
        log("\n4. Parsing HTML...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all section containers
        all_wrappers = soup.find_all('div', class_='section-action-wrapper')
        log(f"   Found {len(all_wrappers)} total wrappers")

        # Filter for actual sections
        section_wrappers = []
        for wrapper in all_wrappers:
            section_title = wrapper.get('data-section-title', '')
            # Must have brackets OR a decimal point
            if '[' in section_title or '.' in section_title:
                section_wrappers.append(wrapper)

        log(f"   Filtered to {len(section_wrappers)} actual sections")

        if len(section_wrappers) == 0:
            log("\n   ❌ ERROR: No sections found after filtering!")
            return None

        # Extract data from ALL sections
        log("\n5. Extracting data from all sections...")
        log("=" * 60)

        all_sections = []
        success_count = 0
        error_count = 0

        for i, section_wrapper in enumerate(section_wrappers, 1):
            log(f"\n[{i}/{len(section_wrappers)}] Processing section...")

            try:
                # Get data-section-title for reference
                data_title = section_wrapper.get('data-section-title', 'NO TITLE')
                log(f"   data-section-title: {data_title}")

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

                log(f"   Extracted: {section_number} - {title}")

                # Extract description (first paragraph with text-id)
                description = ""
                paragraphs = section_wrapper.find_all('p')
                for p in paragraphs:
                    if p.get('id') and 'text-id' in p.get('id'):
                        text = p.get_text(strip=True)
                        # Clean up spacing
                        text = ' '.join(text.split())
                        if text and len(text) > 10:  # Skip very short texts
                            description = text
                            break

                # Limit description length
                if len(description) > 500:
                    description = description[:500] + "..."

                if not description:
                    description = "(No description found)"

                log(f"   Description: {description[:80]}...")

                # Extract actual URL from heading id
                section_url = chapter_url  # Default fallback
                # Look for heading tags (h1-h6) with an id attribute
                for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    heading = section_wrapper.find(heading_tag, id=True)
                    if heading and heading.get('id'):
                        anchor_id = heading.get('id')
                        section_url = f"{chapter_url}#{anchor_id}"
                        log(f"   Found anchor: #{anchor_id}")
                        break

                # Build section data
                section_data = {
                    "section_number": section_number,
                    "title": title,
                    "description": description,
                    "url": section_url,
                    "chapter": "1"
                }

                all_sections.append(section_data)
                success_count += 1
                log(f"   ✓ Success")

            except Exception as e:
                error_count += 1
                log(f"   ❌ Error: {e}")
                continue

        # Summary
        log("\n" + "=" * 60)
        log("EXTRACTION COMPLETE")
        log("=" * 60)
        log(f"Total sections processed: {len(section_wrappers)}")
        log(f"Successfully extracted:   {success_count}")
        log(f"Errors:                   {error_count}")
        log(f"Extraction ended: {datetime.now()}")

        # Build final output in format expected by populate_icc_data.py
        output_data = {
            "code": "IPC",
            "year": 2018,
            "title": "2018 International Plumbing Code",
            "base_url": "https://codes.iccsafe.org/content/IPC2018P5",
            "chapters_scraped": 1,
            "total_sections": len(all_sections),
            "sections": all_sections
        }

        # Save to JSON
        output_file = 'scripts/ipc_chapter_1_extracted.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        log(f"\n✓ Data saved to: {output_file}")
        log(f"✓ Log saved to: {log_file_path}")

        # Print summary to console
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Sections extracted: {len(all_sections)}")
        print(f"Output file:        {output_file}")
        print(f"Log file:           {log_file_path}")
        print("\nFirst 3 sections:")
        for i, sec in enumerate(all_sections[:3], 1):
            print(f"  {i}. {sec['section_number']} - {sec['title']}")
        print("\nLast 3 sections:")
        for i, sec in enumerate(all_sections[-3:], len(all_sections) - 2):
            print(f"  {i}. {sec['section_number']} - {sec['title']}")
        print("=" * 60)

        return output_data

    except Exception as e:
        log(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        log(traceback.format_exc())
        return None

    finally:
        log_file.close()
        print("\nKeeping browser open for 3 seconds...")
        time.sleep(3)
        print("Closing browser...")
        driver.quit()
        print("Done!")


if __name__ == "__main__":
    print("\n📋 EXTRACT ALL SECTIONS FROM CHAPTER 1")
    print("This will extract all sections and log each one\n")

    result = extract_all_sections_chapter_1()

    print("\n" + "=" * 60)
    if result and result['total_sections'] > 0:
        print("✅ EXTRACTION SUCCESSFUL!")
        print("\nNext steps:")
        print("  1. Review: scripts/extraction_log.txt")
        print("  2. Test:   python scripts/populate_icc_data.py --file ipc_chapter_1_extracted.json --dry-run")
        print("  3. Insert: python scripts/populate_icc_data.py --file ipc_chapter_1_extracted.json")
    else:
        print("❌ EXTRACTION FAILED!")
        print("\nCheck scripts/extraction_log.txt for details")
    print("=" * 60)
