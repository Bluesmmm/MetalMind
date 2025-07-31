"""
clip_lora_infer.py

1.build index:
python clip_lora_infer.py `
  --build_index `
  --image_dir "/clip_lora" `
  --caption_csv "/clip_lora/vision/files/extracted_figures_with_paths_new.csv" `
  --clip_model "/clip_lora/vision/models/clip" `
  --lora_dir "lora-best"

2.text2img:
python clip_lora_infer.py `
  --mode text2img `
  --query "powder delivery system" `
  --image_dir "/clip_lora" `
  --caption_csv "/clip_lora/vision/files/extracted_figures_with_paths_new.csv" `
  --clip_model "/clip_lora/vision/models/clip" `
  --lora_dir "lora-best"

3.img2text:
python clip_lora_infer.py `
  --mode img2text `
  --query "/clip_lora/your_query_image.jpg" `
  --image_dir "/clip_lora" `
  --caption_csv "/clip_lora/vision/files/extracted_figures_with_paths_new.csv" `
  --clip_model "/clip_lora/vision/models/clip" `
  --lora_dir "lora-best"
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel
from peft import PeftModel
import faiss
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["img2text", "text2img"], default="text2img")
parser.add_argument("--query", type=str, default="")
parser.add_argument("--image_dir", type=str, default="")
parser.add_argument("--caption_csv", type=str, default="/clip_lora/vision/files/extracted_figures_with_paths.csv")
parser.add_argument("--lora_dir", type=str, default="lora-best")
parser.add_argument("--clip_model", type=str, default="/clip_lora/models/clip")
parser.add_argument("--faiss_path", type=str, default="clip_faiss.index")
parser.add_argument("--topk", type=int, default=5)
parser.add_argument("--batch_size", type=int, default=8)
parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
parser.add_argument("--build_index", action='store_true')
args = parser.parse_args()

print(f"Loading base CLIP model from: {args.clip_model}")
model = CLIPModel.from_pretrained(args.clip_model, local_files_only=True).to(args.device)
if args.lora_dir and os.path.exists(args.lora_dir):
    print(f"Loading LoRA adapter from: {args.lora_dir}")
    model = PeftModel.from_pretrained(model, args.lora_dir)
model.eval()

processor = CLIPProcessor.from_pretrained(args.clip_model, local_files_only=True)

def get_image_embedding(images):
    with torch.no_grad():
        inputs = processor(images=images, return_tensors="pt", padding=True, do_rescale=False)
        pixel_values = inputs["pixel_values"].to(args.device)
        image_features = model.get_image_features(pixel_values)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()

def get_text_embedding(texts):
    with torch.no_grad():
        inputs = processor(text=texts, return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"].to(args.device)
        attention_mask = inputs["attention_mask"].to(args.device)
        text_features = model.get_text_features(input_ids=input_ids, attention_mask=attention_mask)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()

if args.build_index:
    print("Building FAISS index from image_dir ...")
    df = pd.read_csv(args.caption_csv)
    img_paths = df["Local Image Path"].tolist()
    all_vecs, all_captions = [], []
    for i in tqdm(range(0, len(img_paths), args.batch_size)):
        imgs = []
        for p in img_paths[i:i+args.batch_size]:
            try:
                img = Image.open(os.path.join(args.image_dir, p)).convert("RGB")
                imgs.append(img)
            except Exception as e:
                print(f"[Warning] Failed to load image {p}: {e}")
        if imgs:
            feats = get_image_embedding(imgs)
            all_vecs.append(feats)
            all_captions.extend(df["Caption"].iloc[i:i+len(imgs)].tolist())
    all_vecs = np.concatenate(all_vecs, axis=0).astype("float32")
    index = faiss.IndexFlatIP(all_vecs.shape[1])
    index.add(all_vecs)
    faiss.write_index(index, args.faiss_path)
    df[["Local Image Path", "Caption"]].to_csv("clip_index_meta.csv", index=False)
    print("FAISS index & metadata saved.")
    sys.exit(0)

print("Loading FAISS index...")
index = faiss.read_index(args.faiss_path)
meta = pd.read_csv("clip_index_meta.csv")

def search_by_text(query, topk=5):
    feats = get_text_embedding([query])
    D, I = index.search(feats, topk)
    return [{"image": meta.iloc[idx]["Local Image Path"], "caption": meta.iloc[idx]["Caption"], "score": float(score)}
            for idx, score in zip(I[0], D[0])]

def search_by_image(image_path, topk=5):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Failed to open image {image_path}: {e}")
        return []
    feats = get_image_embedding([img])
    D, I = index.search(feats, topk)
    return [{"image": meta.iloc[idx]["Local Image Path"], "caption": meta.iloc[idx]["Caption"], "score": float(score)}
            for idx, score in zip(I[0], D[0])]

def show_results(results):
    for i, r in enumerate(results):
        try:
            img = Image.open(os.path.join(args.image_dir, r["image"]))
            plt.subplot(1, args.topk, i+1)
            plt.imshow(img)
            plt.title(f"{r['score']:.2f}", fontsize=8)
            plt.axis('off')
        except Exception as e:
            print(f"[Warning] Can't load result image {r['image']}: {e}")
    plt.tight_layout()
    plt.show()

if args.mode == "text2img":
    print(f"Searching images for text: {args.query}")
    res = search_by_text(args.query, args.topk)
    for i, r in enumerate(res):
        print(f"[{i+1}] {r['image']}\n  Caption: {r['caption']}\n  Score: {r['score']:.4f}")
    show_results(res)
elif args.mode == "img2text":
    print(f"Searching captions for image: {args.query}")
    res = search_by_image(args.query, args.topk)
    for i, r in enumerate(res):
        print(f"[{i+1}] {r['image']}\n  Caption: {r['caption']}\n  Score: {r['score']:.4f}")
    show_results(res)
else:
    print("Unknown mode! Use --mode text2img or img2text.")
