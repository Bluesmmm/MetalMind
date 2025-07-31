import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pandas as pd
from tqdm import tqdm
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

from rag.rag_vector import VectorRAGPipeline
from rag.rag_graph import GraphRAGPipeline
from rag.rag_hybrid import HybridRAGPipeline

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
def load_evalset(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def context_recall(pred_ctx, gold_ans):
    hit = 0
    total = 0
    gold_sentences = [s.strip() for s in gold_ans.split('.') if s.strip()]
    for s in gold_sentences:
        total += 1
        if s in pred_ctx:
            hit += 1
    return hit / total if total > 0 else 0

def compute_bleu(pred, gold):
    smoothie = SmoothingFunction().method4
    return sentence_bleu([gold.split()], pred.split(), smoothing_function=smoothie)

def evaluate_pipeline(pipeline, evalset, name="HybridRAG", result_csv="eval_results.csv"):
    results = []
    for sample in tqdm(evalset, desc=f"Evaluating-{name}"):
        query = sample["query"]
        golden = sample["answer"]

        if name.lower() == "vectorrag":
            answer, sources = pipeline.run(query, [])
            paths = []
        else:
            answer, sources, paths = pipeline.run(query, [])

        context_str = "\n".join(
            s.get("content", s.get("description", s.get("caption", ""))) for s in sources
        )

        bleu = compute_bleu(answer, golden)
        recall = context_recall(context_str, golden)
        context_token_len = len(tokenizer.encode(context_str))
        answer_token_len = len(tokenizer.encode(answer))

        results.append({
            "query": query,
            "golden": golden,
            "answer": answer,
            "context": context_str,
            "BLEU": bleu,
            "ContextRecall": recall,
            "ContextTokens": context_token_len,
            "AnswerTokens": answer_token_len,
            "Paths": json.dumps(paths, ensure_ascii=False) 
        })

    df = pd.DataFrame(results)
    df.to_csv(result_csv, index=False)
    print(f"\n=== {name} ===")
    print(df[["BLEU", "ContextRecall", "ContextTokens", "AnswerTokens"]].describe())
    return df


if __name__ == "__main__":
    evalset = load_evalset("evaluate.json")

    # # 1. Vector RAG
    # vector_rag = VectorRAGPipeline()
    # evaluate_pipeline(
    #     pipeline=vector_rag,
    #     evalset=evalset,
    #     name="VectorRAG",
    #     result_csv="eval_vector.csv"
    # )

    # 2. KG RAG
    graph_rag = GraphRAGPipeline(
        neo4j_uri="",
        neo4j_user="",
        neo4j_password=""
    )
    evaluate_pipeline(
        pipeline=graph_rag,
        evalset=evalset,
        name="GraphRAG",
        result_csv="eval_graph.csv"
    )
    
    # 3. Hybrid RAG
    base_dir = os.path.dirname(__file__)
    hybrid_rag = HybridRAGPipeline(
        neo4j_uri="",
        neo4j_user="",
        neo4j_password="",
        clip_model_dir = "../clip_lora/vision/models/clip",
        lora_dir="../clip_lora/vision/lora-best",
        faiss_path="../clip_lora/vision/clip_faiss.index",
        meta_csv="../clip_lora/vision/clip_index_meta.csv",
        device="cpu"
    )
    evaluate_pipeline(
        pipeline=hybrid_rag,
        evalset=evalset,
        name="HybridRAG",
        result_csv="eval_hybrid.csv"
    )
