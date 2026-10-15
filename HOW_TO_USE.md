# How to Use

## 1. Set up the app

Create the environment file and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then configure your provider in `.env`:

- use Ollama for local free testing
- or use OpenAI/OpenRouter for cloud access

## 2. Run locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 3. Open the app

Visit these routes in a browser:

- http://localhost:8000/
- http://localhost:8000/proposal
- http://localhost:8000/mvp

## 4. Upload a PDF

On the home page, use the upload box and select a PDF requirement document.

The app will analyze the document and show a structured output.

## 5. Review proposal

The proposal page reads the PDF analysis and presents a business-ready interpretation.

## 6. Use the demo dashboard

The MVP page provides a simple operations dashboard with sample support tickets.

Use the demo credentials:

- Email: ops@demo.com
- Password: demo123

## 7. For investor demos

Keep the message simple:

> We upload a business requirement document and the system turns it into a product direction, feature outline, and working MVP demo.

This keeps the story clear and easy to understand for non-technical stakeholders.
