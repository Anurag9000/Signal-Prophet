# Frontend Configuration

The frontend does not hardcode backend or base-path values.

## Environment

Set these values in your shell or in `web/.env.local`:

- `VITE_API_URL`: Backend origin for API requests.
- `VITE_BASE_PATH`: Optional deployment base path. Defaults to `/`.

## Development

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Vite will print the active local URL when the dev server starts.
