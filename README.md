# Timeline Reporter

An AI-powered news automation system.

## Overview

Timeline Reporter automates the entire journalism workflow from discovery to distribution. The system identifies breaking stories, eliminates duplicates, prioritizes based on impact, conducts research, writes professional articles, and generates audio podcasts.

## Key Features

### 🔍 **Intelligent Lead Discovery**

- Automated scanning of multiple news sources
- Real-time identification of breaking stories
- Category-based news monitoring
- Configurable source prioritization

### 🔄 **Smart Deduplication**

- Vector similarity matching using Pinecone
- Eliminates duplicate stories across sources
- Preserves unique angles and perspectives
- Configurable similarity thresholds

### ⚖️ **AI-Powered Curation**

- Multi-criteria impact assessment
- Priority scoring based on newsworthiness
- Automated editorial decision making
- Customizable evaluation parameters

### 📚 **Comprehensive Research**

- Automated fact-checking and verification
- Source attribution and citation
- Context gathering from multiple references
- Real-time information enhancement

### ✍️ **Professional Writing**

- Publication-ready story generation
- Consistent editorial style and tone
- Proper headline and summary creation
- SEO-optimized content structure

### 🎙️ **Audio Generation**

- Automated podcast creation
- Natural voice synthesis
- Multi-story news briefings
- Cloudflare R2 storage integration

### 💾 **Reliable Persistence**

- MongoDB-based story storage
- Full metadata and source tracking
- Historical archive capabilities
- Query and retrieval APIs

## Technology Stack

- **Python 3.13** - Core runtime environment
- **OpenAI GPT** - Content generation and evaluation
- **Perplexity AI** - Research and discovery
- **Pinecone** - Vector similarity and deduplication
- **MongoDB** - Document storage and persistence
- **Cloudflare R2** - Audio file hosting
- **Poetry** - Dependency management
- **pytest** - Comprehensive testing framework

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry package manager
- Active API keys for required services

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/florian-lup/timeline-reporter
   cd timeline-reporter
   ```

2. **Install dependencies**

   ```bash
   poetry install
   ```

## Usage

### Running the Complete Pipeline

Execute the full 7-step automated pipeline:

```bash
poetry run python main.py
```

### Pipeline Steps

The system executes the following sequence:

1. **Discovery** - Scans news sources for breaking stories
2. **Deduplication** - Removes duplicate content using vector similarity
3. **Curation** - Evaluates and prioritizes leads by impact
4. **Research** - Gathers context and verifies information
5. **Writing** - Generates publication-ready stories
6. **Audio** - Creates podcast episodes from stories
7. **Storage** - Persists content to MongoDB

## Testing

Run the comprehensive test suite:

```bash
# All tests
poetry run pytest

# Coverage report
poetry run pytest --cov

# Integration tests only
poetry run pytest tests/test_integration.py
```

### Test Categories

- **Unit Tests** - Individual component validation
- **Integration Tests** - Service interaction verification
- **Client Tests** - External API connection testing
- **End-to-End Tests** - Complete pipeline validation

## Development

### Code Quality

The project enforces strict code quality standards:

```bash
# Linting and formatting
poetry run ruff check
poetry run ruff format

# Type checking
poetry run mypy

# All quality checks
poetry run python lint.py
```

## License

Proprietary - All rights reserved

---

**Timeline Reporter** - Automating journalism with AI precision.
