#!/usr/bin/env python3
"""
CSI MasterFormat Code Scraper (Recursive)

Scrapes ALL CSI MasterFormat codes from the official CSI widget, including:
- Division level (e.g., 22 00 00 - Plumbing)
- Subdivision level (e.g., 22 07 00 - Plumbing Insulation)
- Detail level (e.g., 22 07 19 - Plumbing Piping Insulation)

Source: https://crmservice.csinet.org/widgets/masterformat/numbersandtitles.aspx
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin


BASE_URL = "https://crmservice.csinet.org/widgets/masterformat/"
MAIN_URL = "https://crmservice.csinet.org/widgets/masterformat/numbersandtitles.aspx"


def scrape_page(url):
    """
    Scrape codes and links from a single page.

    Args:
        url: URL to scrape

    Returns:
        list: List of (code, title, href) tuples
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'tblNumbersAndTitles'})

    if not table:
        return []

    rows = table.find_all('tr', {'class': 'numbersandtitles'})
    results = []

    for row in rows:
        left_col = row.find('td', {'class': 'left-column'})
        right_col = row.find('td', {'class': 'right-column'})

        if left_col and right_col:
            # Get code and title
            code_link = left_col.find('a')
            title_link = right_col.find('a')

            if code_link and title_link:
                code = code_link.get_text(strip=True)
                title = title_link.get_text(strip=True)
                href = code_link.get('href')

                # Convert relative URL to absolute
                if href:
                    href = urljoin(BASE_URL, href)

                results.append((code, title, href))

    return results


def scrape_all_codes():
    """
    Recursively scrape all CSI MasterFormat codes.

    Returns:
        list: List of dictionaries with code, title, division, description
    """
    print("="*70)
    print("CSI MASTERFORMAT RECURSIVE SCRAPER")
    print("="*70)
    print(f"Starting from: {MAIN_URL}\n")

    all_codes = []
    visited_urls = set()
    urls_to_visit = [MAIN_URL]

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)

        # Skip if already visited
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        print(f"📄 Scraping: {current_url}")

        try:
            # Scrape the current page
            page_codes = scrape_page(current_url)

            for code, title, href in page_codes:
                # Extract division number
                division = int(code.split()[0]) if code else 0

                # Check if this is a leaf node (no href or already detailed code)
                # Leaf nodes are codes like "22 07 19" (5 digits without trailing 00s)
                code_parts = code.split()
                is_leaf = (len(code_parts) == 3 and
                          not (code_parts[1] == '00' and code_parts[2] == '00'))

                # Add to results
                code_data = {
                    "code": code,
                    "title": title,
                    "division": division,
                    "description": f"{code} - {title}"
                }
                all_codes.append(code_data)
                print(f"  ✓ {code:10s} - {title}")

                # Add child URL to visit queue if not a leaf node
                if href and not is_leaf and href not in visited_urls:
                    urls_to_visit.append(href)

            print(f"  Found {len(page_codes)} codes on this page")
            print()

            # Be polite - small delay between requests
            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Error scraping {current_url}: {e}")
            continue

    print(f"\n{'='*70}")
    print(f"✅ Scraping complete!")
    print(f"   Total pages visited: {len(visited_urls)}")
    print(f"   Total codes scraped: {len(all_codes)}")
    print(f"{'='*70}\n")

    return all_codes


def save_to_json(csi_codes, output_dir="scripts/extracted_data"):
    """
    Save scraped CSI codes to JSON file.

    Args:
        csi_codes: List of CSI code dictionaries
        output_dir: Directory to save the JSON file
    """
    os.makedirs(output_dir, exist_ok=True)

    output_data = {
        "source": MAIN_URL,
        "scraped_at": datetime.now().isoformat(),
        "total_codes": len(csi_codes),
        "codes": csi_codes
    }

    output_file = os.path.join(output_dir, "csi_masterformat_all.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {len(csi_codes)} CSI codes to: {output_file}")

    return output_file


def main():
    """Main function to run the scraper."""
    try:
        # Scrape all CSI codes recursively
        csi_codes = scrape_all_codes()

        if not csi_codes:
            print("❌ No CSI codes were scraped")
            return

        # Save to JSON
        output_file = save_to_json(csi_codes)

        # Print division summary
        divisions = {}
        for code_data in csi_codes:
            div = code_data['division']
            divisions[div] = divisions.get(div, 0) + 1

        print(f"\n📊 Summary by Division:")
        for div in sorted(divisions.keys()):
            print(f"   Division {div:02d}: {divisions[div]:4d} codes")

        print(f"\n💡 Next step: Run populate_csi_data.py to load into database")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
