# CSI to ICC Code Mapping Tool

A web application that helps civil engineers and construction professionals quickly map CSI MasterFormat codes to relevant ICC (International Code Council) building code sections.

## Problem

Converting CSI specification codes to ICC compliance requirements is a manual, time-consuming process that requires:
- Extensive knowledge of both systems
- Cross-referencing multiple documents
- Tracking state-specific amendments
- Staying current with code updates

## Solution

This tool provides:
- **Quick lookup**: Enter a CSI code and instantly see relevant ICC sections
- **Smart filtering**: Filter by state, year, and ICC document type
- **Direct links**: Jump straight to official ICC documentation
- **State amendments**: See state-specific code modifications

## Tech Stack

### Backend
- Python 3.13+ with FastAPI
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations

### Frontend
- Next.js 15 with TypeScript
- Tailwind CSS

## Getting Started

### Docker Setup (Recommended)

**Prerequisites:** Docker 20.10+ and Docker Compose 2.0+

```bash
git clone <repository-url>
cd csi-to-icc

# Start services
make dev              # Development mode with hot-reload
# OR
make up               # Production mode

# View logs
make logs

# Access the application
# Backend API: http://localhost:8000/api/docs
# Frontend: http://localhost:3000 (coming soon)
```

See `DOCKER.md` or run `make help` for all available commands.

### Manual Setup

**Prerequisites:** Python 3.13+, PostgreSQL 14+, Node.js 20+

```bash
# Clone and setup
git clone <repository-url>
cd csi-to-icc/backend

# Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database
createdb csi_icc_db
cp .env.example .env      # Edit DATABASE_URL in .env
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/api/docs`

## API Usage

```bash
# Search for ICC sections
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"csi_code": "03 30 00", "state": "CO", "year": 2024}'

# List CSI codes
curl http://localhost:8000/api/csi-codes
```

See full API documentation at `http://localhost:8000/api/docs`

## Database Schema

The application uses five main tables:

1. **csi_codes** - CSI MasterFormat codes
2. **icc_documents** - ICC code documents (IBC, IRC, etc.)
3. **icc_sections** - Specific sections within ICC documents
4. **csi_icc_mappings** - Relationships between CSI and ICC codes
5. **state_amendments** - State-specific code modifications

See `CLAUDE.md` for detailed schema information.

## Development

**Database migrations:**
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

**Run tests:**
```bash
pytest
```

See `CLAUDE.md` for detailed project documentation and architecture.

## Data Population

Use the API to add CSI codes, ICC documents, sections, and mappings. See `/api/docs` for endpoint details and schemas.

## Contributing

Suggestions and feedback welcome! Please open an issue.

## License

MIT

## Acknowledgments

Built to help civil engineers streamline code compliance. ICC codes are copyright International Code Council; CSI MasterFormat is maintained by the Construction Specifications Institute. This tool links to official sources rather than hosting copyrighted content.
