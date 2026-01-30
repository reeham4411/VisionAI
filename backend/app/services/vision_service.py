import cv2
import numpy as np
import torch
import random
import io
from PIL import Image

from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration

from app.schemas.response import ImageAnalysisResponse

# -------------------------
# Device setup
# -------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------------
# Load YOLOv8 model
# -------------------------
yolo_model = YOLO("yolov8n.pt")

# -------------------------
# Load BLIP (captioning ONLY)
# -------------------------
blip_processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

blip_model.eval()

# -------------------------
# Emotion mapping (explainable)
# -------------------------
EMOTION_MAP = {
    "person": ["calm", "contemplative", "neutral"],
    "dog": ["playful", "joyful"],
    "cat": ["calm", "peaceful"],
    "car": ["busy", "dynamic"],
    "laptop": ["focused", "productive"],
    "phone": ["busy", "connected"],
    "tree": ["peaceful", "serene"],
    "building": ["neutral", "structured"],
}


def determine_emotion(objects: list) -> str:
    emotions = []
    for obj in objects:
        if obj.lower() in EMOTION_MAP:
            emotions.extend(EMOTION_MAP[obj.lower()])
    return random.choice(emotions) if emotions else "neutral"


# -------------------------
# BLIP caption generation
# -------------------------
def generate_caption(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    inputs = blip_processor(
        images=image,
        return_tensors="pt"
    ).to(device)

    output = blip_model.generate(
        **inputs,
        max_new_tokens=40
    )

    caption = blip_processor.decode(
        output[0],
        skip_special_tokens=True
    )

    return caption.strip()


# -------------------------
# Grounded text generation
# -------------------------
def generate_summary(caption: str, objects: list) -> str:
    if not objects:
        return f"{caption} The scene appears natural and unposed."

    if len(objects) == 1:
        return f"{caption} The image mainly focuses on a {objects[0]} in a simple setting."

    if len(objects) <= 3:
        return (
            f"{caption} Visible elements include {', '.join(objects)}, "
            "arranged in a natural and realistic manner."
        )

    return (
        f"{caption} Several elements such as {', '.join(objects[:3])} "
        "are visible, contributing to a typical real-world scene."
    )


def generate_story(caption: str, objects: list) -> str:
    lower_objects = [o.lower() for o in objects]

    if not objects:
        return (
            f"{caption} The image documents a real moment as it appears, "
            "without any added interpretation or embellishment."
        )

    if "person" in lower_objects:
        return (
            f"{caption} The presence of people suggests an everyday activity. "
            "Nothing in the scene appears staged, and all elements seem naturally placed."
        )

    if any(o in ["laptop", "tv", "phone"] for o in lower_objects):
        return (
            f"{caption} The objects indicate a common indoor setting. "
            "The scene reflects routine use of everyday items in a realistic environment."
        )

    if any(o in ["tree", "building", "road"] for o in lower_objects):
        return (
            f"{caption} The outdoor elements appear unchanged and naturally occurring, "
            "capturing a straightforward view of the environment."
        )

    return (
        f"{caption} The image shows ordinary objects coexisting in a real setting, "
        "representing a simple moment as observed."
    )


# -------------------------
# Main analysis function
# -------------------------
def analyze_image(image_bytes: bytes) -> ImageAnalysisResponse:
    # Decode image for YOLO
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image")

    # YOLO detection
    results = yolo_model(img)

    objects = []
    confidences = {}

    for r in results:
        for cls, conf in zip(r.boxes.cls, r.boxes.conf):
            name = yolo_model.names[int(cls)]
            if name not in objects:
                objects.append(name)
                confidences[name] = float(conf)

    objects.sort(key=lambda x: confidences.get(x, 0), reverse=True)

    if not objects:
        objects = ["scene elements"]

    # BLIP caption (truth anchor)
    caption = generate_caption(image_bytes)

    # Grounded generation
    summary = generate_summary(caption, objects)
    story = generate_story(caption, objects)

    # Emotion inference
    emotion = determine_emotion(objects)

    return ImageAnalysisResponse(
        caption=caption,
        summary=summary,
        objects=objects,
        emotion=emotion,
        story=story
    )
