import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


def get_documents_dir() -> Path:
    docs_dir = Path.home() / "Documents" / "AI Handson"
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir


def list_pdfs_in_documents_dir() -> list[str]:
    docs_dir = get_documents_dir()
    return sorted(str(p.name) for p in docs_dir.glob("*.pdf"))


def build_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )


def generate_response(user_message: str) -> str:
    llm = build_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant who explains things clearly."),
        ("human", "{question}"),
    ])
    chain = prompt | llm

    result = chain.invoke({"question": user_message})
    return result.content


def extract_pdf_text(pdf_path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def analyze_requirements(requirements_text: str) -> str:
    llm = build_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior solution architect. Read the supplied requirement document and return valid JSON only, with no markdown fences and no extra commentary. Use exactly these keys: summary, inferred_app_type, key_features, recommended_stack, integrations, deployment_plan. Rules: summary is a short string; inferred_app_type is a string; key_features, integrations, and deployment_plan are arrays of short strings; recommended_stack is an array of short strings like ['Python', 'FastAPI', 'SQLite']; if a value is not clearly known, use an empty array or a short descriptive string.",
        ),
        ("human", "Analyze the following requirement document and produce a structured response:\n\n{requirements}"),
    ])
    chain = prompt | llm

    result = chain.invoke({"requirements": requirements_text})
    return result.content


def analyze_pdf_file(pdf_path: str) -> str:
    requirements_text = extract_pdf_text(pdf_path)
    return analyze_requirements(requirements_text)


if __name__ == "__main__":
    import sys

    user_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How are you doing today?"
    print(generate_response(user_message))
