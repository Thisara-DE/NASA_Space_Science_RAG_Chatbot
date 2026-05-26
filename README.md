# 🚀 NASA Space Science RAG Chatbot

A sophisticated **Retrieval-Augmented Generation (RAG)** chatbot that brings NASA's space science expertise to your fingertips. Built with cutting-edge NLP and retrieval technologies, this chatbot [...]

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B.svg)](https://streamlit.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Keys & Credentials](#api-keys--credentials)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This chatbot leverages **Retrieval-Augmented Generation** to provide accurate, contextually-aware responses about space science. It combines:

- **Web Scraping**: Automatically harvests NASA Space Science articles from [science.nasa.gov](https://science.nasa.gov)
- **Vector Database**: Indexes content using ChromaDB for fast semantic search
- **Synthetic Q&A Generation**: Creates diverse training pairs from NASA articles
- **Hybrid Retrieval**: Combines semantic and keyword-based search for optimal results
- **LLM Intelligence**: Powered by language models to generate natural, coherent responses
- **User-Friendly Interface**: Streamlit-based chat interface for seamless interaction

---

## ✨ Key Features

- 🔍 **Smart Retrieval**: Hybrid search combining ChromaDB embeddings and traditional keyword matching
- 📚 **Continuous Learning**: Automatic web scraping to keep content up-to-date with NASA publications
- 🤖 **Intelligent Responses**: Context-aware answers generated using large language models
- 💾 **Persistent Storage**: Indexed articles stored in ChromaDB for fast retrieval
- 🎨 **Interactive UI**: Clean, intuitive Streamlit chat interface
- 📊 **Synthetic Q&A**: Automatically generates training data from NASA articles
- 🔗 **Source Attribution**: Provides original NASA article links with responses
- ⚡ **Production-Ready**: Built with scalability and reliability in mind

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                    │
│              (Streamlit Chat Interface)              │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────────────────┐  ┌────────▼──────────────┐
│ Query Processing   │  │ Conversation History  │
└───────────┬────────┘  └───────────────────────┘
            │
    ┌───────▼──────────────┐
    │ Hybrid Retrieval     │
    │ • Semantic Search    │
    │ • Keyword Matching   │
    └───────┬──────────────┘
            │
    ┌───────▼──────────────┐
    │  ChromaDB Vector DB  │
    │ (NASA Articles)      │
    └──────────────────────┘
            │
    ┌───────▼──────────────┐
    │  LLM Response Gen    │
    │ (Answer Synthesis)   │
    └──────────────────────┘
            │
    ┌───────▼──────────────┐
    │  Response with       │
    │  Source Attribution  │
    └──────────────────────┘
```

---

## 📦 Prerequisites

Before getting started, ensure you have:

- **Python 3.8** or higher
- **pip** (Python package manager)
- **API Keys**:
  - Groq API key (for LLM capabilities)
  - Internet connection (for scraping NASA content)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Thisara-DE/NASA_Space_Science_RAG_Chatbot.git
cd NASA_Space_Science_RAG_Chatbot
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./data/chroma_db
NASA_ARTICLES_PATH=./data/nasa_articles
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `CHROMA_DB_PATH` | Path to ChromaDB storage | `./data/chroma_db` |
| `NASA_ARTICLES_PATH` | Directory for stored articles | `./data/nasa_articles` |
| `MAX_ARTICLES` | Maximum articles to scrape | `100` |
| `CHUNK_SIZE` | Text chunk size for indexing | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |

### Customization

Edit `config.py` to adjust:
- Retrieval parameters (top-k results, similarity threshold)
- Scraping frequency and depth
- LLM model selection and parameters
- Q&A generation settings

---

## 🚀 Usage

### Running the Chatbot

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### Typical Workflow

1. **Start the Application**: Run the command above
2. **Ask Questions**: Type space science questions in the chat interface
3. **View Responses**: Get context-aware answers with source attribution
4. **Explore Sources**: Click provided links to view original NASA articles

### Example Questions

- "What are the latest discoveries about Mars?"
- "How does the James Webb Space Telescope work?"
- "Tell me about recent solar research"
- "What's new in exoplanet exploration?"

---

## 📂 Project Structure

```
NASA_Space_Science_RAG_Chatbot/
├── app.py                      # Streamlit main application
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── .env.example               # Environment variables template
├── README.md                  # This file
├── LICENSE                    # MIT License
│
├── src/
│   ├── __init__.py
│   ├── scraper.py            # NASA web scraper
│   ├── indexer.py            # ChromaDB indexing logic
│   ├── retriever.py          # Hybrid retrieval system
│   ├── qa_generator.py       # Synthetic Q&A generation
│   └── llm_handler.py        # LLM integration
│
├── data/
│   ├── chroma_db/            # Vector database storage
│   └── nasa_articles/        # Cached NASA articles
│
└── notebooks/
    └── exploration.ipynb     # Analysis and testing notebooks
```

---

## 🧠 How It Works

### 1. **Data Scraping**
- Automatically crawls `science.nasa.gov` for latest articles
- Extracts title, content, images, and metadata
- Stores articles locally for processing

### 2. **Indexing**
- Chunks articles into manageable segments
- Generates embeddings using state-of-the-art models
- Stores embeddings in ChromaDB for efficient retrieval

### 3. **Synthetic Q&A Generation**
- Creates diverse question-answer pairs from article content
- Uses templates and NLP techniques for variety
- Enriches training data for better model performance

### 4. **Query Processing**
- User asks a question through the Streamlit interface
- Query is embedded and compared against indexed articles
- Hybrid retrieval combines semantic and keyword matching

### 5. **Response Generation**
- Retrieved context is fed to an LLM
- LLM generates contextually accurate response
- Original sources are included for verification

---

## 🔑 API Keys & Credentials

### Setting Up Groq API Key

1. Visit [Groq Platform](https://console.groq.com/keys)
2. Create a new API key
3. Copy and paste into your `.env` file or environment variables
4. Never commit API keys to version control!

### Best Practices

- ✅ Use a `.env` file for local development
- ✅ Use environment variables in production
- ✅ Rotate keys regularly
- ❌ Don't hardcode credentials in source files
- ❌ Don't commit `.env` files to version control

---

## 🐛 Troubleshooting

### Common Issues

**Q: "ModuleNotFoundError: No module named 'streamlit'"**
- A: Run `pip install -r requirements.txt` to install dependencies

**Q: "GROQ_API_KEY not found"**
- A: Ensure your `.env` file is properly configured and the key is valid

**Q: "ChromaDB connection error"**
- A: Check that the `CHROMA_DB_PATH` directory exists and is writable

**Q: "Scraper returns empty results"**
- A: Verify internet connection and NASA website is accessible. Check scraper logs for details.

**Q: "Response quality is poor"**
- A: Rebuild the vector database (`indexer.py`), increase `CHUNK_OVERLAP`, or use a larger LLM model

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request with a clear description

### Development Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- **Issues**: Report bugs or feature requests on [GitHub Issues](https://github.com/Thisara-DE/NASA_Space_Science_RAG_Chatbot/issues)
- **Author**: [Thisara-DE](https://github.com/Thisara-DE)
- **Repository**: [NASA_Space_Science_RAG_Chatbot](https://github.com/Thisara-DE/NASA_Space_Science_RAG_Chatbot)

---

## 🌟 Acknowledgments

- **NASA** for providing excellent space science content at [science.nasa.gov](https://science.nasa.gov)
- **ChromaDB** for vector database capabilities
- **Streamlit** for the web framework
- **Groq** for powerful language models

---

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced conversation context management
- [ ] Integration with additional NASA data sources
- [ ] Custom model fine-tuning
- [ ] Analytics dashboard
- [ ] User feedback loop for continuous improvement
- [ ] Docker containerization
- [ ] Cloud deployment templates

---

**Happy exploring the cosmos! 🌌**
