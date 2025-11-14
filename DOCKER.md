# Docker Setup Guide

This guide covers running the CSI to ICC Code Mapping application using Docker and Docker Compose.

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

To check your versions:
```bash
docker --version
docker compose version
```

## Makefile Commands (Recommended!)

We provide a Makefile for easy Docker management. Run `make help` to see all available commands:

```bash
make help          # Show all available commands
make dev           # Start in development mode
make up            # Start in production mode
make down          # Stop all services
make logs          # View logs
make migrate       # Run database migrations
make shell-db      # Access database shell
make backup        # Backup database
make health        # Check service health
make clean         # Clean up everything
```

**Quick start:**
```bash
# Development (with hot-reload)
make dev

# Production
make up

# View what's happening
make logs
```

## Quick Start

### Production Mode

Run the complete application stack in production mode:

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432

### Development Mode

Run with hot-reloading for local development:

```bash
# Build and start all services in development mode
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop all services
docker compose -f docker-compose.dev.yml down
```

## Services

### 1. PostgreSQL Database (`db`)
- **Image**: postgres:16-alpine
- **Port**: 5432
- **Database**: csi_icc_db
- **Username**: postgres
- **Password**: postgres (change in production!)
- **Volume**: postgres_data (persistent storage)

### 2. Backend API (`backend`)
- **Port**: 8000
- **Framework**: FastAPI
- **Auto-migrations**: Runs Alembic migrations on startup
- **Health check**: `/health` endpoint

### 3. Frontend (`frontend`)
- **Port**: 3000
- **Framework**: Next.js 15
- **API URL**: Configured to connect to backend at http://localhost:8000

## Docker Commands

### Building Images

```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend

# Build with no cache (force rebuild)
docker compose build --no-cache
```

### Starting Services

```bash
# Start all services
docker compose up

# Start in detached mode (background)
docker compose up -d

# Start specific service
docker compose up backend

# Start with build
docker compose up --build
```

### Stopping Services

```bash
# Stop all services (containers remain)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes + images
docker compose down -v --rmi all
```

### Viewing Logs

```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs for specific service
docker compose logs backend
docker compose logs -f frontend

# View last 100 lines
docker compose logs --tail=100
```

### Executing Commands in Containers

```bash
# Access backend shell
docker compose exec backend sh

# Access database shell
docker compose exec db psql -U postgres -d csi_icc_db

# Run Alembic migration
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Run Python script
docker compose exec backend python scripts/add_sample_data.py
```

### Viewing Container Status

```bash
# List running containers
docker compose ps

# View resource usage
docker compose stats

# Inspect service configuration
docker compose config
```

## Development Workflow

### Hot Reloading

Development mode (`docker-compose.dev.yml`) includes volume mounts for hot-reloading:

**Backend changes** (Python files in `app/`):
- Changes detected automatically by uvicorn's `--reload` flag
- No container restart needed

**Frontend changes** (TypeScript/TSX files in `app/`):
- Changes detected by Next.js development server
- Browser auto-refreshes

### Database Migrations

After modifying `backend/app/models.py`:

```bash
# Generate migration
docker compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migration
docker compose exec backend alembic upgrade head

# Rollback migration
docker compose exec backend alembic downgrade -1

# View migration history
docker compose exec backend alembic history
```

### Accessing the Database

```bash
# Connect to PostgreSQL
docker compose exec db psql -U postgres -d csi_icc_db

# Run SQL query
docker compose exec db psql -U postgres -d csi_icc_db -c "SELECT * FROM csi_codes;"

# Backup database
docker compose exec db pg_dump -U postgres csi_icc_db > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U postgres -d csi_icc_db
```

## Troubleshooting

### Port Already in Use

If you see `port is already allocated` errors:

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Change ports in docker-compose.yml
# Example: "8001:8000" instead of "8000:8000"
```

### Database Connection Errors

```bash
# Check database is running
docker compose ps db

# View database logs
docker compose logs db

# Wait for database to be ready
docker compose exec backend sh -c "until pg_isready -h db -U postgres; do sleep 1; done"

# Restart database
docker compose restart db
```

### Container Won't Start

```bash
# View full logs
docker compose logs backend

# Check container status
docker compose ps -a

# Remove and rebuild
docker compose down
docker compose build --no-cache backend
docker compose up backend
```

### Migration Errors

```bash
# Check current migration status
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history

# Reset database (WARNING: deletes all data!)
docker compose down -v
docker compose up -d
```

### Clean Slate Restart

```bash
# Remove everything and start fresh
docker compose down -v --rmi all
docker compose build --no-cache
docker compose up -d
```

## Production Deployment

### Security Best Practices

1. **Change default passwords**:
   ```yaml
   # In docker-compose.yml
   environment:
     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # Use env variable
   ```

2. **Use secrets management**:
   ```bash
   # Store secrets in .env file (not committed to git)
   echo "POSTGRES_PASSWORD=strong_password_here" >> .env
   ```

3. **Limit exposed ports**:
   ```yaml
   # Don't expose database port in production
   # Remove or comment out:
   # ports:
   #   - "5432:5432"
   ```

4. **Use HTTPS** with a reverse proxy (nginx, Traefik, Caddy)

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_DB=csi_icc_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Backend
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/csi_icc_db
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

Then reference in `docker-compose.yml`:
```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### Health Checks

Both backend and frontend include health checks:

```bash
# Check service health
docker compose ps

# Manually test health endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

### Monitoring

```bash
# View resource usage
docker compose stats

# View container events
docker compose events

# Export logs to file
docker compose logs > logs.txt
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (csi-icc-network)                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │  PostgreSQL  │  │
│  │   Next.js    │  │   FastAPI    │  │   Database   │  │
│  │   Port 3000  │  │   Port 8000  │  │   Port 5432  │  │
│  │              │  │              │  │              │  │
│  │  - React UI  │─▶│  - REST API  │─▶│  - Data      │  │
│  │  - Tailwind  │  │  - SQLAlchemy│  │  - Volume    │  │
│  │              │  │  - Alembic   │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                            │
└─────────┼──────────────────┼────────────────────────────┘
          │                  │
          ▼                  ▼
    localhost:3000     localhost:8000
```

## Additional Resources

- **Docker Docs**: https://docs.docker.com
- **Docker Compose Docs**: https://docs.docker.com/compose
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

## Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Review this troubleshooting guide
3. Open an issue on GitHub
