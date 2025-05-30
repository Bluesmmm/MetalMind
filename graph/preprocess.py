import os
import json
import subprocess
import tiktoken
import csv

def run_mineru(pdf_path, mineru_output_dir):
    """
    调用 MinerU CLI 工具进行多模态解析，输出 markdown + JSON
    """
    os.makedirs(mineru_output_dir, exist_ok=True)

    command = [
        "magic-pdf",
        "--pdf", pdf_path,
        "--output_dir", mineru_output_dir,
        "--model", "pdf2md"
    ]
    print("[INFO] Running MinerU:", " ".join(command))
    subprocess.run(command, check=True)
    print(f"[INFO] MinerU 处理完成，输出保存在 {mineru_output_dir}")

def load_chunks_from_markdown(mineru_output_dir, chunk_size=600, overlap=100):
    """
    加载 markdown 并按 token 分块
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    chunks = []
    md_dir = os.path.join(mineru_output_dir, "markdown")

    for filename in os.listdir(md_dir):
        if filename.endswith(".md"):
            with open(os.path.join(md_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
            tokens = encoder.encode(content)
            for start in range(0, len(tokens), chunk_size - overlap):
                end = min(start + chunk_size, len(tokens))
                chunk = encoder.decode(tokens[start:end])
                chunks.append({
                    "source": filename,
                    "content": chunk
                })
    print(f"[INFO] 共提取文本块: {len(chunks)}")
    return chunks

def extract_figures_table_info(mineru_output_dir, csv_path):
    """
    从 MinerU 输出的 JSON 中提取图像和表格路径及描述
    """
    figures = []
    json_path = os.path.join(mineru_output_dir, "nlp_json", "structure.json")
    if not os.path.exists(json_path):
        print("[WARN] 未找到结构化输出 JSON，跳过图像/表格信息提取。")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    for block in doc.get("blocks", []):
        if block.get("type") in ["figure", "table"]:
            figures.append({
                "Local Path": block.get("file_name", ""),
                "Caption": block.get("caption", "")
            })

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Local Path", "Caption"])
        writer.writeheader()
        writer.writerows(figures)
    print(f"[INFO] 提取图像和表格信息: {len(figures)} 条，写入 {csv_path}")

def run_preprocessing(pdf_path, mineru_output_dir, chunk_json_path, figure_csv_path, chunk_size=600, overlap=100):
    """
    全流程接口：MinerU → 分块 → 图像/表格路径提取
    """
    run_mineru(pdf_path, mineru_output_dir)

    chunks = load_chunks_from_markdown(mineru_output_dir, chunk_size, overlap)
    with open(chunk_json_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 文本块写入 {chunk_json_path}")

    extract_figures_table_info(mineru_output_dir, figure_csv_path)

    print("[✅] MinerU 全文预处理完成")

if __name__ == "__main__":
    pdf_path = "AM400.pdf"
    output_dir = "output"
    chunk_json_path = "output/AM400.json"
    figure_csv_path = "output/figures.csv"
    run_preprocessing(pdf_path, output_dir, chunk_json_path, figure_csv_path)