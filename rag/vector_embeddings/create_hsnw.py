import os
import json
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

CHUNK_JSON_PATH = "/chunk_data_content_cleaned.json"
EMBEDDING_MODEL = "BAAI/bge-m3"
USE_FIELD = "content"
SAVE_DIR = "./"

EMBED_SAVE_PATH = os.path.join(SAVE_DIR, "embeddings.npy")
META_SAVE_PATH = os.path.join(SAVE_DIR, "metadata.json")
FAISS_SAVE_PATH = os.path.join(SAVE_DIR, "faiss_hnsw.index")

os.makedirs(SAVE_DIR, exist_ok=True)

with open(CHUNK_JSON_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [chunk[USE_FIELD] for chunk in chunks]
metadata = [
    {
        "chunk_id": chunk["chunk_id"],
        "source": chunk["source"],
        "content": chunk["content"],
        "description": chunk["description"]
    }
    for chunk in chunks
]

print(f"使用嵌入模型: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

print(f"生成 {len(texts)} 条嵌入...")
vectors = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
).astype("float32")

print(f"向量维度: {vectors.shape[1]}")

np.save(EMBED_SAVE_PATH, vectors)
with open(META_SAVE_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"向量保存至: {EMBED_SAVE_PATH}")
print(f"元数据保存至: {META_SAVE_PATH}")

print("构建 FAISS HNSW 索引...")
dim = vectors.shape[1]
M = 32  # 每个点的邻接边数量
index = faiss.IndexHNSWFlat(dim, M)
index.hnsw.efConstruction = 200  # 构图参数
index.hnsw.efSearch = 64         # 查询时使用的邻居数量
index.add(vectors)
faiss.write_index(index, FAISS_SAVE_PATH)
print(f"HNSW 索引已保存至: {FAISS_SAVE_PATH}")
