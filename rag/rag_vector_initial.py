import json
import numpy as np
import os
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from zhipuai import ZhipuAI
from utils.api import api_key
from functools import lru_cache

MAX_HISTORY_TURNS = 3
MAX_SENTENCES = 3
TOP_K = 10
FINAL_K = 3

class VectorRAGPipeline:
    def __init__(self):
        self.embedding_model = SentenceTransformer("BAAI/bge-m3")
        self.reranker = CrossEncoder("BAAI/bge-reranker-large")
        self.client = ZhipuAI(api_key=api_key)

        vec_dir = os.path.join(os.path.dirname(__file__), "vector_embeddings")

        self.index = faiss.read_index(os.path.join(vec_dir, "faiss_hnsw.index"))
        with open(os.path.join(vec_dir, "metadata.json"), "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def rewrite_query(self, query: str, history: list) -> str:
        history_text = "\n".join([f"User: {t['user']}\nAssistant: {t['assistant']}" for t in history[-MAX_HISTORY_TURNS:]])
        prompt = f"""
You are an intelligent assistant for an industrial semantic search system.
Rewrite the new user query based on the following chat history.

Chat History:
{history_text}

New User Query: {query}

Rewritten Query:
"""
        try:
            res = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=256
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            print("GLM rewrite error:", e)
            return query

    @lru_cache(maxsize=128)
    def encode_text_cached(self, text: str):
        return self.embedding_model.encode([text], normalize_embeddings=True).astype("float32")

    def vector_retrieve(self, query: str, top_k: int = TOP_K) -> list:
        query_vec = self.encode_text_cached(query)
        distances, indices = self.index.search(query_vec, top_k)
        results = []
        for i in indices[0]:
            item = self.metadata[i]
            result = {
                "id": item.get("chunk_id", f"chunk_{i}"),
                "label": "Chunk",
                "chunk_id": item.get("chunk_id", ""),
                "description": item.get("description"),
                "content": item.get("content", ""),
                "source": item.get("source", "")
            }
            results.append(result)
        return results

    def rerank(self, query: str, candidates: list, top_n: int = FINAL_K) -> list:
        pairs = [(query, c.get("description")) for c in candidates]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [item[0] for item in reranked[:top_n]]

    def compress_context(self, text: str, max_sentences: int = MAX_SENTENCES):
        sentences = text.replace("\n", " ").split('.')
        selected = [s.strip() for s in sentences if s.strip()]
        if not selected:
            return text 
        return '. '.join(selected[:max_sentences]) + '.'

    def build_context(self, chunks: list) -> str:
        return "\n\n".join([
            self.compress_context(chunk.get("description", "")) for chunk in chunks
        ])

    def generate_answer(self, context: str, query: str, history: list) -> str:
        context_from_history = "\n".join(
            [f"Previous Question: {t['user']}\nPrevious Answer: {t['assistant']}" for t in history[-MAX_HISTORY_TURNS:]]
        )
        prompt = f"""
{context_from_history}

Based on the following document content, answer the current user question:

{context}

Current User Question: {query}

Please provide a professional, accurate, and concise answer:
"""
        FEWSHOT_EXAMPLES = """
Example 1:
Document: The AM400 uses a 400 W ytterbium fibre laser with a wavelength of approximately 1070 nm.
User question: What type of laser and wavelength does the AM400 use?
Answer: The AM400 uses a 400W ytterbium fiber laser with a wavelength of approximately 1070nm.

Example 2:
Document: Ensure the build chamber is purged with inert gas before initiating the laser melting process.
User question: What needs to be done before starting laser melting?
Answer: The build chamber should be purged with inert gas before initiating the laser melting process.
"""
        full_prompt = FEWSHOT_EXAMPLES + "\n\n" + prompt
        try:
            res = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=512
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"LLM request error: {str(e)}"

    def run(self, user_query: str, history: list) -> tuple:
        rewritten_query = self.rewrite_query(user_query, history)
        candidate_chunks = self.vector_retrieve(rewritten_query, top_k=TOP_K)
        top_chunks = self.rerank(rewritten_query, candidate_chunks, top_n=FINAL_K)
        context = self.build_context(top_chunks)
        answer = self.generate_answer(context, user_query, history)
        sources = [{"source": chunk.get("chunk_id", "unknown"), "description": chunk.get("description", "No description available.")} for chunk in top_chunks]
        return answer, sources

if __name__ == "__main__":
    rag = VectorRAGPipeline()
    conversation_history = []
    while True:
        user_query = input("User: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            break
        answer, sources = rag.run(user_query, conversation_history)
        print("Answer:\n", answer)
        print("Sources Used:")
        for i, s in enumerate(sources, 1):
            print(f"[{i}] {s['source']}: {s['content']}")
        conversation_history.append({"user": user_query, "assistant": answer})
