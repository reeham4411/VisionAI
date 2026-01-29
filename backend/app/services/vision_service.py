import cv2
import numpy as np
from ultralytics import YOLO
from app.schemas.response import ImageAnalysisResponse
import random

model = YOLO("yolov8n.pt")

# Emotion mapping based on objects
EMOTION_MAP = {
    'person': ['joyful', 'calm', 'contemplative'],
    'dog': ['playful', 'energetic', 'joyful'],
    'cat': ['peaceful', 'mysterious', 'calm'],
    'car': ['energetic', 'dynamic', 'busy'],
    'book': ['peaceful', 'contemplative', 'calm'],
    'phone': ['connected', 'busy', 'modern'],
    'laptop': ['productive', 'focused', 'busy'],
    'food': ['satisfied', 'appetizing', 'comforting'],
    'tree': ['peaceful', 'natural', 'serene'],
    'building': ['urban', 'structured', 'busy'],
    'bicycle': ['active', 'energetic', 'free'],
    'bird': ['peaceful', 'free', 'natural'],
}

def determine_emotion(objects: list) -> str:
    """Determine emotion based on detected objects"""
    if not objects:
        return "neutral"
    
    emotions = []
    for obj in objects:
        if obj.lower() in EMOTION_MAP:
            emotions.extend(EMOTION_MAP[obj.lower()])
    
    if emotions:
        return random.choice(emotions)
    
    # Default emotions based on number of objects
    if len(objects) > 5:
        return "chaotic"
    elif len(objects) > 2:
        return "busy"
    else:
        return "calm"

def generate_caption(objects: list) -> str:
    """Generate a natural caption from objects"""
    if not objects:
        return "An image showing a scene with various elements."
    
    if len(objects) == 1:
        return f"A scene featuring a {objects[0]}."
    elif len(objects) == 2:
        return f"An image showing a {objects[0]} and a {objects[1]}."
    elif len(objects) <= 4:
        obj_list = ", ".join(objects[:-1]) + f", and {objects[-1]}"
        return f"A scene with {obj_list}."
    else:
        main_objects = objects[:3]
        obj_list = ", ".join(main_objects)
        return f"A busy scene featuring {obj_list}, and more."

def generate_summary(objects: list, emotion: str) -> str:
    """Generate a rich summary based on objects and emotion"""
    if not objects:
        return "The image presents a scene with various elements.\nThe composition appears natural and balanced.\nIt captures a moment in time with clarity."
    
    # First line - what's in the image
    if len(objects) == 1:
        line1 = f"The image prominently features a {objects[0]}, capturing attention immediately."
    elif len(objects) <= 3:
        obj_str = " and ".join(objects)
        line1 = f"The scene showcases {obj_str} in a natural arrangement."
    else:
        main_objs = ", ".join(objects[:2])
        line1 = f"A dynamic composition featuring {main_objs}, along with {len(objects)-2} other elements."
    
    # Second line - atmosphere/mood
    mood_descriptions = {
        'joyful': "The atmosphere feels warm and uplifting, radiating positive energy.",
        'peaceful': "A sense of tranquility and calm pervades the entire scene.",
        'calm': "Everything appears serene and undisturbed, creating a soothing ambiance.",
        'energetic': "There's a palpable sense of movement and vitality throughout.",
        'chaotic': "The busy composition creates a sense of dynamic activity.",
        'mysterious': "An intriguing quality draws the viewer deeper into the frame.",
        'contemplative': "The scene invites quiet reflection and thoughtful observation.",
    }
    line2 = mood_descriptions.get(emotion, "The scene presents an interesting visual narrative.")
    
    # Third line - visual quality
    visual_quality = [
        "The lighting and composition work together harmoniously.",
        "Details are captured with clarity and precision.",
        "The frame is well-balanced and thoughtfully arranged.",
        "Natural elements blend seamlessly with the composition.",
    ]
    line3 = random.choice(visual_quality)
    
    # Fourth line - context/conclusion
    if 'person' in [o.lower() for o in objects]:
        line4 = "Human presence adds life and scale to the environment."
    elif any(obj in ['car', 'bus', 'truck', 'bicycle', 'motorcycle'] for obj in [o.lower() for o in objects]):
        line4 = "The presence of vehicles suggests urban activity and movement."
    elif any(obj in ['tree', 'plant', 'flower', 'grass'] for obj in [o.lower() for o in objects]):
        line4 = "Natural elements bring organic beauty to the frame."
    else:
        line4 = "Each element contributes to the overall visual story being told."
    
    return f"{line1}\n{line2}\n{line3}\n{line4}"

def generate_story(objects: list, emotion: str) -> str:
    """Generate a creative short story inspired by the scene"""
    if not objects:
        objects = ["various elements"]

    obj_lower = [o.lower() for o in objects]

   
    if 'person' in obj_lower:
        stories = [
            f"In this moment, someone pauses amidst the {objects[1] if len(objects) > 1 else 'surroundings'}.\n"
            "Time seems to slow as they take in their environment.\n"
            "Perhaps they're lost in thought, or simply appreciating the view.\n"
            "The world continues around them, but they remain still.\n"
            "It's a reminder that sometimes we need to stop and observe.\n"
            "These quiet moments often hold the most meaning.\n"
            "When they move on, they'll carry this scene with them.",

            f"A figure stands surrounded by {', '.join(objects[:2])}.\n"
            "Their presence transforms the ordinary into something memorable.\n"
            "The scene feels natural and unposed, as if captured mid-moment.\n"
            "Nothing dramatic is happening, yet the image feels complete.\n"
            "It reflects a slice of everyday life.\n"
            "Small moments like this often pass unnoticed.\n"
            "The camera preserves it in quiet detail.",
        ]

  
    elif any(obj in ['car', 'bus', 'truck', 'bicycle', 'motorcycle'] for obj in obj_lower):
        stories = [
            f"The {objects[0]} is positioned within its surroundings, ready for movement.\n"
            "It appears to be part of a typical daily setting.\n"
            "The scene suggests regular activity rather than a special event.\n"
            "Nothing feels rushed or staged.\n"
            "The environment supports the sense of everyday motion.\n"
            "This is a familiar sight in many places.\n"
            "The image captures a routine moment in time.",

            f"A vehicle rests quietly among {', '.join(objects[1:3]) if len(objects) > 1 else 'its environment'}.\n"
            "Its presence hints at travel, work, or daily routines.\n"
            "The scene feels practical and grounded.\n"
            "There is no sense of urgency.\n"
            "It represents movement paused briefly.\n"
            "Soon, the moment will pass.\n"
            "For now, it remains still within the frame.",
        ]

   
    elif any(obj in ['laptop', 'phone', 'tv', 'keyboard', 'mouse'] for obj in obj_lower):
        stories = [
            f"The image shows {', '.join(objects)} arranged in a familiar indoor setting.\n"
            "The objects suggest regular use rather than display.\n"
            "Everything appears intentionally placed.\n"
            "The environment feels functional and lived-in.\n"
            "The mood is {emotion} and steady.\n"
            "Nothing interrupts the scene.\n"
            "It reflects a common part of modern life.",

            f"A workspace comes into view, defined by {', '.join(objects[:2])}.\n"
            "The setup feels practical and purposeful.\n"
            "The scene suggests focus or routine.\n"
            "No dramatic action is taking place.\n"
            "It feels like a moment between tasks.\n"
            "The setting is familiar.\n"
            "A quiet snapshot of everyday productivity.",
        ]

   
    elif any(obj in ['dog', 'cat', 'bird'] for obj in obj_lower):
        stories = [
            f"The image captures {', '.join(objects)} within a calm environment.\n"
            "The animal appears comfortable in its surroundings.\n"
            "There is a sense of stillness in the scene.\n"
            "Nothing suggests sudden movement.\n"
            "The moment feels natural and unforced.\n"
            "It reflects a peaceful interaction with the environment.\n"
            "A simple, grounded scene.",

            f"A quiet moment features {objects[0]} as the main focus.\n"
            "The setting feels ordinary and familiar.\n"
            "The animal seems relaxed.\n"
            "No tension or excitement is visible.\n"
            "It is a snapshot of everyday life.\n"
            "Moments like these often go unnoticed.\n"
            "The image preserves it briefly.",
        ]

    
    elif any(obj in ['tree', 'plant', 'grass', 'building'] for obj in obj_lower):
        stories = [
            f"The image presents an outdoor scene containing {', '.join(objects)}.\n"
            "The elements appear naturally positioned.\n"
            "Nothing feels artificially arranged.\n"
            "The scene reflects a real-world environment.\n"
            "The mood is {emotion} and balanced.\n"
            "There is no central action.\n"
            "It captures a normal moment outdoors.",

            f"A quiet outdoor setting unfolds with {', '.join(objects[:2])} in view.\n"
            "The environment feels stable and familiar.\n"
            "Everything appears undisturbed.\n"
            "The scene could be encountered during a regular day.\n"
            "There is no sense of urgency.\n"
            "The moment feels grounded.\n"
            "A straightforward visual record.",
        ]

  
    else:
        stories = [
            f"Here lie {' and '.join(objects[:2])}, frozen in time by the lens.\n"
            "Each object has traveled its own path to be here.\n"
            "Manufactured, purchased, placed, or grown - all with their own origin.\n"
            "Now they exist together in this single frame.\n"
            "What stories would they tell if they could speak?\n"
            "How many hands have touched them, how many eyes seen them?\n"
            "In silence, they compose a visual poem of existence.",

            f"The scene unfolds with {', '.join(objects[:3])} taking center stage.\n"
            "Nature and human creation meet in unexpected harmony.\n"
            "Light plays across surfaces, revealing textures and forms.\n"
            "Time has passed, leaving subtle marks of its presence.\n"
            "Yet everything remains, persistent and patient.\n"
            "This is a world in miniature, complete unto itself.\n"
            "A single frame containing infinite stories waiting to be told.",
        ]

    return random.choice(stories)


def analyze_image(image_bytes: bytes):
    """
    Main analysis function using YOLO + rule-based NLP generation
    """
    # Convert bytes to image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image")

    # Run YOLO detection
    results = model(img)

    # Extract detected objects with confidence
    objects = []
    object_details = {}
    
    for r in results:
        for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
            obj_name = model.names[int(cls)]
            if obj_name not in objects:
                objects.append(obj_name)
                object_details[obj_name] = float(conf)
    
    # Sort objects by confidence
    objects.sort(key=lambda x: object_details.get(x, 0), reverse=True)

    # Fallback if nothing detected
    if not objects:
        objects = ["scene elements"]
        print("Warning: No objects detected by YOLO")

    print(f"Detected objects: {objects}")

    # Generate all outputs
    emotion = determine_emotion(objects)
    caption = generate_caption(objects)
    summary = generate_summary(objects, emotion)
    story = generate_story(objects, emotion)

    return ImageAnalysisResponse(
        caption=caption,
        summary=summary,
        objects=objects,
        emotion=emotion,
        story=story
    )