from torch.nn.functional import embedding
from services.model_services import generate_caption, predict_tags, extract_vit_embedding

paths = ["uploads/images/cat.jpg", "uploads/images/nature.jpg", "uploads/images/pasta.jpg", "uploads/images/rome.jpg", "uploads/images/woman.jpg"]

for image_path in paths:
    try:
        print("Generating caption...")
        caption = generate_caption(image_path)
        print(f"Caption: {caption}\n")

        print("Predicting tags...")
        tags = predict_tags(image_path)
        print(f"Tags: {tags}")

        print("Extracting Embedding...")
        embedding = extract_vit_embedding(image_path)
        print(f"Embedding: {embedding}")

    except Exception as e:
        print(f"Error: {e}")
