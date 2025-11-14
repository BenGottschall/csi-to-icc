# ICC Scraper Design Document

## Overview
Simple, no-authentication scraper for ICC 2018 IPC code sections.

**Key Insight:** No login required - all content is publicly viewable!

---

## HTML Structure (Based on Analysis)

### Section Container
```html
<div class="section-action-wrapper"
     data-section-title="[A] 101.1 Title."
     data-chapter-title="CHAPTER 1 SCOPE AND ADMINISTRATION">
```

### Section Number & Title
```html
<h1 id="text-id-24698365">
  <span class="section_number"> 101.1 </span>
  <span class="level2_title">Title.</span>
</h1>
```

### Section Content
```html
<p id="text-id-24698365-0" section-number="24698365">
  These regulations shall be known as the Plumbing Code...
</p>
```

### URL Pattern
```
https://codes.iccsafe.org/content/IPC2018P5/chapter-1-scope-and-administration#IPC2018P5_Ch01_SubCh01_Sec101.1
```

---

## Scraper Requirements Checklist

### Core Functionality
- [ ] Navigate to chapter URL (no login)
- [ ] Wait for JavaScript to render content (3-5 seconds)
- [ ] Find all section containers (`.section-action-wrapper`)
- [ ] Extract section data for each section
- [ ] Save to JSON in correct format
- [ ] Handle errors gracefully

### Data Extraction Per Section
- [ ] Section number (from `.section_number` span)
- [ ] Section title (from `.level2_title` span)
- [ ] Section description (from `<p>` tags)
- [ ] Construct proper section URL
- [ ] Store chapter number

### Technical Requirements
- [ ] Use Selenium with Chrome/Chromium
- [ ] Headless mode option (with flag)
- [ ] Debug mode option (save HTML, screenshots)
- [ ] Progress indicators (which chapter, how many sections found)
- [ ] Configurable wait times for page load

### Output Format
Must match `populate_icc_data.py` expectations:
```json
{
  "code": "IPC",
  "year": 2018,
  "title": "2018 International Plumbing Code",
  "base_url": "https://codes.iccsafe.org/content/IPC2018P5",
  "chapters_scraped": 1,
  "total_sections": 45,
  "sections": [
    {
      "section_number": "101.1",
      "title": "Title.",
      "description": "These regulations shall be known as...",
      "url": "https://codes.iccsafe.org/...",
      "chapter": "1"
    }
  ]
}
```

---

## Scraper Architecture

### Main Components

**1. ICCScraperSimple Class**
```python
class ICCScraperSimple:
    def __init__(self, headless=True, debug=False):
        # Initialize settings

    def setup_driver(self):
        # Setup Chrome/Chromium with Selenium

    def scrape_chapter(self, chapter_num):
        # Scrape a single chapter
        # Returns: list of section dicts

    def scrape_all_chapters(self, start=1, end=13):
        # Scrape multiple chapters
        # Returns: complete data dict

    def save_to_json(self, data, filename):
        # Save scraped data to JSON

    def close(self):
        # Clean up browser
```

**2. Helper Methods**
```python
def construct_chapter_url(chapter_num):
    # Build chapter URL
    # Example: chapter 1 = .../chapter-1-scope-and-administration
    # Note: Chapter 1 has special slug, others are just "chapter-N"

def construct_section_url(base_url, chapter_num, section_num):
    # Build section URL from components
    # Format: #IPC2018P5_Ch01_SubCh01_Sec101.1

def extract_section_data(section_element, chapter_num):
    # Extract all data from a section element
    # Returns: dict with section_number, title, description, url, chapter

def clean_text(text):
    # Remove extra whitespace, clean up text
```

---

## BeautifulSoup Selectors

### Primary Strategy
```python
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all section containers
sections = soup.find_all('div', class_='section-action-wrapper')

for section in sections:
    # Get section number
    section_num = section.find('span', class_='section_number')

    # Get title
    title = section.find('span', class_='level2_title')

    # Get description (all <p> tags in this section)
    paragraphs = section.find_all('p')
```

### Fallback Strategy
If primary fails:
```python
# Use data attributes
section_title = section.get('data-section-title')
# Parse "[A] 101.1 Title." to extract parts
```

---

## Error Handling

### Must Handle
- **Page load timeout** - Retry with longer wait
- **No sections found** - Save HTML for debugging
- **Missing section data** - Log warning, continue to next section
- **ChromeDriver errors** - Clear message with fix instructions
- **Network errors** - Retry mechanism

### Debug Mode
When `--debug` flag is set:
- Save HTML for each chapter: `chapter_N.html`
- Save screenshots: `chapter_N_screenshot.png`
- Print verbose logging
- Show sample sections found

---

## Command Line Interface

```bash
# Test with one chapter
python scripts/icc_scraper_simple.py --chapters 1 --debug

# Scrape specific range
python scripts/icc_scraper_simple.py --start 1 --end 3

# Scrape all 13 chapters
python scripts/icc_scraper_simple.py --all

# Custom output file
python scripts/icc_scraper_simple.py --chapters 2 --output test.json

# Headless mode
python scripts/icc_scraper_simple.py --chapters 1 --headless

# Visible browser (for debugging)
python scripts/icc_scraper_simple.py --chapters 1 --no-headless --debug
```

---

## Testing Strategy

### Phase 1: Single Section Test
Create `test_scraper_single.py`:
- Load Chapter 1
- Find just one section (101.1)
- Print extracted data
- Verify it matches expected format

### Phase 2: Single Chapter Test
Create `test_scraper_chapter.py`:
- Load Chapter 1
- Extract all sections
- Save to `test_chapter_1.json`
- Validate with `populate_icc_data.py --dry-run`

### Phase 3: Full Scrape
- Run on all 13 chapters
- Monitor for errors
- Verify section counts make sense

---

## Known Challenges & Solutions

### Challenge: Chapter URL Variations
**Problem:** Chapter 1 URL is different from others
- Chapter 1: `.../chapter-1-scope-and-administration`
- Chapter 2: `.../chapter-2-definitions`
- Chapter 3: `.../chapter-3-general-regulations`

**Solution:** Map chapter numbers to slugs, or try constructing URL and handle redirects

### Challenge: JavaScript Rendering Time
**Problem:** Sections may not load immediately

**Solution:**
- Wait for specific element: `section-action-wrapper`
- Use WebDriverWait with explicit conditions
- Configurable timeout (default 10s)

### Challenge: Section URL Construction
**Problem:** URL format is complex: `#IPC2018P5_Ch01_SubCh01_Sec101.1`

**Solution:**
- Parse from `<h1>` id attribute: `text-id-24698365`
- Or construct manually: `IPC2018P5_Ch{chapter:02d}_SubCh{chapter:02d}_Sec{section_num}`
- Best: Use existing href if link exists in page

---

## Success Criteria

**Scraper is successful when:**
- ✅ Can scrape Chapter 1 and get ~15-20 sections
- ✅ All section data complete (number, title, description, URL)
- ✅ JSON validates with `populate_icc_data.py`
- ✅ Can insert into database successfully
- ✅ Works in both headless and visible modes
- ✅ Clear error messages if something fails
- ✅ Can scale to all 13 chapters (~200-300 sections)

---

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Chrome startup | ~2s | One time |
| Load chapter page | ~3-5s | Per chapter |
| Parse sections | <1s | Per chapter |
| Single chapter | ~5-7s | Total |
| All 13 chapters | ~2-3 min | With 2s delays |

---

## Next Steps

1. **Get user approval** on this design
2. **Create test script** - Single section extraction test
3. **Implement scraper** - Following this spec
4. **Test & iterate** - Fix any issues found
5. **Document** - Update README with usage

---

## Questions for User

Before implementing, confirm:
- [ ] Is the output JSON format correct?
- [ ] Should we scrape all 13 IPC chapters, or a subset?
- [ ] Any specific chapters to prioritize?
- [ ] Should scraper handle multiple ICC codes (IBC, IRC) or just IPC for now?
