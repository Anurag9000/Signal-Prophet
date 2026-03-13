// API URL is injected at build time via VITE_API_URL.
const rawApiUrl = import.meta.env.VITE_API_URL;

if (!rawApiUrl) {
  console.warn(
    '[Signal-Prophet] VITE_API_URL is not set. ' +
    'Set VITE_API_URL in your environment or web/.env.local before running the app.'
  );
}

export const API_URL = rawApiUrl ?? '';
