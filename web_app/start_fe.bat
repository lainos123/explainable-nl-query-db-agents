@echo off
:: Run frontend Next.js in port 8000
start cmd /k "cd frontend && npm run dev -- -p 8000 --turbopack"