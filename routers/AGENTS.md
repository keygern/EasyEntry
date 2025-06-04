# API & Billing Guide

## Routes
| Method | Path | Body | Response |
|--------|------|------|----------|
| POST   | /documents/upload | multipart `file`, `doc_type` | `{ job_id }` |
| GET    | /documents/parse/{doc_type}/{job_id} | – | `{ status, needs_mapping?, data?, pdf_url? }` |
| POST   | /column-mapping | `{ qty_col:int, val_col:int }` | `204` |
| GET    | /documents/pdf/{doc_type}/{job_id} | – | `application/pdf` |

*Auth* – every route uses `verify_supabase_jwt` dependency → `user_id`  
*Quota* – before `/upload`, check plan vs monthly filings. Over quota → **402**.

### Stripe Billing (embedded here)
* `/checkout/{plan}`  
  - Include `client_reference_id=<user_id>`  
  - Plans: hobby 5, growth 50, pro ∞ filings per month
* `/billing/webhook`
  - Verify signature (`STRIPE_WH_SECRET`)
  - On `checkout.session.completed` → update `users.plan`, `quota_remaining`
  - Handle `invoice.payment_failed` & `customer.subscription.deleted` (downgrade)

Return **JSON** only; no HTML. Enable CORS for `https://easyentry.vercel.app`.
