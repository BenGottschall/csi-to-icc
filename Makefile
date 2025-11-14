.PHONY: help build up down restart logs ps clean migrate shell-backend shell-frontend shell-db dev dev-build dev-down dev-logs dev-restart test backup restore health scrape-ipc scrape-ipc-test populate-ipc populate-ipc-dry

# Default target - show help
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  CSI to ICC Code Mapper - Docker Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📦 Production Commands:"
	@echo "  make up              Start all services (detached)"
	@echo "  make down            Stop and remove all containers"
	@echo "  make restart         Restart all services"
	@echo "  make build           Build all Docker images"
	@echo "  make logs            View logs (all services)"
	@echo "  make ps              Show running containers"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  make dev             Start in development mode (with hot-reload)"
	@echo "  make dev-build       Build and start in development mode"
	@echo "  make dev-down        Stop development services"
	@echo "  make dev-logs        View development logs"
	@echo "  make dev-restart     Restart development services"
	@echo ""
	@echo "🗄️  Database Commands:"
	@echo "  make migrate         Run database migrations"
	@echo "  make migrate-create  Create new migration (MSG='description')"
	@echo "  make shell-db        Access PostgreSQL shell"
	@echo "  make backup          Backup database to backups/db_backup_TIMESTAMP.sql"
	@echo "  make restore         Restore database (FILE=path/to/backup.sql)"
	@echo ""
	@echo "📥 Data Scraping Commands:"
	@echo "  make scrape-ipc      Scrape all IPC 2018 chapters (13 chapters, ~15-20 min)"
	@echo "  make scrape-ipc-test Test scraper with chapters 1 & 3 only"
	@echo "  make populate-ipc    Populate database with scraped data"
	@echo "  make populate-ipc-dry Preview what will be inserted (dry run)"
	@echo ""
	@echo "🔍 Shell Access:"
	@echo "  make shell-backend   Access backend container shell"
	@echo "  make shell-frontend  Access frontend container shell"
	@echo ""
	@echo "🧪 Testing & Health:"
	@echo "  make test            Run backend tests"
	@echo "  make health          Check service health"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  make clean           Stop and remove containers, volumes, images"
	@echo "  make clean-images    Remove only Docker images"
	@echo "  make clean-volumes   Remove only Docker volumes (⚠️  deletes data!)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "   Development:  make dev"
	@echo "   Production:   make up"
	@echo "   View logs:    make logs"
	@echo "   Stop:         make down"
	@echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Production Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

up:
	@echo "🚀 Starting services (production mode)..."
	docker compose up -d
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/api/docs"
	@echo ""
	@echo "📝 View logs: make logs"

down:
	@echo "🛑 Stopping services..."
	docker compose down
	@echo "✅ Services stopped!"

restart:
	@echo "🔄 Restarting services..."
	docker compose restart
	@echo "✅ Services restarted!"

build:
	@echo "🔨 Building Docker images..."
	docker compose build
	@echo "✅ Build complete!"

logs:
	@echo "📋 Showing logs (Ctrl+C to exit)..."
	docker compose logs -f

ps:
	@echo "📊 Container status:"
	@docker compose ps

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Development Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dev:
	@echo "🔧 Starting services (development mode with hot-reload)..."
	docker compose -f docker-compose.dev.yml up -d
	@echo "✅ Development services started!"
	@echo "   Frontend: http://localhost:3000  (hot-reload enabled)"
	@echo "   Backend:  http://localhost:8000  (hot-reload enabled)"
	@echo "   API Docs: http://localhost:8000/api/docs"
	@echo ""
	@echo "📝 View logs: make dev-logs"

dev-build:
	@echo "🔨 Building and starting development services..."
	docker compose -f docker-compose.dev.yml up -d --build
	@echo "✅ Development services started!"

dev-down:
	@echo "🛑 Stopping development services..."
	docker compose -f docker-compose.dev.yml down
	@echo "✅ Development services stopped!"

dev-logs:
	@echo "📋 Showing development logs (Ctrl+C to exit)..."
	docker compose -f docker-compose.dev.yml logs -f

dev-restart:
	@echo "🔄 Restarting development services..."
	docker compose -f docker-compose.dev.yml restart
	@echo "✅ Development services restarted!"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

migrate:
	@echo "🗄️  Running database migrations..."
	docker compose exec backend alembic upgrade head
	@echo "✅ Migrations complete!"

migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a migration message"; \
		echo "   Usage: make migrate-create MSG='your message'"; \
		exit 1; \
	fi
	@echo "📝 Creating new migration: $(MSG)"
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration created!"

shell-db:
	@echo "🗄️  Connecting to PostgreSQL..."
	@echo "   Database: csi_icc_db"
	@echo "   User: postgres"
	@echo "   (Type 'exit' or press Ctrl+D to quit)"
	@echo ""
	docker compose exec db psql -U postgres -d csi_icc_db

backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	docker compose exec db pg_dump -U postgres csi_icc_db > backups/db_backup_$$TIMESTAMP.sql && \
	echo "✅ Backup created: backups/db_backup_$$TIMESTAMP.sql"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: Please provide a backup file"; \
		echo "   Usage: make restore FILE=backups/db_backup_YYYYMMDD_HHMMSS.sql"; \
		exit 1; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
		echo "❌ Error: File '$(FILE)' not found"; \
		exit 1; \
	fi
	@echo "⚠️  WARNING: This will replace all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🔄 Restoring database from $(FILE)..."; \
		cat $(FILE) | docker compose exec -T db psql -U postgres -d csi_icc_db && \
		echo "✅ Database restored!"; \
	else \
		echo "❌ Restore cancelled"; \
	fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Shell Access
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

shell-backend:
	@echo "🐍 Accessing backend container shell..."
	@echo "   (Type 'exit' or press Ctrl+D to quit)"
	@echo ""
	docker compose exec backend sh

shell-frontend:
	@echo "⚛️  Accessing frontend container shell..."
	@echo "   (Type 'exit' or press Ctrl+D to quit)"
	@echo ""
	docker compose exec frontend sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Testing & Health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

test:
	@echo "🧪 Running backend tests..."
	docker compose exec backend pytest
	@echo "✅ Tests complete!"

health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "Backend API:"
	@curl -s http://localhost:8000/health || echo "  ❌ Backend not responding"
	@echo ""
	@echo ""
	@echo "Frontend:"
	@curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:3000 || echo "  ❌ Frontend not responding"
	@echo ""
	@echo "Database:"
	@docker compose exec -T db pg_isready -U postgres && echo "  ✅ Database is ready" || echo "  ❌ Database not responding"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cleanup Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

clean:
	@echo "🧹 Cleaning up Docker resources..."
	@echo "⚠️  This will remove:"
	@echo "   - All containers"
	@echo "   - All volumes (database data will be lost)"
	@echo "   - All images for this project"
	@echo ""
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v --rmi all && \
		echo "✅ Cleanup complete!"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi

clean-images:
	@echo "🧹 Removing Docker images..."
	docker compose down --rmi all
	@echo "✅ Images removed!"

clean-volumes:
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v && \
		echo "✅ Volumes removed!"; \
	else \
		echo "❌ Operation cancelled"; \
	fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Utility Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Show service logs for specific service
logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

logs-db:
	docker compose logs -f db

# Rebuild specific service
rebuild-backend:
	@echo "🔨 Rebuilding backend..."
	docker compose build backend
	docker compose up -d backend
	@echo "✅ Backend rebuilt!"

rebuild-frontend:
	@echo "🔨 Rebuilding frontend..."
	docker compose build frontend
	docker compose up -d frontend
	@echo "✅ Frontend rebuilt!"

# Stats
stats:
	@echo "📊 Docker resource usage:"
	docker compose stats

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Scraping Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

scrape-ipc:
	@echo "📥 Scraping all IPC 2018 chapters..."
	@echo "⏱️  This will take approximately 15-20 minutes"
	@echo "📁 Output: backend/scripts/extracted_data/ipc_2018/"
	@echo ""
	cd backend && python scripts/ipc_scraper_all.py --headless
	@echo ""
	@echo "✅ Scraping complete! Check backend/scripts/extracted_data/ipc_2018/"
	@echo "💡 Next step: make populate-ipc-dry (preview) or make populate-ipc (insert)"

scrape-ipc-test:
	@echo "🧪 Test mode: Scraping chapters 1 & 3 only..."
	@echo "📁 Output: backend/scripts/extracted_data/ipc_2018/"
	@echo ""
	cd backend && python scripts/ipc_scraper_all.py --test --headless
	@echo ""
	@echo "✅ Test scraping complete!"
	@echo "💡 Next step: make populate-ipc-dry (preview) or make populate-ipc (insert)"

populate-ipc-dry:
	@echo "🔍 DRY RUN: Preview database population..."
	@echo "📁 Reading: backend/scripts/extracted_data/ipc_2018/"
	@echo ""
	cd backend && python scripts/populate_all_chapters.py --dry-run
	@echo ""
	@echo "💡 This was a preview. Run 'make populate-ipc' to actually insert data."

populate-ipc:
	@echo "💾 Populating database with IPC 2018 data..."
	@echo "📁 Reading: backend/scripts/extracted_data/ipc_2018/"
	@echo ""
	cd backend && python scripts/populate_all_chapters.py
	@echo ""
	@echo "✅ Database population complete!"
	@echo "🌐 Test at: http://localhost:3000"
