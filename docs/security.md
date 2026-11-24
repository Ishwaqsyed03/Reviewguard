# API security configuration

## Required deployment settings

Configure these on the API host (Render), not in the Next.js `NEXT_PUBLIC_*` environment:

- `FRONTEND_ORIGINS`: comma-separated exact origins allowed to call the API, including scheme and host. For local development use `http://localhost:3000`; add the actual deployed front-end origin in production. Do not include a path or trailing slash.
- `REVIEWGUARD_ADMIN_TOKEN`: a long random secret used only to authorize model training. Generate it with a password manager or a cryptographically secure generator. Never place it in browser code, a committed file, or a public build variable.
- `RATELIMIT_STORAGE_URI` (optional): a shared rate-limit store such as Redis when running multiple API instances. The default is in-memory and resets when the process restarts.

Without `REVIEWGUARD_ADMIN_TOKEN`, `POST /api/train` returns 503 and cannot replace the model. With a token, send it as a bearer credential:

```http
Authorization: Bearer <admin-token>
```

## Public API limits

- `POST /api/detect`: at most 10 requests per minute per client IP; review text is limited to 10,000 characters, IDs to 100 characters, and numeric values are range checked.
- `GET /api/reviews`: at most 30 requests per minute; page size is limited to 1–100. The response contains only analysis summary fields.
- `POST /api/train`: requires the admin bearer token and is limited to 2 requests per hour per client IP.
- Other API routes use a default limit of 120 requests per minute per client IP.

The default in-memory rate-limit store is suitable only for a single-process demo. Use a shared store for multiple workers or instances; IP-based throttling is not a substitute for authentication or abuse monitoring.

## Data handling

New detections are analyzed in memory. The database stores the rating, verdict, probability, verification flag, timestamp, and internal row ID; it does not store the submitted review text or reviewer/product IDs. The public history API also omits these fields.

Existing database rows from before this change are not rewritten automatically. Their text and IDs remain in the SQLite file, although the public history endpoint no longer returns them. Back up the database before choosing whether to purge those older fields.
