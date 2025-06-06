# EasyEntry

This project provides a FastAPI backend and a simple Next.js frontend.

## Environment Variables

The frontend expects `NEXT_PUBLIC_API_URL` to be set to the base URL of the FastAPI server.

The backend requires an `AWS_S3_BUCKET` where Textract results will be stored.

When deploying on Vercel (or another hosting provider), add `NEXT_PUBLIC_API_URL` to your environment variables so the frontend can reach the API.

Example `.env.local`:

```
NEXT_PUBLIC_API_URL=https://api.example.com
```

## Running Locally

1. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   uvicorn main:app --reload
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```
4. Start the frontend:
   ```bash
   npm run dev
   ```
5. Run the tests:
   ```bash
   pytest -q
   ```
