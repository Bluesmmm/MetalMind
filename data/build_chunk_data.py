import os
import json
from transformers import AutoTokenizer, AutoConfig

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
INPUT_ROOT = "../raw_data/after_parsing"
OUTPUT_JSON = "chunk_data.json"

def find_all_full_md(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "full.md":
                yield os.path.join(root, file)

def chunk_text(text, tokenizer, chunk_size=600, overlap=100):
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        sub_tokens = tokens[i:i+chunk_size]
        chunk_text = tokenizer.decode(sub_tokens)
        chunks.append(chunk_text.strip())
    return chunks

def build_chunk_data():
    config = AutoConfig.from_pretrained("THUDM/glm-4-9b-chat", trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained("THUDM/glm-4-9b-chat", config=config, trust_remote_code=True)

    all_chunks = []
    for md_path in find_all_full_md(INPUT_ROOT):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        source_name = os.path.basename(os.path.dirname(md_path))
        chunks = chunk_text(content, tokenizer, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk in chunks:
            all_chunks.append({
                "source": source_name,
                "content": chunk
            })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(all_chunks, out, ensure_ascii=False, indent=2)
    print(f"chunk data written to {OUTPUT_JSON} with {len(all_chunks)} chunks.")

if __name__ == "__main__":
    build_chunk_data()
