# AI Handson

A lightweight AI-powered workflow that turns a requirement document into an MVP direction, product summary, and client-ready proposal.

## Business idea

Teams often receive PDFs, specs, or rough requirement documents that are full of business context but not ready for implementation. This project helps convert those documents into:

- a concise business summary
- an inferred app type
- a feature list
- a recommended stack
- integration ideas
- deployment guidance
- an operational demo dashboard

This makes the tool useful for founders, consultants, internal product teams, and client-facing solution work.

## Why this matters

Instead of manually reading dense documents and creating a product plan from scratch, the system provides a fast starting point. It reduces discovery time and turns ambiguous input into a usable MVP conversation.

## Product flow

1. Upload a requirement PDF.
2. Extract text from the document.
3. Ask the LLM to infer business intent and app type.
4. Generate structured output.
5. Present the result in a proposal page and demo dashboard.

## Stack

- Python
- FastAPI
- LangChain
- OpenAI / OpenRouter / Ollama
- PyPDF
- HTML + JavaScript

## Project structure

- `main.py` — FastAPI app, UI routes, and business demo pages
- `app.py` — LLM orchestration and PDF analysis helpers
- `tests/test_app.py` — regression checks
- `.env.example` — environment configuration template

## Quick start

1. Create a virtual environment:

   python3 -m venv .venv
   source .venv/bin/activate

2. Install dependencies:

   pip install -r requirements.txt

3. Copy the environment file and set values:

   cp .env.example .env

4. Start Ollama locally or configure OpenAI/OpenRouter credentials.

5. Run the app:

   uvicorn main:app --host 0.0.0.0 --port 8000

6. Open:

   - http://localhost:8000/
   - http://localhost:8000/proposal
   - http://localhost:8000/mvp

## Local model option

This project supports Ollama with a free local model flow. It is the best default for learning, prototyping, and low-cost demos.

Example:

- LLM_PROVIDER=ollama
- OLLAMA_MODEL=llama3.2

## Paid provider option

You can also use OpenAI or OpenRouter:

- set `LLM_PROVIDER=openai` or `LLM_PROVIDER=openrouter`
- add the matching API key and model

## Demo login

For the MVP page:

- Email: ops@demo.com
- Password: demo123

## Investor summary

This project is positioned as a lightweight AI workflow for turning raw business requirements into MVP-ready direction and client-facing proposals. It is intentionally simple, fast to demo, and easy to extend.

## License

This project is provided for learning and prototyping purposes.
