import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import io

# Load model once (IMPORTANT)
device = "cuda" if torch.cuda.is_available() else "cpu"

processor = Blip2Processor.from_pretrained(
    "Salesforce/blip2-flan-t5-small"
)

model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-flan-t5-small",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)

model.to(device)
model.eval()


def blip_generate(image_bytes: bytes):
    """
    Generate caption, summary, and realistic story using BLIP-2
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def ask(prompt: str, max_tokens=120):
        inputs = processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        ).to(device)

        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens
        )

        return processor.decode(output[0], skip_special_tokens=True)

    caption = ask(
        "Describe this image accurately in one sentence."
    )

    summary = ask(
        "Give a short, factual summary of what is happening in this image."
    )

    story = ask(
        "Write a realistic short paragraph describing exactly what is visible in this image. Do not invent details."
    )

    return caption, summary, story
