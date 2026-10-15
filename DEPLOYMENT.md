# Deployment Guide

## Local deployment

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Render deployment

1. Push this project to GitHub.
2. Create a new Render Web Service.
3. Choose the repository.
4. Use the following start command:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

5. Add environment variables from `.env.example` as needed.
6. Deploy.

## Railway deployment

1. Push to GitHub.
2. Create a Railway project.
3. Import the repository.
4. Set the startup command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

5. Add environment variables.

## Public sharing

For investor feedback or friend sharing, use a public-facing deployment option and keep the demo simple:

- one document upload
- a generated summary
- a client-ready proposal
- one demo dashboard

## Important note

This app is a prototype and should be deployed as a lightweight demo service, not a production-grade multi-tenant platform.
