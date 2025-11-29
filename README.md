# Healthcare Misinformation Detector

A sophisticated, agentic AI system designed to detect, analyze, and verify healthcare misinformation across text, images, and video content.

## 🚀 Overview

This system uses a graph of specialized AI agents (orchestrated by **LangGraph**) to process content from news articles, tweets, and video URLs. It extracts claims, cross-references them with trusted medical sources, and provides a detailed verification report.

## ✨ Key Features

*   **Multi-Agent Architecture**: Decomposes complex verification into atomic steps (Extraction, Canonicalization, Retrieval, Verification).
*   **Multimodal Analysis**:
    *   **Text**: NLP-based claim extraction and verification.
    *   **Images**: Uses a local Vision Language Model (**Moondream2**) to analyze medical diagrams, memes, and charts.
    *   **Video**: Downloads and transcribes YouTube videos using **yt-dlp** and **OpenAI Whisper** (local) for analysis.
*   **Trend Analysis**: Identifies recurring misinformation narratives using **TF-IDF** and **K-Means clustering**.
*   **Local & Cloud Hybrid**:
    *   **Cloud**: Groq API (Llama 3) for high-speed reasoning and explanation.
    *   **Local**: Moondream2 (Vision) and Whisper (Audio) run locally for privacy and cost efficiency.
*   **Storage Optimization**: Automatic retention policies to clean up old data and temporary files.

## 🏗️ System Architecture

The system follows a directed acyclic graph (DAG) workflow:

1.  **Ingestion**: Scrapers (BBC, CNN, Twitter, etc.) or Manual Input (Text/URL).
2.  **Video Processor**: (If Video) Downloads audio and transcribes text.
3.  **Claim Extraction**: Identifies atomic healthcare claims from the content.
4.  **VLM Analysis**: (If Images) Describes images and extracts visual claims.
5.  **Canonicalization**: Deduplicates claims using vector embeddings (ChromaDB) to map them to known narratives.
6.  **Evidence Retrieval**: Searches trusted sources (PubMed, CDC, Web) for verification evidence.
7.  **Verification**: Compares claims against evidence to determine truthfulness (True/False/Unverified).
8.  **Explainer**: Generates a final, user-friendly report summarizing the findings.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, SQLAlchemy (Async)
*   **Orchestration**: LangGraph, LangChain
*   **Database**: PostgreSQL (Metadata), ChromaDB (Vector Store)
*   **AI Models**:
    *   LLM: `openai/gpt-oss-120b` (via Groq)
    *   Vision: `vikhyatk/moondream2` (Hugging Face Transformers)
    *   Audio: `openai-whisper` (Base model)
*   **Tools**: `uv` (Package Manager), `yt-dlp`, `ffmpeg`

## 📦 Setup & Installation

### Prerequisites
*   Python 3.10+
*   `uv` (recommended) or `pip`
*   `ffmpeg` (installed and in system PATH for video processing)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd truelen
    ```

2.  **Install dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file in the root directory:
    ```env
    DATABASE_URL=sqlite+aiosqlite:///./truelen.db
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Initialize Database**:
    The database tables are automatically created on startup.

### Running the Application

Start the development server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## 🖥️ Usage

### Web Interface
Open `http://localhost:8000/static/index.html` in your browser.

*   **Trigger Scan**: Scrapes configured news sources for latest healthcare articles.
*   **Manual Analysis**: Paste text or a YouTube URL to analyze specific content.
*   **Trending Misinformation**: View clusters of recurring false claims.
*   **Analysis Report**: View detailed breakdown of claims, evidence, and image/video analysis.

### API Endpoints

*   `POST /api/trigger-scan`: Start the scraping process.
*   `GET /api/articles`: List scraped articles.
*   `POST /api/analyze/{id}`: Analyze a specific article by ID.
*   `POST /api/analyze-text`: Analyze raw text or a video URL.
*   `GET /api/trends`: Get current misinformation trends.

## 🤝 Contributing
1.  Fork the repo.
2.  Create a feature branch.
3.  Submit a Pull Request.

## 📄 License
MIT
