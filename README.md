# Supply Chain Optimization with Knowledge Graphs and RAG

An end-to-end system for answering complex supply chain questions using semantic search and language models. Takes structured logistics data, builds a knowledge graph, and uses RAG to generate actionable recommendations from retrieved context.

## What This Does

The project addresses a real problem: supply chain data lives in silos, making it hard to answer operational questions quickly. This system bridges that gap.

Given a question like "Which suppliers have a lead time over 20 days and low reliability?", the pipeline:
1. Converts the question into a semantic embedding
2. Searches a ChromaDB index for relevant supplier facts
3. Passes the retrieved context to an LLM
4. Returns a structured recommendation with reasoning and sources

The entire process runs in under 1 second.

## Architecture

The system flows through five stages:

**Stage 1: Data Generation** - Synthetic supply chain dataset with suppliers, warehouses, routes, orders, and performance metrics.

**Stage 2: Knowledge Graph** - Converts structured data into RDF triples (Turtle format). Entities include suppliers with lead times, reliability scores, contract types, and risk ratings. Relationships capture business logic.

**Stage 3: NLP Export** - Converts triples into natural language sentences. "Supplier 1 has lead time 28 days and on-time delivery rate of 94%." This is necessary for LLMs to understand the facts contextually.

**Stage 4: Semantic Embeddings** - Fine-tunes a pre-trained model on 200 supply chain Q&A pairs. Produces 384-dimensional vectors that cluster similar queries and facts together.

**Stage 5: RAG Pipeline** - Retrieves top-5 relevant facts from ChromaDB, formats them as context, and sends to Llama 3.2 via Groq API. Tested four prompt strategies to optimize output quality.

## Technology Choices

- **RDFlib** - Standard for semantic web. Allows us to model relationships, not just attributes.
- **SentenceTransformers** - Lightweight (80MB), 384 dimensions sufficient for supply chain domain, can be fine-tuned.
- **ChromaDB** - Vector database with HNSW indexing. Sub-millisecond retrieval at scale.
- **Groq** - Free tier with fast Llama 3.2 inference. Good for iterating on prompts without cost.
- **LangChain** - Simplifies RAG orchestration and prompt templating.

## Key Results

**Export Quality**: 1,426 natural language sentences from 400+ RDF triples. Each sentence is semantically coherent and parseable by the LLM.

**Retrieval Performance**: Queries consistently retrieve supplier facts matching the question intent. Cosine similarity on fine-tuned embeddings captures domain semantics well.

**Prompt Engineering**: Tested four strategies. The optimised prompt (role clarity + structured output + step-by-step reasoning + guardrails) outperformed zero-shot by 40% on actionability and specificity.

**Latency**: End-to-end processing runs in 0.3-0.8 seconds. Bottleneck is LLM API latency, not retrieval.

## About the Notebooks

1. **01_01_generate_synthetic_data.ipynb** - Creates realistic supply chain dataset (suppliers, warehouses, routes, orders).

2. **01_02_create_knowledge_graph.ipynb** - Builds RDF graph with 9 supplier performance metrics.

3. **01_03_visualize_knowledge_graph.ipynb** - Interactive graph visualization. Helps verify data quality.

4. **01_04_export_kg_triples_as_text.ipynb** - Converts triples to natural language. Critical step for LLM comprehension.

5. **02_01_embeddings_finetuning.ipynb** - Fine-tunes SentenceTransformers on domain Q&A pairs.

6. **02_02_chromadb_semantic_search.ipynb** - Builds ChromaDB index. Tests retrieval accuracy.

7. **03_01_rag_pipeline_core.ipynb** - Implements core RAG logic. Connects embeddings to LLM.

8. **03_02_prompt_engineering.ipynb** - Compares four prompt strategies on a benchmark query.



## Trade-offs

The current approach is straightforward but has limitations:

- **Synthetic data** - Unrealistic patterns. Real supply chain data has long-tail distributions and rare events.
- **Single-hop retrieval** - Works for point questions but struggles with complex multi-step logic.
- **Fine-tuned embeddings** - Small training set (200 pairs). More data would improve performance.
- **Static KG** - Updates require re-running the pipeline. Real systems need incremental updates.

These are acceptable for a proof-of-concept. Production would require rethinking some of these.

## Dependencies

Key packages:
- rdflib==6.0.0 - RDF graph operations
- sentence-transformers==2.2.2 - Embeddings
- chromadb>=1.5.9 - Vector database (pin will auto-upgrade when CVE fix is published to PyPI)
- langchain==0.1.0 - RAG orchestration
- langchain-groq - Groq LLM integration
- torch - ML compute

See requirements.txt for the full list.
| **RAG Framework** | LangChain | Prompt templates & orchestration |
| **Fine-tuning** | PyTorch + MultipleNegativesRankingLoss | Domain adaptation on supply chain pairs |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (free tier: https://console.groq.com)
- 2GB RAM minimum, 4GB+ recommended

### Installation

```bash
# Clone repository
git clone https://github.com/maheshmic88/supply-chain-optimization-kg.git
cd supply-chain-optimization-kg

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure nbstripout to auto-strip notebook outputs on commit
# This keeps the repo clean by not committing cell outputs and execution counts
nbstripout --install --attributes .gitattributes
```

### Environment Setup

```bash
# Copy .env.example to .env and add your actual Groq API key
cp .env.example .env

# Then edit .env and replace gsk_YOUR_KEY_HERE with your actual key from https://console.groq.com
# For example: GROQ_API_KEY=gsk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5
```

**Important:** If you skip this step, the notebooks will prompt you to enter your Groq API key interactively when needed.

### Running the Notebooks

Execute notebooks **in order** (each builds on outputs from the previous):

1. **01_01_generate_synthetic_data.ipynb** - Creates `data/raw/*.csv` (suppliers, products, orders, etc.)
2. **01_02_create_knowledge_graph.ipynb** - Reads CSVs, outputs `data/processed/supplychain_kg.ttl` (RDF graph)
3. **01_03_visualize_knowledge_graph.ipynb** - Visualizes the graph (optional, for exploration)
4. **01_04_export_kg_triples_as_text.ipynb** - Converts RDF triples to `data/processed/supplychain_kg_text.txt`
5. **02_01_embeddings_finetuning.ipynb** - Reads the text file, outputs fine-tuned embeddings to `data/models/` and `data/outputs/`
6. **02_02_chromadb_semantic_search.ipynb** - Indexes embeddings in ChromaDB (optional, tested separately)
7. **03_01_rag_pipeline_core.ipynb** - Implements RAG orchestration (requires all above + Groq API key)
8. **03_02_prompt_engineering.ipynb** - Compares 4 prompt strategies on benchmark query
9. **03_03_rag_business_queries.ipynb** - Demonstrates 5 realistic supply chain queries
10. **04_01_llmops_responsible_ai.ipynb** - MLflow experiment tracking + hallucination guardrail

**Start here:** Run 01_01 → 01_02 → 01_04 → 02_01 → 03_01 as the **minimum viable pipeline**. Other notebooks are optional refinements.

## Configuration

Edit `config.py` to customize:

```python
DATA_DIR = Path(__file__).parent / "data"              # Data directory
GROQ_MODEL_NAME = "llama-3.2-70b-versatile"           # LLM model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"                  # Embedding model
COLLECTION_NAME = "supply_chain_kg"                   # ChromaDB collection
N_RESULTS_DEFAULT = 5                                 # Retrieval top-K
```

---

## Project Structure

```
supply-chain-optimization-kg/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                          # Project configuration
├── .env.example                       # API key template (copy to .env)
├── .gitignore                         # Git configuration
├── .gitattributes                     # Auto-strip notebook outputs on commit
│
├── notebooks/                         # Jupyter notebooks (main workflow)
│   ├── 01_01_generate_synthetic_data.ipynb        # Create sample supply chain data
│   ├── 01_02_create_knowledge_graph.ipynb         # Build RDF KG from structured data
│   ├── 01_03_visualize_knowledge_graph.ipynb      # Interactive graph visualization
│   ├── 01_04_export_kg_triples_as_text.ipynb      # Convert RDF triples → NL sentences
│   ├── 02_01_embeddings_finetuning.ipynb          # Fine-tune domain embeddings
│   ├── 02_02_chromadb_semantic_search.ipynb       # Index embeddings & test retrieval
│   ├── 03_01_rag_pipeline_core.ipynb              # Core RAG orchestration
│   ├── 03_02_prompt_engineering.ipynb             # Compare 4 prompt strategies
│   ├── 03_03_rag_business_queries.ipynb           # 5 real-world supply chain queries
│   └── 04_01_llmops_responsible_ai.ipynb          # MLflow tracking + AI guardrails
│
├── data/
│   ├── raw/                           # Synthetic CSVs (suppliers, warehouses, orders, etc.)
│   ├── processed/                     # Generated artifacts
│   │   ├── supplychain_kg.ttl         # RDF knowledge graph (Turtle format)
│   │   └── supplychain_kg_text.txt    # NL-exported sentences (1,426 lines)
│   ├── models/
│   │   └── fine_tuned_embedder/       # Fine-tuned SentenceTransformer (auto-generated)
│   └── outputs/                       # Embeddings, RAG results, visualizations (auto-generated)
│
└── tests/                             # Unit tests
```

---

## Key Features

### 1. Knowledge Graph
- **Entities**: Suppliers, Warehouses, Routes, Orders, Materials
- **Properties**: Lead time, reliability score, on-time delivery rate, risk rating, capacity tier, exposure score
- **Format**: Turtle RDF for semantic reasoning

### 2. Fine-tuned Embeddings
- **Base Model**: `all-MiniLM-L6-v2` (384 dimensions, ~80 MB)
- **Training Data**: 200 supply chain Q&A pairs
- **Loss**: MultipleNegativesRankingLoss for contrastive learning
- **Outcome**: Domain-specific semantic search that understands supply chain terminology

### 3. Semantic Search
- **Index**: ChromaDB with HNSW (Hierarchical Navigable Small World)
- **Similarity**: Cosine distance on fine-tuned embeddings
- **Query Example**: "Which suppliers have lead time over 20 days?" → 5 contextual chunks in <100ms

### 4. RAG Pipeline
- **Retrieval**: Top-5 semantic chunks from ChromaDB
- **Prompt Strategies**: 
  - Zero-shot (baseline)
  - Few-shot (with examples)
  - Chain-of-Thought (step-by-step reasoning)
  - Optimised (role + format + CoT + guardrails) ← **Recommended**
- **LLM Output**: Structured findings, recommended actions, confidence scores


---

## What I'd Change Next

If I were extending this, I'd focus on:

- **Real data integration** - Replace synthetic data with actual ERP/WMS feeds
- **Multi-hop reasoning** - Answer questions like "If Supplier X is delayed, which warehouses are affected?" requires traversing the graph
- **Confidence scoring** - Don't just say the LLM is confident; quantify it with retrieval scores and reasoning traces
- **API layer** - Wrap the pipeline in a REST API for production use
- **Monitoring** - Track retrieval precision, LLM latency, and user satisfaction over time


## License

This project is open-source. Feel free to use, modify, and distribute as needed.

---
