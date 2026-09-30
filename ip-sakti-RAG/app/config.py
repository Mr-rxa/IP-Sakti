from pathlib import Path
import os

from dotenv import load_dotenv


APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
DATA_DIR = BASE_DIR / "data"
CORPUS_PATH = DATA_DIR / "corpus" / "corpus.json"
CHROMA_DIR = DATA_DIR / "vector_store" / "chroma"
BM25_PATH = DATA_DIR / "vector_store" / "bm25_index.pkl"
CONFIDENCE_MODEL_PATH = DATA_DIR / "confidence_model.pkl"
DEFAULT_SOURCE_DIR = BASE_DIR.parent / "Corpus Research" / "My Notes"

load_dotenv(BASE_DIR / ".env")
load_dotenv(APP_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"
)
CORPUS_ONLY = os.getenv("IP_SAKTI_CORPUS_ONLY", "on").strip().lower() not in {
    "0",
    "false",
    "no",
    "off",
}
MIN_RETRIEVAL_RESULTS = max(1, int(os.getenv("IP_SAKTI_MIN_RETRIEVAL_RESULTS", "1")))

# Pinecone Vector DB Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "ip-sakti-corpus")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
ENABLE_PINECONE = bool(PINECONE_API_KEY)

_dense_setting = os.getenv("IP_SAKTI_ENABLE_DENSE", "auto").strip().lower()
ENABLE_DENSE = _dense_setting not in {"0", "false", "no", "off"} and bool(
    GEMINI_API_KEY
)

_llm_setting = os.getenv("IP_SAKTI_ENABLE_LLM", "auto").strip().lower()
ENABLE_LLM = _llm_setting not in {"0", "false", "no", "off"} and bool(GEMINI_API_KEY)


def normalize_jurisdiction(jurisdiction: str | None) -> str:
    value = (jurisdiction or "India").strip().lower()
    if value in {"india", "indian", "national"}:
        return "India"
    if value in {"international", "intl", "global"}:
        return "International"
    raise ValueError("jurisdiction must be 'India' or 'International'")
