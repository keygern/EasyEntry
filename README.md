# EasyEntry

EasyEntry extracts data from invoices and CBP forms using AWS Textract and stores the results in S3. The API is built with FastAPI and SQLModel and uses Supabase for authentication and Stripe for billing.

## Requirements
- Python 3.11+
- PostgreSQL database
- Redis for Celery broker
- Node.js 18+ for the frontend

### Environment Variables
- `AWS_S3_BUCKET` – S3 bucket where uploads and results are stored
- `AWS_REGION` – AWS region (default `us-east-1`)
- `STRIPE_SK` – Stripe secret key
- `STRIPE_WH_SECRET` – Stripe webhook signing secret
- `SUPABASE_URL` – Supabase project URL
- `SUPABASE_JWT_SECRET` – JWT secret from Supabase
- `CELERY_BROKER_URL` – Redis URL (e.g. `redis://localhost:6379/0`)

Create a `.env` file with these values.

## Backend
Create the database and tables then run the API server:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "from db import create_db_and_tables; create_db_and_tables()"
uvicorn main:app --reload
```

Start the Celery worker in another terminal:

```bash
celery -A services.tasks.celery_app worker --loglevel info
```

## Frontend
The frontend lives in `frontend/` and uses Next.js.

```bash
cd frontend
npm install    # install dependencies once
npm run dev    # or `npm run build` to create a production build
```

The app expects to be served from `https://easyentry.vercel.app` and the API from your FastAPI server.
