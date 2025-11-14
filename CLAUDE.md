# CSI to ICC Code Mapping - Project Context

## Project Overview

This is a web application that helps civil engineers and construction professionals map CSI (Construction Specifications Institute) MasterFormat codes to ICC (International Code Council) building code sections.

**Problem**: Converting CSI specification codes to relevant ICC compliance codes is a manual, time-consuming process requiring extensive cross-referencing.

**Solution**: A web application where users can:
- Enter a CSI code
- Filter by state and year
- Get relevant ICC code sections with direct links to official documentation

## Tech Stack

### Backend
- **Language**: Python 3.13+
- **Framework**: FastAPI (REST API)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### Frontend (To Be Implemented)
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: fetch/Axios

## Project Structure

```
csi-to-icc/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database connection & session management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic schemas for API validation
│   │   ├── crud.py              # Database CRUD operations
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── codes.py         # API endpoints for CSI/ICC codes
│   ├── alembic/                 # Database migrations
│   ├── venv/                    # Python virtual environment (not in git)
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── .env                     # Actual environment variables (not in git)
├── frontend/                    # Next.js application (to be created)
├── .gitignore
├── CLAUDE.md                    # This file
└── README.md                    # User-facing documentation
```

## Database Schema

### Tables

1. **csi_codes** - CSI MasterFormat codes
   - `id` (PK)
   - `code` (unique, e.g., "03 30 00")
   - `division` (integer)
   - `title` (e.g., "Cast-in-Place Concrete")
   - `description`

2. **icc_documents** - ICC code documents (IBC, IRC, etc.)
   - `id` (PK)
   - `code` (e.g., "IBC", "IRC")
   - `year` (e.g., 2021, 2024)
   - `title`
   - `state` (nullable, for state-specific codes)
   - `base_url` (link to codes.iccsafe.org)

3. **icc_sections** - Specific sections within ICC documents
   - `id` (PK)
   - `document_id` (FK to icc_documents)
   - `section_number` (e.g., "1905.2")
   - `title`
   - `chapter`
   - `url` (direct link to section)
   - `description`

4. **csi_icc_mappings** - Many-to-many relationship
   - `id` (PK)
   - `csi_code_id` (FK)
   - `icc_section_id` (FK)
   - `relevance` (primary/secondary/reference)
   - `notes`
   - `created_at`

5. **state_amendments** - State-specific code amendments
   - `id` (PK)
   - `icc_section_id` (FK)
   - `state`
   - `amendment_text`
   - `effective_date`

## API Endpoints

### CSI Codes
- `GET /api/csi-codes` - List all CSI codes
- `GET /api/csi-codes/{code}` - Get specific CSI code
- `POST /api/csi-codes` - Create new CSI code
- `GET /api/csi-codes/{code}/icc-sections` - Get ICC sections for a CSI code (supports filters)

### ICC Documents
- `GET /api/icc-documents` - List ICC documents (with filters)
- `GET /api/icc-documents/{id}` - Get specific document
- `POST /api/icc-documents` - Create new document

### ICC Sections
- `GET /api/icc-sections/{id}` - Get specific section
- `POST /api/icc-sections` - Create new section
- `GET /api/icc-sections/{id}/amendments` - Get state amendments

### Mappings
- `POST /api/mappings` - Create CSI-to-ICC mapping

### Search
- `POST /api/search` - Main search endpoint
  - Body: `{ "csi_code": "03 30 00", "state": "CO", "year": 2024 }`

## Development Approach

### Phase 1: MVP (Current)
✅ Backend API structure
✅ Database schema
✅ Basic CRUD operations
⏳ Frontend (Next.js)
⏳ Initial data population (10-20 mappings)

### Phase 2: Data Population
- Manually create mappings for common CSI codes
- Use LLMs to suggest mappings (with expert verification)
- Focus on most-used divisions (concrete, steel, wood, etc.)

### Phase 3: Features
- Natural language search
- User accounts and saved searches
- Community contributions (with moderation)
- Export functionality

## Data Sources

### Legal & Available
- **codes.iccsafe.org** - Free public access to ICC codes
- State government websites - Many publish adopted codes
- Your friend's expertise - Initial mappings
- LLMs - Draft suggestions (must be verified)

### Important Notes
- ICC code content is copyrighted but publicly viewable
- We link to official sources rather than hosting content
- State amendments are often public domain
- Manual verification is essential for accuracy

## Development Setup

See README.md for setup instructions.

## Key Design Decisions

1. **Approach 1 (Direct Linking)**: We map CSI codes to ICC section URLs rather than scraping/hosting content
2. **PostgreSQL**: Chosen for robust relational data handling and future scalability
3. **FastAPI**: Modern Python framework with auto-generated API docs
4. **Alembic**: Database version control for schema changes
5. **Pydantic v2**: Type-safe API validation

## Future Considerations

- Add full-text search (PostgreSQL `tsvector`)
- Implement caching (Redis) for popular queries
- Add analytics to track most-searched codes
- Consider ICC partnership for official data access
- Mobile app version

## Testing Strategy

- Unit tests for CRUD operations
- Integration tests for API endpoints
- Manual testing with real CSI codes
- Expert validation of mappings

## Deployment (Future)

- **Backend**: Railway, Render, or DigitalOcean
- **Frontend**: Vercel (optimized for Next.js)
- **Database**: Managed PostgreSQL
- **CI/CD**: GitHub Actions

## Contact & Collaboration

This is a personal project built to help a friend in civil engineering. The goal is to create a genuinely useful tool while building a portfolio-worthy full-stack application.
