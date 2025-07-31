from typing import List, Dict, Tuple
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
from neo4j import GraphDatabase
from zhipuai import ZhipuAI
from utils.api import api_key

MAX_HISTORY_TURNS = 3

class GraphRAGPipeline:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.embedding_model = SentenceTransformer("BAAI/bge-m3")
        self.reranker = CrossEncoder("BAAI/bge-reranker-large")
        self.client = ZhipuAI(api_key=api_key)

        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.chunk_embeddings = self.load_chunk_embeddings()
        self.chunk_nodes = self.load_chunk_nodes()

    def load_chunk_embeddings(self) -> np.ndarray:
        path = os.path.join(os.path.dirname(__file__), "vector_embeddings", "embeddings.npy")
        return np.load(path)

    def load_chunk_nodes(self) -> List[Dict]:
        path = os.path.join(os.path.dirname(__file__), "vector_embeddings", "metadata.json")
        with open(path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        return chunks

    def rewrite_query(self, query: str, history: List[Dict]) -> str:
        history_text = ""
        for turn in history[-MAX_HISTORY_TURNS:]:
            history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"

        prompt = f"""
You are an intelligent assistant for industrial question answering.
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
        except:
            return query

    def get_query_embedding(self, query: str) -> np.ndarray:
        return self.embedding_model.encode([query], normalize_embeddings=True).astype("float32")[0]

    def identify_relevant_chunks(self, query: str, top_k: int = 1) -> List[Dict]:
        query_vec = self.get_query_embedding(query)
        scores = np.dot(self.chunk_embeddings, query_vec)
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [self.chunk_nodes[i] for i in top_indices]

    def fetch_entities(self, chunk_ids: List[str], max_hops: int = 2) -> List[Dict]:
        chunk_ids_str = ', '.join(f'"{cid}"' for cid in chunk_ids)
        query = f"""
        MATCH (c:Chunk)
        WHERE c.chunk_id IN [{chunk_ids_str}]
        MATCH (c)-[:RELATION*1..{max_hops}]-(e)
        WHERE NONE(lbl IN labels(e) WHERE lbl IN ["Chunk", "Document"])
        RETURN DISTINCT elementId(e) AS id, head(labels(e)) AS label, e.description AS description
        """
        entities = []
        with self.driver.session() as session:
            results = session.run(query)
            for record in results:
                entities.append({
                    "id": record["id"],
                    "label": record.get("label", "Unknown"),
                    "description": record.get("description", "")
                })
        return entities

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

    def rerank_entities(self, query: str, candidates: List[Dict], top_n: int = 3) -> List[Dict]:
        pairs = [(query, c["description"]) for c in candidates]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [x[0] for x in ranked[:top_n]]

    def build_context(self, entities: List[Dict]) -> str:
        lines = ["Based on the following technical knowledge:"]
        for i, e in enumerate(entities):
            lines.append(f"{i+1}. Entity: {e['id']}\n   Type: {e['label']}\n   Description: {e['description']}")
        return "\n\n" + "\n\n".join(lines)

    def generate_answer(self, context: str, query: str) -> str:
        prompt = f"""
{context}

User Question: {query}

Please provide a professional, concise answer based only on the information above. Do not mention any ## ids or specific chunk references ##.
"""
        res = self.client.chat.completions.create(
            model="glm-4-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=512
        )
        return res.choices[0].message.content.strip()

    def fallback_rag(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        query_vec = self.get_query_embedding(query)
        scores = np.dot(self.chunk_embeddings, query_vec)
        top_indices = np.argsort(scores)[-top_k:][::-1]
        top_chunks = [self.chunk_nodes[i] for i in top_indices]
        context = "\n\n".join([f"Chunk {i+1}:\n{c['description']}" for i, c in enumerate(top_chunks)])
        answer = self.generate_answer(context, query)
        return answer, top_chunks

    def run(self, user_query: str, history: List[Dict]) -> Tuple[str, List[Dict], List[Dict]]:
        rewritten_query = self.rewrite_query(user_query, history)
        chunks = self.identify_relevant_chunks(rewritten_query)
        chunk_ids = [c["chunk_id"] for c in chunks]

        if not chunk_ids:
            answer, fallback_chunks = self.fallback_rag(rewritten_query)
            return answer, fallback_chunks, []

        entities = self.fetch_entities(chunk_ids)
        if not entities:
            answer, fallback_chunks = self.fallback_rag(rewritten_query)
            return answer, fallback_chunks, []

        top_entities = self.rerank_entities(rewritten_query, entities)
        top_entity = top_entities[0] if top_entities else None

        paths = []
        if top_entity:
            path = self.fetch_paths_for_entity(chunk_ids, top_entity["id"])
            if path:
                paths.extend(path)

        context = self.build_context(top_entities)
        answer = self.generate_answer(context, rewritten_query)
        return answer, top_entities, paths


if __name__ == "__main__":
    rag = GraphRAGPipeline(
        neo4j_uri="",
        neo4j_user="",
        neo4j_password=""
    )
    conversation_history = []
    while True:
        user_query = input("User: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            break
        answer, sources, paths = rag.run(user_query, conversation_history)
        print("Answer:\n", answer)
        print("Sources:\n", sources)
        print("Paths:\n", paths)
        conversation_history.append({"user": user_query, "assistant": answer})
