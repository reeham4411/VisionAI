import json
import re
from typing import Dict, Any


REQUIRED_KEYS = {"caption", "summary", "objects", "emotion", "story"}


class ModelResponseError(Exception):
    """Custom exception for invalid model output."""
    pass


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extracts JSON object from model output safely.
    Handles cases where model adds extra text.
    """
    try:
        # First attempt: direct JSON
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON using regex
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ModelResponseError("No JSON object found in model response.")

    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ModelResponseError(f"Invalid JSON structure: {str(e)}")


def validate_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures all required keys exist and are of correct type.
    """
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ModelResponseError(f"Missing required fields: {missing}")

    if not isinstance(data["objects"], list):
        raise ModelResponseError("Field 'objects' must be a list.")

    # Normalize data (optional safety)
    data["caption"] = str(data["caption"]).strip()
    data["summary"] = str(data["summary"]).strip()
    data["emotion"] = str(data["emotion"]).strip()
    data["story"] = str(data["story"]).strip()
    data["objects"] = [str(obj).strip() for obj in data["objects"]]

    return data


def parse_model_response(raw_text: str) -> Dict[str, Any]:
    """
    Main parser function used by vision_service.
    """
    parsed = extract_json(raw_text)
    validated = validate_response(parsed)
    return validated
