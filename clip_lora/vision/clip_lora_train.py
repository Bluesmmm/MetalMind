import os
import pandas as pd
import torch
import torch.nn as nn
import numpy as np
import torchvision.transforms as transforms
import random
from tqdm import tqdm
from PIL import Image, ImageFile
from datetime import datetime
from torch.utils.data import Dataset, DataLoader
from transformers import CLIPProcessor, CLIPModel
from peft import LoraConfig, get_peft_model
from accelerate import Accelerator
import wandb

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Reproducibility
np.random.seed(42)
torch.manual_seed(42)
random.seed(42)

# WandB init
wandb.init(
    mode="offline",
    project="clip-lora-renishaw",
    name="run_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
    config={"epochs": 100, "batch_size": 64, "lr": 1e-5, "model": "CLIP + LoRA"}
)

# Accelerator
accelerator = Accelerator(mixed_precision="fp16")

# Dataset
class Image_dataset(Dataset):
    def __init__(self, root_dir, data_frame, processor, transforms=None):
        self.root_dir = root_dir
        self.processor = processor
        self.transforms = transforms
        self.data_list = [
            [row["Local Image Path"], [row["Caption"]]] for _, row in data_frame.iterrows()
        ]

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        image_name, captions = self.data_list[idx]
        image_name = image_name.strip()
        full_path = os.path.join(self.root_dir, image_name)

        try:
            img = Image.open(full_path).convert("RGB")
        except Exception as e:
            print(f"[WARNING] Skipping image {full_path} due to error: {e}")
            return self.__getitem__((idx + 1) % len(self.data_list))

        if self.transforms:
            img = self.transforms(img)
        caption = random.choice(captions)
        return img, caption

# Transforms (exclude ToTensor/Normalize)
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(336),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    transforms.RandomRotation(30)
])
val_transforms = transforms.Compose([
    transforms.Resize(336)
])

# Load data
processor = CLIPProcessor.from_pretrained(
    "", local_files_only=True
)
data = pd.read_csv("/extracted_figures_with_paths_new.csv")

# Clean up invalid image paths
data["Local Image Path"] = data["Local Image Path"].apply(lambda x: os.path.join("/clip_lora", x.strip()))
data = data[data["Local Image Path"].apply(lambda p: os.path.exists(p) and p.lower().endswith((".png", ".jpg", ".jpeg")))].reset_index(drop=True)

# Dataset
train_set = Image_dataset("", data[:808], processor, train_transforms)
val_set = Image_dataset("", data[808:], processor, val_transforms)

# Collate function
collate_fn = lambda samples: processor(
    text=[t for _, t in samples],
    images=[i for i, _ in samples],
    return_tensors="pt",
    padding=True,
    do_rescale=False
)

# DataLoaders
train_loader = DataLoader(train_set, batch_size=64, shuffle=True, collate_fn=collate_fn, num_workers=8, pin_memory=True)
val_loader = DataLoader(val_set, batch_size=64, shuffle=False, collate_fn=collate_fn, num_workers=8, pin_memory=True)

# Load model and apply LoRA
base_model = CLIPModel.from_pretrained(
    "/clip_lora/models/clip", local_files_only=True
)
config = LoraConfig(r=16, lora_alpha=16, target_modules=["q_proj", "v_proj"], lora_dropout=0.1, bias="none")
model = get_peft_model(base_model, config)

# Freeze base model
for name, param in model.named_parameters():
    if "lora_" not in name:
        param.requires_grad = False

optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5)
criterion = nn.CrossEntropyLoss()

# Prepare for acceleration
model, optimizer, train_loader, val_loader = accelerator.prepare(
    model, optimizer, train_loader, val_loader
)

# Validation function
def evaluate(model):
    model.eval()
    correct, total_loss = 0, 0
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids']
            attention_mask = batch['attention_mask']
            pixel_values = batch['pixel_values']
            targets = torch.arange(input_ids.size(0)).long().to(input_ids.device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, pixel_values=pixel_values)
            loss_i = criterion(outputs.logits_per_image, targets)
            loss_t = criterion(outputs.logits_per_text, targets)
            loss = (loss_i + loss_t) / 2
            total_loss += loss.item() * input_ids.size(0)
            preds = torch.argmax(outputs.logits_per_image, dim=1)
            correct += (preds == targets).sum().item()
    return correct / len(val_set), total_loss / len(val_set)

# Training loop
best_loss = float("inf")
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        pixel_values = batch['pixel_values']
        targets = torch.arange(input_ids.size(0)).long().to(input_ids.device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, pixel_values=pixel_values)
        loss_i = criterion(outputs.logits_per_image, targets)
        loss_t = criterion(outputs.logits_per_text, targets)
        loss = (loss_i + loss_t) / 2
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
        running_loss += loss.item() * input_ids.size(0)

    train_loss = running_loss / len(train_set)
    val_acc, val_loss = evaluate(accelerator.unwrap_model(model))
    wandb.log({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss, "val_acc": val_acc})

    if val_loss < best_loss:
        best_loss = val_loss
        accelerator.unwrap_model(model).save_pretrained("lora-best")

# Save final model
accelerator.unwrap_model(model).save_pretrained("lora-final")
wandb.finish()
