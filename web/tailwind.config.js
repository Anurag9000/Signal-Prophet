/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                academic: {
                    50: '#f8f9fa',
                    100: '#e9ecef',
                    800: '#343a40',
                    900: '#212529',
                },
                brand: {
                    blue: '#007bff',
                    indigo: '#6610f2',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                serif: ['Merriweather', 'serif'],
                mono: ['Fira Code', 'monospace'],
            }
        },
    },
    plugins: [],
}
