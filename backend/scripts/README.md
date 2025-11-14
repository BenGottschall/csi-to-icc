# ICC Code Scraper

Scripts to scrape ICC code data from codes.iccsafe.org and populate the database.

## Overview

These scripts automate the process of extracting code sections from the ICC website and inserting them into your database. This is specifically configured for the **2018 International Plumbing Code (IPC)** but can be adapted for other codes.

## Prerequisites

1. **Python Dependencies** (already installed):
   ```bash
   pip install selenium webdriver-manager beautifulsoup4 lxml
   ```

2. **Free ICC Account**:
   - Register at: https://codes.iccsafe.org/register
   - Free accounts have full read access to codes

3. **Chrome/Chromium Browser**:
   - Required for Selenium WebDriver
   - ChromeDriver auto-installed by `webdriver-manager`

## Setup

### 1. Create Credentials File

Copy the example file and add your credentials:

```bash
cd backend
cp icc_credentials.env.example icc_credentials.env
```

Edit `icc_credentials.env`:
```env
ICC_USERNAME=your_email@example.com
ICC_PASSWORD=your_password
```

**Important**: This file is gitignored and will not be committed.

### 2. Register ICC Account

If you don't have an account:

1. Visit https://codes.iccsafe.org/register
2. Fill in your information (all fields required)
3. Verify your email
4. Login to confirm access works

## Usage

### Quick Start (Test with 2 Chapters)

```bash
cd backend
source venv/bin/activate

# Step 1: Scrape data from ICC website
python scripts/icc_scraper.py --chapters 2

# Step 2: Preview what will be inserted (dry run)
python scripts/populate_icc_data.py --dry-run

# Step 3: Populate database
python scripts/populate_icc_data.py
```

### Full IPC Scrape (All 13 Chapters)

```bash
# This will take 3-5 minutes and scrape ~200-300 sections
python scripts/icc_scraper.py --chapters 13 --output ipc_2018_full.json

# Populate database
python scripts/populate_icc_data.py --file ipc_2018_full.json
```

## Script Details

### `icc_scraper.py`

Scrapes code sections from codes.iccsafe.org using Selenium browser automation.

**Options**:
- `--chapters N`: Number of chapters to scrape (default: 2)
- `--output FILE`: Output JSON filename (default: `ipc_2018_scraped.json`)
- `--headless`: Run browser in headless mode (default: True)

**What it does**:
1. Launches Chrome browser
2. Logs into ICC website with your credentials
3. Navigates to IPC 2018 table of contents
4. Scrapes each chapter for section data
5. Saves to JSON file

**Output**: `scripts/ipc_2018_scraped.json` containing:
```json
{
  "code": "IPC",
  "year": 2018,
  "title": "2018 International Plumbing Code",
  "base_url": "https://codes.iccsafe.org/content/IPC2018P5",
  "chapters_scraped": 2,
  "total_sections": 45,
  "sections": [
    {
      "section_number": "101.1",
      "title": "Title",
      "url": "https://codes.iccsafe.org/content/IPC2018P5/chapter-1#IPC2018P5_Ch01_Sec101.1",
      "description": "These regulations shall be known as the International Plumbing Code...",
      "chapter": "1"
    },
    ...
  ]
}
```

### `populate_icc_data.py`

Reads scraped JSON and inserts data into the database.

**Options**:
- `--file FILE`: JSON file to load (default: `ipc_2018_scraped.json`)
- `--dry-run`: Preview without making changes

**What it does**:
1. Loads scraped JSON file
2. Creates ICC Document record (if doesn't exist)
3. Creates ICC Section records for each section
4. Skips duplicates automatically

## Troubleshooting

### Login Fails

**Error**: "Login failed: Unable to locate element"

**Solutions**:
- Verify credentials in `icc_credentials.env` are correct
- Check if ICC website structure changed
- Try running without headless mode:
  ```bash
  python scripts/icc_scraper.py --headless false
  ```

### No Sections Found

**Error**: "Found 0 sections in chapter X"

**Solutions**:
- ICC website may have changed HTML structure
- Try different chapter numbers
- Inspect browser output (run without headless)

### ChromeDriver Issues

**Error**: "chromedriver not found"

**Solutions**:
- `webdriver-manager` should auto-install
- Manually install: `sudo apt install chromium-browser chromium-chromedriver` (Linux)
- Or download from: https://chromedriver.chromium.org/

### Database Errors

**Error**: "Database connection failed"

**Solutions**:
- Ensure database is running
- Check `DATABASE_URL` in `backend/.env`
- Run migrations: `alembic upgrade head`

## Data Flow

```
┌─────────────────┐
│ ICC Website     │
│ (codes.iccsafe) │
└────────┬────────┘
         │
         │ Selenium scrapes
         ▼
┌──────────────────┐
│ icc_scraper.py   │
└────────┬─────────┘
         │
         │ Generates JSON
         ▼
┌────────────────────────────┐
│ ipc_2018_scraped.json      │
│ {sections: [...]}          │
└────────┬───────────────────┘
         │
         │ Parsed by
         ▼
┌─────────────────────────┐
│ populate_icc_data.py    │
└────────┬────────────────┘
         │
         │ Inserts into
         ▼
┌─────────────────────────┐
│ PostgreSQL Database     │
│  - icc_documents        │
│  - icc_sections         │
└─────────────────────────┘
```

## Extending to Other Codes

To scrape other ICC codes (IBC, IRC, IFC, etc.):

1. **Update base URL** in `icc_scraper.py`:
   ```python
   self.ibc_2024_url = f"{self.base_url}/content/IBC2024"
   ```

2. **Update document metadata**:
   ```python
   result = {
       'code': 'IBC',
       'year': 2024,
       'title': '2024 International Building Code',
       ...
   }
   ```

3. **Run scraper** with new code

## Best Practices

1. **Start Small**: Always test with 1-2 chapters first
2. **Respect Rate Limits**: 2-3 second delays between requests
3. **Check Data Quality**: Review JSON before populating database
4. **Use Dry Run**: Always run with `--dry-run` first
5. **Backup Database**: Before large imports

## Legal & Ethical

- **Copyright**: ICC codes are copyrighted by International Code Council
- **Usage**: Free accounts allow reading for personal/professional reference
- **Redistribution**: Do not redistribute scraped data publicly
- **Commercial Use**: Requires paid ICC license
- **Rate Limiting**: Be respectful - don't hammer their servers

## Performance

| Action | Time | Data |
|--------|------|------|
| Login | ~5 sec | - |
| Single chapter | ~10 sec | ~15-30 sections |
| 2 chapters (test) | ~30 sec | ~40-60 sections |
| Full IPC (13 chapters) | ~3-5 min | ~200-300 sections |
| Database insert | <1 sec | 100 sections |

## Support

If you encounter issues:
1. Check error message carefully
2. Review troubleshooting section above
3. Try running with `--headless false` to see browser
4. Check if ICC website structure changed
5. Verify credentials are correct

## Example Session

```bash
$ cd backend
$ source venv/bin/activate

$ python scripts/icc_scraper.py --chapters 2
============================================================
Starting ICC 2018 IPC Scraper
============================================================
Setting up Chrome WebDriver...
WebDriver ready!
Logging in as user@example.com...
Login successful!
Fetching table of contents...
Found 13 chapters

Limiting to first 2 chapters for testing

[1/2] Processing chapter...
Scraping Chapter 1: Administration
  Found 25 sections in chapter 1

[2/2] Processing chapter...
Scraping Chapter 2: Definitions
  Found 20 sections in chapter 2

============================================================
Scraping complete! Found 45 sections
============================================================

Data saved to: scripts/ipc_2018_scraped.json

✓ Successfully scraped 45 sections from 2 chapters

Browser closed.

$ python scripts/populate_icc_data.py --dry-run
============================================================
ICC Data Population Script
============================================================
Loaded data: IPC 2018
  - 2 chapters
  - 45 sections

🔍 DRY RUN MODE - No changes will be made to database

Would create:
  - 1 ICC Document: IPC 2018
  - 45 ICC Sections

✓ Success!

$ python scripts/populate_icc_data.py
============================================================
ICC Data Population Script
============================================================
Loaded data: IPC 2018
  - 2 chapters
  - 45 sections

Connecting to database...

✓ Created ICC Document: IPC 2018 (ID: 2)

Inserting 45 sections...

✓ Created 45 new sections

============================================================
✓ Database population complete!
============================================================

Summary:
  - ICC Document ID: 2
  - Sections inserted: 45

You can now search for ICC sections in the web app!

✓ Success!
```
