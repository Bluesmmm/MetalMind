from typing import List, Dict, Tuple
import numpy as np
import json
import os
from sentence_transformers import CrossEncoder
from neo4j import GraphDatabase
from zhipuai import ZhipuAI
from utils.api import api_key

from transformers import CLIPProcessor, CLIPModel
from peft import PeftModel
import torch
import faiss
import pandas as pd

from rag.rag_vector import VectorRAGPipeline

MAX_HISTORY_TURNS = 3

class HybridRAGPipeline:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                 clip_model_dir="clip_lora/vision/models/clip", lora_dir=None, faiss_path=None, meta_csv=None, device="cuda"):
        self.reranker = CrossEncoder("BAAI/bge-reranker-large")
        self.client = ZhipuAI(api_key=api_key)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.chunk_embeddings = self.load_chunk_embeddings()
        self.chunk_nodes = self.load_chunk_nodes()

        self.device = device if torch.cuda.is_available() else "cpu"
        self.processor = CLIPProcessor.from_pretrained(clip_model_dir, local_files_only=True)
        self.clip_model = CLIPModel.from_pretrained(clip_model_dir).to(self.device)
        if lora_dir:
            self.clip_model = PeftModel.from_pretrained(self.clip_model, lora_dir)
        self.clip_model.eval()

        if faiss_path and meta_csv:
            self.faiss_index = faiss.read_index(faiss_path)
            self.clip_meta = pd.read_csv(meta_csv)

        self.vector_pipeline = VectorRAGPipeline()

    def load_chunk_embeddings(self) -> np.ndarray:
        path = os.path.join(os.path.dirname(__file__), "vector_embeddings", "embeddings.npy")
        return np.load(path)

    def load_chunk_nodes(self) -> List[Dict]:
        path = os.path.join(os.path.dirname(__file__), "vector_embeddings", "metadata.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def rewrite_query(self, query: str, history: List[Dict]) -> str:
        return self.vector_pipeline.rewrite_query(query, history)

    def vector_retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        return self.vector_pipeline.vector_retrieve(query, top_k=top_k)

    def fetch_entities(self, chunk_ids: List[str], max_hops: int = 2) -> List[Dict]:
        chunk_ids_str = ', '.join(f'"{cid}"' for cid in chunk_ids)
        query = f"""
        MATCH (c:Chunk)
        WHERE c.chunk_id IN [{chunk_ids_str}]
        MATCH (c)-[:RELATION*1..{max_hops}]-(e)
        WHERE NONE(lbl IN labels(e) WHERE lbl IN ["Chunk", "Document"])
        RETURN DISTINCT elementId(e) AS id, head(labels(e)) AS label, e.description AS description
        """
        with self.driver.session() as session:
            return [{
                "id": record["id"],
                "label": record.get("label", "Unknown"),
                "description": record.get("description", "")
            } for record in session.run(query)]

    def fetch_paths_for_entity(self, chunk_ids: List[str], entity_id: str, max_hops: int = 2, limit: int = 5) -> List[Dict]:
        chunk_ids_str = ', '.join(f'"{cid}"' for cid in chunk_ids)

        query = f"""
        MATCH (c:Chunk)
        WHERE c.chunk_id IN [{chunk_ids_str}]
        WITH c
        MATCH (e)
        WHERE elementId(e) = "{entity_id}"
        WITH c, e
        MATCH path = (c)-[:RELATION*1..{max_hops}]-(e)
        RETURN nodes(path) AS path_nodes, relationships(path) AS path_rels
        LIMIT {limit}
        """

        paths = []
        with self.driver.session() as session:
            result = session.run(query)

            for record in result:
                path_nodes = []
                for n in record["path_nodes"]:
                    if "chunk_id" in n:
                        node_id = n["chunk_id"]
                    elif "id" in n:
                        node_id = n["id"]
                    elif "name" in n:
                        node_id = n["name"]
                    else:
                        node_id = str(n.element_id)

                    node_label = list(n.labels)[0] if hasattr(n, "labels") and n.labels else "Unknown"
                    node_desc = n["description"] if "description" in n else ""

                    path_nodes.append({
                        "id": node_id,
                        "label": node_label,
                        "description": node_desc
                    })

                path_rels = []
                for r in record["path_rels"]:
                    rel_type = r.type
                    rel_desc = r["description"] if "description" in r else ""
                    path_rels.append({
                        "type": rel_type,
                        "description": rel_desc
                    })

                paths.append({
                    "path_nodes": path_nodes,
                    "path_rels": path_rels
                })

        return paths

    def clip_search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not hasattr(self, "faiss_index"):
            return []
        with torch.no_grad():
            inputs = self.processor(text=[query], return_tensors="pt", padding=True, truncation=True).to(self.device)
            feats = self.clip_model.get_text_features(**inputs)
            feats = feats / feats.norm(dim=-1, keepdim=True)
            feats = feats.cpu().numpy().astype("float32")
        D, I = self.faiss_index.search(feats, top_k)
        return [{
            "id": f"IMG_{idx}",
            "label": "Figure",
            "caption": self.clip_meta.iloc[idx]["Caption"],
            "image_path": self.clip_meta.iloc[idx]["Local Image Path"],
            "description": f"{self.clip_meta.iloc[idx]['Caption']} (image path: {self.clip_meta.iloc[idx]['Local Image Path']})"
        } for idx, score in zip(I[0], D[0])]

    def normalize_candidate(self, item: Dict) -> Dict:
        return {
            "id": item.get("chunk_id") or item.get("id") or f"unnamed_{hash(str(item))}",
            "label": item.get("label", "Chunk"),
            "description": item.get("description"),
            "chunk_id": item.get("chunk_id", ""),
            "content": item.get("content", ""),
            "image_path": item.get("image_path", ""),
            "caption": item.get("caption", "")
        }

    def rerank(self, query: str, candidates: List[Dict], top_n: int = 30) -> List[Dict]:
        normalized = [self.normalize_candidate(c) for c in candidates]
        pairs = [(query, c["description"]) for c in normalized]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(normalized, scores), key=lambda x: x[1], reverse=True)
        return [x[0] for x in reranked[:top_n]]

    def build_context(self, items: List[Dict]) -> str:
        lines = []
        for item in items:
            if item.get("label") == "Chunk":
                lines.append(f"[Chunk] {item.get('chunk_id')}: {item.get('description')[:256]}")
            elif item.get("label") == "Figure":
                lines.append(f"[Figure] {item.get('image_path')}: {item.get('caption')}")
            else:
                lines.append(f"[Entity] {item.get('id')}, {item.get('label')}: {item.get('description')}")
        return "\n\n".join(lines)

    def generate_answer(self, context: str, query: str) -> str:
        prompt = f"""
Based on the following technical knowledge and images, answer the user question concisely and professionally.
Do not mention any ## ids or specific chunk references ##.
You can not say you don't know the answer, but you can say the information is not available in the provided context.
{context}

User Question: {query}
"""
        res = self.client.chat.completions.create(
            model="glm-4-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024
        )
        return res.choices[0].message.content.strip()

    def fallback(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        top_chunks = self.vector_pipeline.vector_retrieve(query, top_k)
        context = "\n\n".join([c['content'] for c in top_chunks])
        answer = self.generate_answer(context, query)
        return answer, top_chunks

    def run(self, user_query: str, history: List[Dict]) -> Tuple[str, List[Dict], List[Dict]]:
        rewritten_query = self.rewrite_query(user_query, history)
        top_chunks = self.vector_retrieve(rewritten_query)
        chunk_ids = [c["chunk_id"] for c in top_chunks]

        entities = self.fetch_entities(chunk_ids) if chunk_ids else []
        image_hits = self.clip_search(rewritten_query)

        # Fallback if all sources are empty
        if not top_chunks and not entities and not image_hits:
            answer, sources = self.fallback(rewritten_query)
            return answer, sources, []

        # Rerank each modality separately (Late Fusion)
        chunk_k = 3
        entity_k = 3
        image_k = 3

        top_chunks_ranked = self.rerank(rewritten_query, top_chunks, top_n=chunk_k) if top_chunks else []
        top_entities_ranked = self.rerank(rewritten_query, entities, top_n=entity_k) if entities else []
        top_images_ranked = self.rerank(rewritten_query, image_hits, top_n=image_k) if image_hits else []

        # Fuse top results
        top_items = top_chunks_ranked + top_entities_ranked + top_images_ranked

        # Build context and generate answer
        context = self.build_context(top_items)
        answer = self.generate_answer(context, rewritten_query)

        # Find top entity for path tracing
        top_entity = next((e for e in top_items if e.get("label") not in ["Chunk", "Figure"]), None)
        paths = self.fetch_paths_for_entity(chunk_ids, top_entity["id"]) if top_entity and "id" in top_entity else []

        return answer, top_items, paths

