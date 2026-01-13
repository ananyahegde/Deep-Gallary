import torch
from PIL import Image
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    CLIPProcessor,
    CLIPModel,
    ViTImageProcessor,
    ViTForImageClassification,
    BatchEncoding,
)
import os
from typing import Optional, List, cast
import re

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

blip_processor: Optional[BlipProcessor] = None
blip_model: Optional[BlipForConditionalGeneration] = None
clip_processor: Optional[CLIPProcessor] = None
clip_model: Optional[CLIPModel] = None
vit_processor: Optional[ViTImageProcessor] = None
vit_model: Optional[ViTForImageClassification] = None

CLIP_CATEGORIES = [
    "architecture", "buildings", "urban", "interior",
    "food", "culinary",
    "nature", "landscape", "mountains", "ocean", "forest",
    "portrait", "people",
    "wildlife", "animals", "pets",
    "travel", "street photography", "night photography",
    "abstract", "minimalist", "macro"
]

class MLServiceError(Exception):
    pass

def load_models() -> None:
    global blip_processor, blip_model, clip_processor, clip_model, vit_processor, vit_model

    try:
        if blip_model is None:
            print("Loading BLIP model...")
            blip_processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-base",
                cache_dir=MODEL_DIR,
            )
            blip_model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base",
                cache_dir=MODEL_DIR,
            )
            blip_model.to(device)
            print("BLIP model loaded successfully")

        if clip_model is None:
            print("Loading CLIP model...")
            clip_processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=MODEL_DIR,
            )
            clip_model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=MODEL_DIR,
            )
            clip_model.to(device)
            print("CLIP model loaded successfully")

        if vit_model is None:
            print("Loading ViT model...")
            vit_processor = ViTImageProcessor.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=MODEL_DIR,
            )
            vit_model = ViTForImageClassification.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=MODEL_DIR,
            )
            vit_model.to(device)
            print("ViT model loaded successfully")
    except Exception as e:
        raise MLServiceError(f"Failed to load models: {str(e)}")

def clean_vit_label(label: str) -> str:
    label = label.replace("_", " ")

    label = re.sub(r',.*$', '', label)

    label = label.strip()

    words = label.split()
    if len(words) > 2:
        label = " ".join(words[:2])

    return label

def generate_caption(image_path: str) -> str:
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        load_models()

        assert blip_processor is not None
        assert blip_model is not None

        image = Image.open(image_path).convert("RGB")

        inputs = cast(
            BatchEncoding,
            blip_processor(images=image, return_tensors="pt"),
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        output_ids = blip_model.generate(**inputs, max_length=50)
        caption = blip_processor.decode(
            output_ids[0], skip_special_tokens=True
        )

        return caption
    except FileNotFoundError:
        raise
    except Exception as e:
        raise MLServiceError(f"Failed to generate caption: {str(e)}")

def predict_tags_vit(image_path: str, top_k: int = 2) -> List[str]:
    try:
        load_models()

        assert vit_processor is not None
        assert vit_model is not None

        image = Image.open(image_path).convert("RGB")

        inputs = vit_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = vit_model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]

        top_indices = torch.argsort(probs, descending=True)[:top_k]

        tags = []
        for idx in top_indices:
            label = vit_model.config.id2label[idx.item()]
            cleaned_label = clean_vit_label(label)
            tags.append(cleaned_label)

        return tags
    except Exception as e:
        raise MLServiceError(f"Failed to predict ViT tags: {str(e)}")

def predict_tags_clip(image_path: str, top_k: int = 2) -> List[str]:
    try:
        load_models()

        assert clip_processor is not None
        assert clip_model is not None

        image = Image.open(image_path).convert("RGB")

        inputs = cast(
            BatchEncoding,
            clip_processor(
                text=CLIP_CATEGORIES,
                images=image,
                return_tensors="pt",
                padding=True,
            ),
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = clip_model(**inputs)
            logits = outputs.logits_per_image[0]
            probs = torch.softmax(logits, dim=0)

        top_indices = torch.argsort(probs, descending=True)[:top_k]
        return [CLIP_CATEGORIES[i] for i in top_indices]
    except Exception as e:
        raise MLServiceError(f"Failed to predict CLIP tags: {str(e)}")

def predict_tags(image_path: str) -> List[str]:
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        clip_tags = predict_tags_clip(image_path, top_k=2)
        vit_tags = predict_tags_vit(image_path, top_k=2)

        combined_tags = clip_tags + vit_tags

        seen = set()
        unique_tags = []
        for tag in combined_tags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)

        return unique_tags
    except FileNotFoundError:
        raise
    except Exception as e:
        raise MLServiceError(f"Failed to predict tags: {str(e)}")
