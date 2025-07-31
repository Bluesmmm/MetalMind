import sys
import os
import json
import glob
import datetime
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from zhipuai import ZhipuAI

from rag.rag_vector import VectorRAGPipeline
from rag.rag_graph import GraphRAGPipeline
from rag.rag_hybrid import HybridRAGPipeline
from utils.api import api_key

HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = "hybrid"

@st.cache_resource
def load_pipelines():
    return {
        "vector": VectorRAGPipeline(),
        "graph": GraphRAGPipeline(
            neo4j_uri="",
            neo4j_user="",
            neo4j_password=""
        ),
        "hybrid": HybridRAGPipeline(
            neo4j_uri="",
            neo4j_user="",
            neo4j_password="",
            clip_model_dir="clip_lora/vision/models/clip",
            lora_dir="clip_lora/vision/lora-best",
            faiss_path="clip_lora/vision/clip_faiss.index",
            meta_csv="clip_lora/vision/clip_index_meta.csv",
            device=""
        )
    }

pipelines = load_pipelines()
client = ZhipuAI(api_key=api_key)

def auto_select_mode_llm(query: str) -> str:
    prompt = f"""
You are a RAG assistant that helps determine the best retrieval strategy.
Decide whether to use vector, graph, or hybrid retrieval mode for the user query.

Here are some examples:

Query: What is the function of the build chamber?\nAnswer: vector
Query: How does the recoater interact with the build platform?\nAnswer: graph
Query: Show me the diagram of the safe change filter valve.\nAnswer: hybrid
Query: What are the maintenance steps for the laser chiller?\nAnswer: vector
Query: Which part connects the argon gas supply and filter assembly?\nAnswer: graph
Query: Where is the image showing the wiper installation?\nAnswer: hybrid

Now decide the retrieval mode for the following user query:
Query: {query}
Answer with only one of: vector, graph, hybrid
"""
    try:
        res = client.chat.completions.create(
            model="glm-4-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=5
        )
        return res.choices[0].message.content.strip().lower()
    except:
        return "vector"

st.subheader("🧠 MetalMind: A Customized RAG System for Metal AM")

st.sidebar.header("Mode Selection")
auto_mode = st.sidebar.checkbox("Auto Select By LLM", value=False)
mode = st.sidebar.selectbox("Retrieve Mode", ["vector", "graph", "hybrid"], index=["vector", "graph", "hybrid"].index(st.session_state.mode))
st.session_state.mode = mode

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Load Past Chat")
history_files = sorted(glob.glob(os.path.join(HISTORY_DIR, "*.json")), reverse=True)
if st.sidebar.button("🗑️ Delete All History Files"):
    for f in history_files:
        os.remove(f)
    st.sidebar.success("All history files deleted.")
    st.rerun()
selected_file = st.sidebar.selectbox("Select a history file", ["(None)"] + [os.path.basename(f) for f in history_files])

if selected_file != "(None)":
    if st.sidebar.button("🔁 Load This Chat"):
        with open(os.path.join(HISTORY_DIR, selected_file), "r", encoding="utf-8") as f:
            st.session_state.history = json.load(f)
        st.rerun()

user_input = st.text_input("Please tell us what do you need：", key="user_query")
submit = st.button("🚀 Send")
clear_history = st.button("🔍 Clear Chat History")

if clear_history:
    st.session_state.history = []
    st.rerun()

if submit and user_input.strip():
    with st.spinner("Thinking..."):
        chosen_mode = auto_select_mode_llm(user_input) if auto_mode else mode
        pipeline = pipelines[chosen_mode]
        result = pipeline.run(user_input, st.session_state.history)

        if isinstance(result, tuple) and len(result) == 3:
            answer, sources, paths = result
        else:
            answer, sources = result
            paths = []

        st.session_state.history.append({"user": user_input, "assistant": answer})
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
        with open(os.path.join(HISTORY_DIR, filename), "w", encoding="utf-8") as f:
            json.dump(st.session_state.history, f, ensure_ascii=False, indent=2)

        st.markdown("### 🤖 Answer")
        st.markdown(answer)

        if sources:
            st.markdown("### 📚 Sources(Vector)")
            for i, src in enumerate(sources, 1):
                label = src.get("label")
                if label == "Figure":
                    rel_path = src.get("image_path", "").strip()
                    if rel_path:        
                        img_path = Path("clip_lora") / rel_path          
                        if img_path.is_file():                                
                            st.image(str(img_path), caption=src.get("caption", ""), width=300)
                        else:                                              
                            st.warning(f"Image Not Found: {img_path}")
                elif label == "Entity":
                    st.markdown(f"**[Entity {i}]** `{src['id']}` ({label}): {src.get('description', 'No description')}")
                elif label == "Chunk" or label is None:
                    source_id = src.get("source") or src.get("chunk_id") or src.get("id", f"Item_{i}")
                    description = src.get("description")
                    st.markdown(f"**[Chunk {i}] `{source_id}`**\n\n{description[:500]}")

            st.markdown("### 📑 Sources(Graph)")

            import pandas as pd
            type_order = [
                "Chunk", "Component", "Material", "Procedure", "SafetyStep",
                "Tool", "Warning", "AdditionalInfo", "Figure", "Document", "Image", "Entity"
            ]

            for t in type_order:
                typed_sources = [s for s in sources if s.get("label") == t]
                if typed_sources:
                    st.markdown(f"#### 🏷️ `{t}` ({len(typed_sources)} items)")
                    if t == "Chunk":
                        # Full display for chunks
                        df = pd.json_normalize(typed_sources)
                    elif t == "Figure":
                        df = pd.json_normalize(typed_sources)
                        columns = [c for c in ["id", "label", "description", "image_path", "caption"] if c in df.columns]
                        st.dataframe(df[columns])
                    else:
                        # Only show id, label, description for others
                        df = pd.json_normalize(typed_sources)[["id", "label", "description"]]
                    st.dataframe(df, use_container_width=True)

        if paths:
            st.markdown("### 🕸️ Knowledge Graph")

            import pandas as pd

            color_map = {
                "Chunk": "#6FA8DC", "Component": "#F6B26B", "Material": "#FFD966",
                "Procedure": "#93C47D", "SafetyStep": "#C9DAF8", "Tool": "#D5A6BD",
                "Warning": "#E06666", "AdditionalInfo": "#A4C2F4", "Entity": "#CCCCCC",
                "Figure": "#FAD7A0", "Document": "#D7BDE2", "Unknown": "#999999"
            }

            for path_idx, path in enumerate(paths):
                with st.expander(f"📌 Path {path_idx + 1}", expanded=True):
                    net = Network(height="400px", width="100%", bgcolor="#ffffff", font_color="black", directed=False)

                    nodes = path.get("path_nodes", [])
                    rels = path.get("path_rels", [])

                    for node in nodes:
                        nid = node.get("id", "Unknown")
                        nlabel = node.get("label", "Unknown")
                        node_info = "<br>".join([f"<b>{k}</b>: {v}" for k, v in node.items()])
                        net.add_node(
                            nid,
                            label=f"{nlabel}: {nid}",
                            color=color_map.get(nlabel, "#CCCCCC"),
                            title=node_info
                        )

                    for j in range(len(nodes) - 1):
                        rel_info = rels[j] if j < len(rels) else "Unknown"
                        from_node = nodes[j]["id"]
                        to_node = nodes[j + 1]["id"]

                        if isinstance(rel_info, dict):
                            rel_label = rel_info.get("description")
                            rel_title = "<br>".join([f"<b>{k}</b>: {v}" for k, v in rel_info.items()])
                        else:
                            rel_label = str(rel_info)
                            rel_title = rel_label

                        net.add_edge(
                            from_node,
                            to_node,
                            label=rel_label,
                            title=rel_title
                        )

                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                    net.write_html(tmp_file.name)
                    with open(tmp_file.name, "r", encoding="utf-8") as f:
                        html_content = f.read()
                        components.html(html_content, height=420)

                    st.markdown("#### 🧩 Node Details")
                    if nodes:
                        node_data = []
                        for node in nodes:
                            node_data.append({
                                "name": node.get("id", ""),
                                "label": node.get("label", ""),
                                "description": node.get("description", "")
                            })
                        node_df = pd.DataFrame(node_data)
                        st.dataframe(node_df, use_container_width=True)

                    st.markdown("#### 🔗 Relationship Details")
                    rel_table = []
                    for j in range(len(nodes) - 1):
                        from_node = nodes[j].get("id", "")
                        to_node = nodes[j + 1].get("id", "")
                        rel_info = rels[j] if j < len(rels) else {}
                        if isinstance(rel_info, dict):
                            description = rel_info.get("description", "")
                        else:
                            description = str(rel_info)  # fallback

                        rel_table.append({
                            "from": from_node,
                            "to": to_node,
                            "description": description
                        })

                    if rel_table:
                        rel_df = pd.DataFrame(rel_table)
                        st.dataframe(rel_df, use_container_width=True)
                    else:
                        st.info("No relationship data available.")

if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📂 History Chat")
    with st.container():
        st.markdown("<div style='max-height: 300px; overflow-y: auto;'>", unsafe_allow_html=True)
        for turn in reversed(st.session_state.history):
            st.markdown(f"**👤 User：** {turn['user']}")
            st.markdown(f"**🤖 Assistant：** {turn['assistant']}")
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)
