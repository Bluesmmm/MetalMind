# MATCH (n)
# DETACH DELETE n;
import re
import os
import json
import hashlib
import colorsys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from zhipuai import ZhipuAI
from neo4j import GraphDatabase

client = ZhipuAI(api_key="eec3e949ce864c05b28c326c53f0fcd3.77NtrJwUcrvCzbpt")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNK_JSON_PATH = os.path.join(SCRIPT_DIR, "chunk_data_20250606.json")
PROMPT_FILE = os.path.join(SCRIPT_DIR, "kg_prompt.txt")

TUPLE_DELIMITER = "|||"
RECORD_DELIMITER = "<REC>"
COMPLETION_DELIMITER = "<END>"

NEO4J_URI = "bolt://localhost:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neoneo4j"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

def extract_entities_relations(text):
    prompt = PROMPT_TEMPLATE \
        .replace("{input_text}", text.strip()) \
        .replace("{tuple_delimiter}", TUPLE_DELIMITER) \
        .replace("{record_delimiter}", RECORD_DELIMITER) \
        .replace("{completion_delimiter}", COMPLETION_DELIMITER)

    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.7,
            max_tokens=4096
        )
        result = response.choices[0].message.content
    except Exception as e:
        print("模型调用失败：", e)
        return []

    if COMPLETION_DELIMITER in result:
        result = result.split(COMPLETION_DELIMITER)[0]

    segments = result.split(RECORD_DELIMITER)
    triples = []

    for seg in segments:
        raw_seg = seg
        seg = seg.strip()

        if not seg:
            continue

        match = re.match(r'["\'()]*\s*(entity|relationship)\s*["\'()]*\s*\|\|\|(.*)', seg, re.IGNORECASE)
        if not match:
            print(raw_seg)
            continue

        kind = match.group(1).lower()
        rest = match.group(2)
        parts = [p.strip() for p in rest.split(TUPLE_DELIMITER)]

        if kind == "entity" and len(parts) == 3:
            triples.append({"type": "entity", "name": parts[0], "entity_type": parts[1], "description": parts[2]})
        elif kind == "relationship" and len(parts) == 3:
            triples.append({"type": "relation", "source": parts[0], "target": parts[1], "desc": parts[2]})

    return triples

def format_label(label):
    return ''.join(word.capitalize() for word in re.split(r'\W+', label) if word)

def type_to_color(entity_type):
    h = int(hashlib.md5(entity_type.encode()).hexdigest(), 16)
    hue = (h % 360) / 360.0
    saturation = 0.7
    value = 0.9
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return '#{:02X}{:02X}{:02X}'.format(int(r*255), int(g*255), int(b*255))

def insert(parsed, driver):
    with driver.session() as session:
        for item in parsed:
            if item["type"] == "entity":
                label = format_label(item["entity_type"])
                etype = item["entity_type"].upper()
                color = type_to_color(etype)
                session.run(f"""
                    MERGE (e:{label} {{name: $name}})
                    SET e.description = $desc,
                        e.entity_type = $etype,
                        e.color = $color
                """, name=item["name"], desc=item["description"], etype=etype, color=color)

            elif item["type"] == "relation":
                session.run("""
                    MATCH (s {name: $source}), (t {name: $target})
                    MERGE (s)-[r:RELATION {description: $desc}]->(t)
                """, source=item["source"], target=item["target"], desc=item["desc"])

def build_kg():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with open(CHUNK_JSON_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(extract_entities_relations, c["content"]) for c in chunks]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Building KG"):
            parsed = future.result()
            if parsed:
                insert(parsed, driver)

    driver.close()

if __name__ == "__main__":
    build_kg()
