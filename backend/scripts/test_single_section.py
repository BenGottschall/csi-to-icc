"""
Minimal Test: Extract a Single Section from IPC 2018 Chapter 1
Goal: Prove the concept works before building the full scraper
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json


def test_single_section():
    """Extract just section 101.1 from Chapter 1"""

    print("=" * 60)
    print("TEST: Extract Single Section (101.1)")
    print("=" * 60)

    # Setup Chrome browser
    print("\n1. Setting up browser...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Disabled - show browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    print("   ✓ Browser ready (VISIBLE mode - you'll see the window)")

    try:
        # Navigate to Chapter 1
        chapter_url = "https://codes.iccsafe.org/content/IPC2018P5/chapter-1-scope-and-administration"
        print(f"\n2. Navigating to Chapter 1...")
        print(f"   URL: {chapter_url}")

        driver.get(chapter_url)

        # Wait for page to load and sections to appear
        print("\n3. Waiting for content to load (10 seconds)...")
        time.sleep(10)  # Simple wait - can be improved with WebDriverWait

        print("   ✓ Page loaded")

        # Parse with BeautifulSoup
        print("\n4. Parsing HTML...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all section containers
        all_wrappers = soup.find_all('div', class_='section-action-wrapper')
        print(f"   Found {len(all_wrappers)} total wrappers")

        # Filter for actual sections (skip chapter headers)
        # Real sections have data-section-title like "[A] 101.1 Title." (with brackets AND decimal)
        # Chapter headers are like "CHAPTER 1 SCOPE AND ADMINISTRATION" (no brackets, no decimal)
        section_wrappers = []
        for wrapper in all_wrappers:
            section_title = wrapper.get('data-section-title', '')
            # Must have brackets OR a decimal point (like 101.1, 102.2, etc.)
            if '[' in section_title or '.' in section_title:
                section_wrappers.append(wrapper)

        print(f"   Filtered to {len(section_wrappers)} actual sections (skipped chapter headers)")

        if len(section_wrappers) == 0:
            print("\n   ❌ ERROR: No sections found after filtering!")
            print("   Saving HTML for debugging...")
            with open('scripts/debug_no_sections.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   Saved to: scripts/debug_no_sections.html")

            # Show what we DID find
            print("\n   First 3 wrapper titles we found:")
            for i, w in enumerate(all_wrappers[:3], 1):
                title = w.get('data-section-title', 'NO TITLE')
                print(f"      {i}. {title}")

            return None

        # Get the FIRST actual section (should be 101.1)
        print("\n5. Extracting data from first section...")
        first_section = section_wrappers[0]

        # DEBUG: Save the HTML of just this section
        print("\n   DEBUG: First section HTML snippet:")
        section_html = str(first_section)[:500]  # First 500 chars
        print(f"   {section_html}...")

        # DEBUG: Check what the data-section-title says
        data_title = first_section.get('data-section-title', 'NO ATTRIBUTE')
        print(f"\n   data-section-title attribute: {data_title}")

        # Extract section number
        section_num_elem = first_section.find('span', class_='section_number')
        print(f"\n   Looking for: <span class='section_number'>")
        print(f"   Found element: {section_num_elem}")
        section_number = section_num_elem.get_text(strip=True) if section_num_elem else "NOT FOUND"
        print(f"   Section number: {section_number}")

        # Extract title
        title_elem = first_section.find('span', class_='level2_title')
        print(f"\n   Looking for: <span class='level2_title'>")
        print(f"   Found element: {title_elem}")
        title = title_elem.get_text(strip=True) if title_elem else "NOT FOUND"
        print(f"   Title: {title}")

        # DEBUG: Show all spans in this section
        all_spans = first_section.find_all('span')
        print(f"\n   Total spans found in section: {len(all_spans)}")
        print("   First 5 spans:")
        for i, span in enumerate(all_spans[:5], 1):
            classes = span.get('class', [])
            text = span.get_text(strip=True)[:50]
            print(f"      {i}. class={classes} text='{text}'")

        # Extract description (first paragraph)
        paragraphs = first_section.find_all('p')
        print(f"\n   Found {len(paragraphs)} paragraphs")
        print("   First 3 paragraphs:")
        for i, p in enumerate(paragraphs[:3], 1):
            p_id = p.get('id', 'NO ID')
            text = p.get_text(strip=True)[:60]
            print(f"      {i}. id='{p_id}' text='{text}...'")

        description = ""
        for p in paragraphs:
            # Skip paragraphs that are part of buttons/actions
            if p.get('id') and 'text-id' in p.get('id'):
                text = p.get_text(strip=True)
                if text:
                    description = text
                    print(f"\n   Using description from paragraph: {p.get('id')}")
                    break

        # Construct URL
        section_url = f"{chapter_url}#IPC2018P5_Ch01_SubCh01_Sec{section_number.strip()}"

        # Build result
        result = {
            "section_number": section_number,
            "title": title,
            "description": description[:200] if description else "NOT FOUND",  # Limit length
            "url": section_url,
            "chapter": "1"
        }

        # Display result
        print("\n" + "=" * 60)
        print("EXTRACTED DATA:")
        print("=" * 60)
        print(f"Section Number: {result['section_number']}")
        print(f"Title:          {result['title']}")
        print(f"Description:    {result['description']}")
        print(f"URL:            {result['url']}")
        print(f"Chapter:        {result['chapter']}")
        print("=" * 60)

        # Save to JSON
        output_file = 'scripts/test_single_section.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved to: {output_file}")

        return result

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Save HTML for debugging
        try:
            with open('scripts/debug_error.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   Saved debug HTML to: scripts/debug_error.html")
        except:
            pass

        return None

    finally:
        print("\nKeeping browser open for 5 seconds so you can see it...")
        time.sleep(5)
        print("Closing browser...")
        driver.quit()
        print("Done!")


if __name__ == "__main__":
    print("\n🔬 MINIMAL TEST: Single Section Extraction")
    print("This will extract ONLY section 101.1 from Chapter 1\n")

    result = test_single_section()

    print("\n" + "=" * 60)
    if result and result['section_number'] != "NOT FOUND":
        print("✅ TEST PASSED!")
        print("\nNext step: Expand to extract all sections from Chapter 1")
    else:
        print("❌ TEST FAILED!")
        print("\nCheck debug files in scripts/ folder")
    print("=" * 60)
