# Axiom

Axiom is a single-source-of-truth operational platform for messy real-world inputs. This codebase provides a production-friendly MVP architecture for:

- multimodal document ingestion
- client and invoice reconciliation
- asset tracking and location history
- exception-first workflows

## Quick start

1. Create a virtual environment with Python 3.14.7:
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
uvicorn app.main:app --reload
```

## Example requests

### Ingest a rough document
```bash
curl -X POST http://localhost:8000/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "receipt",
    "raw_text": "Acme Build Co. Labor 2 @ 150.00, materials 1 @ 250.00. Total 550.00"
  }'
```

### Generate an invoice from a document
```bash
curl -X POST http://localhost:8000/invoices/generate \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_0001"}'
```

### Register an asset
```bash
curl -X POST http://localhost:8000/assets/register \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Impact Drill",
    "category":"tool",
    "location":"Red Trailer",
    "source":"site_photo",
    "confidence":0.92
  }'
```

### Update location
```bash
curl -X POST http://localhost:8000/assets/location \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id":"asset_0001",
    "location":"Green Truck",
    "source":"gps_beacon",
    "confidence":0.87
  }'
```

## Design principles

- Tolerant data model: accepts noisy real-world input
- Evidence-linked records: every invoice and asset update retains source context
- Exception-driven operations: humans only intervene for real conflicts
- Versionable state: future work can plug in persistent storage and audit logs