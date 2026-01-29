def build_prompt():
    return """
You are an intelligent vision assistant.

Analyze the image and return STRICT JSON with these fields:

{
  "caption": "One sentence factual caption",
  "summary": "3–5 lines describing the scene",
  "objects": ["list", "of", "detected", "objects"],
  "emotion": "overall emotional tone",
  "story": "5–10 line short narrative inspired by the image"
}

Rules:
- Be factual for caption & summary
- Story must be imaginative but scene-consistent
- Objects must be visible in image
- Emotion must reflect the scene
- Do NOT include markdown
"""
