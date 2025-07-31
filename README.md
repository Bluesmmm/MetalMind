# 🧠 MetalMind: Multi-Modal RAG System for Metal AM Domain

**MetalMind** 是一个专为金属增材制造（Metal Additive Manufacturing, Metal AM）领域定制的多模态检索增强生成系统，集成了文本、图谱、图像三种模态的信息源，支持面向工业文档的智能问答、图谱可视化、图像检索与多轮对话能力。

本项目支持：
- 文本向量检索（Vector-RAG）
- 知识图谱实体关系扩展（Graph-RAG）
- 图文融合多模态增强（Hybrid-RAG）
- 图像搜索（CLIP+LoRA）
- 图谱自动构建（基于 LLM）
- Streamlit 界面交互

---

## 🧱 项目结构

```
.
├── app.py                         # Streamlit 前端入口
├── rag/
│   ├── rag_vector.py             # 向量检索 RAG 实现
│   ├── rag_graph.py              # 图谱检索 RAG 实现
│   └── rag_hybrid.py             # 多模态融合 RAG 实现
├── clip_lora/
│   ├── clip_lora_train.py       # CLIP + LoRA 图像微调训练
│   ├── clip_lora_infer.py       # 图像检索推理脚本
│   └── vision/                  # 保存模型、index、caption 数据等
├── kg/
│   ├── build_kg_neo4j.py        # 基于 LLM 的图谱抽取与写入 Neo4j
│   └── kg_prompt.txt            # 图谱抽取 Prompt 模板
├── data_for_kg/
│   └── raw/ + chunked md/pdf    # 原始和切分后的 AM 文档
├── utils/
│   └── api.py                   # 存放 API Key（如 ZhipuAI）
├── evaluate.py                  # 模型评估脚本（BLEU、Recall）
├── build_chunk_data.py          # Tokenizer 分块脚本
├── clean_chunk_data.py          # Chunk 内容清洗器
├── vector_embeddings/           # 向量索引与元数据（embeddings.npy + metadata.json）
├── chat_history/                # 保存对话历史
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
# 包括 transformers, faiss, peft, neo4j, streamlit, zhipuai, etc.
```

### 2. 启动前端应用

```bash
streamlit run app.py
```

启动后可选择 Vector / Graph / Hybrid 检索模式，支持多轮对话、图谱可视化、图片展示与历史对话加载。

---

## 📦 模块说明

详见项目结构，每个模块职责清晰，核心功能包括：

| 模块             | 功能说明 |
|------------------|----------|
| `VectorRAG`      | 文本向量召回 + 重排序 |
| `GraphRAG`       | 图谱实体扩展 + 路径追踪 |
| `HybridRAG`      | 向量 + 图谱 + 图像融合 |
| `clip_lora_*`    | 图像向量构建 + 推理 |
| `build_kg_neo4j` | LLM 图谱构建写入 Neo4j |
| `evaluate.py`    | BLEU / Recall 等指标评估 |

---

## 📁 部分数据说明

| 文件 / 文件夹                    | 说明 |
|----------------------------------|------|
| `vector_embeddings/embeddings.npy` | Chunk 文本向量（bge-m3 编码） |
| `vector_embeddings/metadata.json` | Chunk 元信息（source, content, chunk_id） |
| `clip_faiss.index`                | 图像向量索引（CLIP+LoRA） |
| `clip_index_meta.csv`            | 图像与 caption 对应表 |
| `chunk_data_*.json`              | 经过 tokenizer 切分后的文本片段 |
| `chunk_data_content_cleaned.json`| 清洗后的 chunk 数据（用于图谱） |

---

## 🔐 API Key 设置

请在 `utils/api.py` 中添加你的 API Key，例如：

```python
api_key = "YOUR_ZHIPUAI_API_KEY"
```

---

## 📄 License

MIT License. 本项目用于科研、教育与工业问答系统原型验证。

---

## ✨ 致谢

- [THUDM/GLM](https://github.com/THUDM/GLM)
- [BAAI bge](https://huggingface.co/BAAI)
- [ZhipuAI API](https://open.bigmodel.cn/)
- [Neo4j](https://neo4j.com/)
