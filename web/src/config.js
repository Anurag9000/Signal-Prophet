// Load API URL from environment variable (Vite injects this at build time)
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
