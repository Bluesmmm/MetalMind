# MetalMind: A Knowledge Graph + RAG System for Metal AM

MetalMind is a human-centric, multimodal knowledge system that integrates a large-scale knowledge graph (KG), retrieval-augmented generation (RAG) to support metal additive manufacturing (AM) training and decision-making. 

---

## 🔧 Features

- 📄 **PDF-to-Knowledge Graph**: Converts metal AM manuals into structured knowledge using GLM-4V-9B.
- 🧠 **Entity & Relation Extraction**: GLM-4V-9B-based pipeline for schema-free ➝ schema-based KG creation.
- 🔗 **Neo4j Graph Storage**: All nodes and relationships stored in a traversable graph database.
- 🔍 **Three-Mode Retrieval System**:
  - **Vector Retrieval** using FAISS and entity embeddings
  - **Graph Traversal Retrieval** via Neo4j
  - **Hybrid Retrieval** combining both
- 🖼️ **Image Retrieval via CLIP + LoRA**: Fine-tuned CLIP model with figure captions, enhancing diagram-based explanation and multimodal reasoning.
- 📊 **Evaluation Metrics**: Support for faithfulness, answer precision, rubric scores, and token-efficiency tracking.
- 🌐 **Streamlit Web App**: Visual interactive front-end for testing text/image queries.

---

## 📁 Project Structure

```bash
.
├── preprocess.py              # PDF to markdown + chunking
├── build_kg_neo4j.py          # GLM-4V-9B-based KG construction, writes to Neo4j
├── postprocess.py             # Entity cleanup, deduplication
├── neo4j_handler.py           # Neo4j API abstraction
├── rag_vector.py              # Vector-based retrieval
├── rag_graph.py               # Graph-based retrieval
├── rag_hybrid.py              # Combined hybrid mode
├── clip_lora_train.py         # Train LoRA on CLIP with figure captions
├── clip_lora_infer.py         # Use LoRA-CLIP to retrieve images
├── evaluate.py                # Retrieval evaluation script
├── app.py                     # Streamlit app
├── full_pipeline.py           # Optional: run all modules in sequence
└── README.md
```

---

## 🚀 Getting Started

### 1. Setup Environment
```bash
conda create -n metalmind python=3.10
conda activate metalmind
pip install -r requirements.txt
```

### 2. Prepare Data
- Place your machine manual PDF in the root directory (e.g., `AM400.pdf`)
- Prepare a CSV file `extracted_figures_with_paths.csv` with columns:
  - `Local Image Path`
  - `Caption`

### 3. Run Pipeline
```bash
python preprocess.py
python build_kg_neo4j.py
python postprocess.py
```

### 4. Train LoRA-enhanced CLIP
```bash
python clip_lora_train.py
```

### 5. Launch Web App
```bash
streamlit run app.py
```

---

## 🤖 Using GLM-4V-9B
This project relies on [`THUDM/glm-4v-9b`](https://huggingface.co/collections/THUDM/glm-4-665fcf188c414b03c2f7e3b7) for all natural language and multimodal tasks. You can:

- Use it via HuggingFace Transformers (`transformers>=4.44`)
- Deploy locally or call through OpenBMB, InternLM or ChatGLM API-compatible services
- Supports both caption generation and instruction-style prompting for entity-relation extraction

---

## 🧪 Evaluation
```bash
python evaluate.py
```
Customize the metrics and query list in the script.

---

## 📚 Requirements
- Python 3.10+
- Neo4j
- FAISS
- HuggingFace Transformers (GLM-4V-9B)
- PyMuPDF
- sentence-transformers
- peft, bitsandbytes
- Streamlit, scikit-learn, pandas, tqdm

---

## 📌 Citation & Acknowledgement
- GLM-4V-9B: [https://huggingface.co/collections/THUDM/glm-4](https://huggingface.co/collections/THUDM/glm-4)
- Inspired by Fan et al. (2025): "MetalMind: A Knowledge Graph-Driven Human-Centric Knowledge System for Metal Additive Manufacturing"

---
