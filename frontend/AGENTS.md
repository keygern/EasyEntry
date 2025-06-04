# Front-End MVP Spec

## Tech
* Next.js + TypeScript (or V0.dev export)
* TailwindCSS
* Supabase JS client (auth)

## Pages
### /upload
* File drop-zone → POST `/documents/upload`
* Poll `/documents/parse` every 3 s  
* If `needs_mapping` → render first 5 table rows, let user click qty/value → POST `/column-mapping` → re-poll.

### /results/[job_id]
* Show parsed line items, HS code, duty / total
* “Download 7501 PDF” → GET `/documents/pdf/7501/{job_id}`

### /account
* Display current plan & usage
* “Upgrade” → fetch `/checkout/{plan}` → redirect

## Notes
* Store Supabase JWT in `localStorage`; attach as Bearer to API calls.
* Use React Query for polling & cache.
* No secret keys in browser; only Supabase anon key.
