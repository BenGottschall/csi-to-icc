# CSI to ICC Code Mapper

**🔗 Live App: [csimap.up.railway.app](https://csimap.up.railway.app/)**

A web tool that helps construction professionals and civil engineers quickly map CSI MasterFormat specification codes to relevant ICC (International Code Council) building code sections.

## The Problem

Converting CSI specification codes to ICC compliance requirements is tedious and time-consuming:
- Requires extensive knowledge of both coding systems
- Involves manually cross-referencing multiple documents
- Takes valuable time away from actual design and engineering work

## The Solution

Enter a CSI code, get relevant ICC code sections instantly:
- ✅ **Fast search** - Find ICC sections in seconds, not hours
- ✅ **Smart matching** - Keyword-based search finds relevant sections automatically
- ✅ **Direct links** - Jump straight to official ICC documentation
- ✅ **Filter by document** - Search within specific ICC codes (IPC, IBC, etc.)

## How It Works

1. **Enter a CSI code** (e.g., "03 30 00" for Cast-in-Place Concrete)
2. **Select an ICC document** (currently IPC 2018, more coming soon)
3. **Get results** - See matching ICC sections with descriptions and direct links

## Current Data

- **8,778 CSI MasterFormat 2016 codes** across all divisions
- **1,087 IPC 2018 sections** (International Plumbing Code)
- More ICC documents coming soon (IBC, IRC, IECC, IMC)

## Tech Stack

**Backend:** Python, FastAPI, PostgreSQL
**Frontend:** Next.js 15, TypeScript, Tailwind CSS
**Hosting:** Railway

## For Developers

### Local Development

**Prerequisites:** Docker and Docker Compose

```bash
git clone https://github.com/yourusername/csi-to-icc.git
cd csi-to-icc

# Start all services (backend, frontend, database)
make dev

# View logs
make logs

# Access locally
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
```

See [DOCKER.md](DOCKER.md) for detailed setup instructions and [TODO.md](TODO.md) for planned features.

### API Usage

```bash
# Search for ICC sections by CSI code
curl -X POST https://csi-to-icc-backend-production.up.railway.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"csi_code": "03 30 00"}'
```

Full API documentation: [Backend API Docs](https://csi-to-icc-backend-production.up.railway.app/api/docs)

## Contributing

Found a bug? Have a feature request? Open an issue!

Want to add ICC code mappings? Contributions from construction professionals are especially welcome.

## License

MIT

## Acknowledgments

Built to help engineers and construction professionals work more efficiently.

**Note:** ICC codes are copyrighted by the International Code Council. CSI MasterFormat is maintained by the Construction Specifications Institute. This tool links to official sources rather than hosting copyrighted content.
