# Axiom: Elite-Grade Operational Platform

Production-ready stack for handling messy real-world inputs: invoicing, compliance, and asset tracking.

## Architecture

### Backend
- **FastAPI** with async support
- **PostgreSQL** for relational data
- **Redis** for caching and task queues
- **Celery** for async document processing
- **SQLAlchemy** ORM with full type safety
- **JWT** authentication
- **S3-compatible** object storage integration

### Frontend
- **React 18** with TypeScript
- **Zustand** for state management
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API calls

### Key Features
- Tolerant multimodal document ingestion
- Automatic invoice generation from documents
- Asset tracking with location history
- Exception-driven workflow (only surface real conflicts)
- Evidence-linked records (audit trail)
- Full team/multi-user support
- Tax and compliance packet generation

## Quick Start

### Prerequisites
- Docker and Docker Compose (runs PostgreSQL 18 via `postgres:18-alpine`)
- PostgreSQL 18 (installed locally on host PC or via Docker)
- Node.js 18+ (if running frontend locally)
- Python 3.14.7 (installed on system / virtualenv)

### Run with Docker Compose
```bash
docker-compose up
```

Backend: http://localhost:8000
Frontend: http://localhost:5173
API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
# Create and activate Python 3.14.7 environment
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Clients
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients` - List clients
- `GET /api/v1/clients/{client_id}` - Get client
- `PUT /api/v1/clients/{client_id}` - Update client
- `DELETE /api/v1/clients/{client_id}` - Delete client

### Documents
- `POST /api/v1/documents/upload` - Upload document (receipt, timesheet, PDF, etc.)
- `POST /api/v1/documents/{document_id}/process` - Process document (OCR, extraction)

### Invoices
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices` - List invoices
- `GET /api/v1/invoices/{invoice_id}` - Get invoice
- `PUT /api/v1/invoices/{invoice_id}` - Update invoice

### Assets
- `POST /api/v1/assets/register` - Register asset
- `GET /api/v1/assets` - List assets
- `GET /api/v1/assets/{asset_id}` - Get asset
- `POST /api/v1/assets/{asset_id}/location` - Update asset location
- `GET /api/v1/assets/{asset_id}/history` - Get asset location history

### Exceptions
- `POST /api/v1/exceptions/scan` - Scan and create exceptions
- `GET /api/v1/exceptions` - Get exception queue
- `POST /api/v1/exceptions/{exception_id}/resolve` - Resolve exception

## Environment Variables

See `backend/.env.example` for all configuration options.

Critical settings:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection
- `JWT_SECRET_KEY` - Change in production
- `S3_*` - AWS S3 credentials for document storage
- `STRIPE_*` - Stripe payment keys (for future billing)

## Data Model

### Core Entities
- **User** - Team member with login credentials
- **Team** - Organization/workspace
- **Client** - Customer/vendor record with tax ID and terms
- **Invoice** - Generated invoice with line items, totals, tax
- **LineItem** - Individual line on an invoice
- **Document** - Ingested source document (receipt, timesheet, PDF, photo)
- **Expense** - Tracked expense with category and receipt
- **Payment** - Payment against an invoice
- **Asset** - Physical tool or equipment
- **AssetLocationEvent** - Historical location record for an asset
- **Contract** - Client contract with terms
- **Exception** - Workflow exception (missing data, conflicts, etc.)
- **AuditLog** - Full audit trail of all changes

### Key Design Patterns
- **Evidence Linking**: All records retain source references for traceability
- **Temporal History**: Assets track full location history
- **Exception-First**: Default to automation; surface only true conflicts
- **Multi-Tenant**: Full team/workspace isolation
- **Async Processing**: Document processing via Celery workers

## Deployment

### Production Checklist
- [ ] Update `JWT_SECRET_KEY` and all API keys in `.env`
- [ ] Configure PostgreSQL with replication + backups
- [ ] Set up Redis persistence
- [ ] Enable S3 versioning and lifecycle policies
- [ ] Configure CORS properly for your domain
- [ ] Set up SSL/TLS with nginx or ALB
- [ ] Configure application monitoring (Sentry, NewRelic)
- [ ] Set up log aggregation (ELK, Datadog)
- [ ] Enable database connection pooling
- [ ] Scale Celery workers horizontally

### Kubernetes (future)
- Helm charts for backend, frontend, worker, beat
- StatefulSet for PostgreSQL
- ConfigMaps for environment variables
- Secrets for credentials
- Horizontal Pod Autoscaling

## Testing
```bash
# Backend tests (pytest)
cd backend
pytest tests/ -v --cov

# Frontend tests (vitest)
cd frontend
npm run test
```

## Contributing
- Follow PEP 8 for Python
- Use TypeScript strict mode
- All public functions must have docstrings/JSDoc
- All database changes must be migrations
- No truncation of error handling

## License
MIT