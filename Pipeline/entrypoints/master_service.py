"""Local Master Registration Engine (No Cloud / S3 dependencies)

Processes owner golden reference images locally on disk:
- Generates baselines/<room>_baseline.json
- Saves baselines/<room>_ref.jpg
- Optionally exports annotated visual detections to Testing/<room>_annotated.jpg
"""

import os
import json
import cv2
import numpy as np

from Pipeline.utils.model import load_yolo
from Pipeline.utils.features import extract_features
from Pipeline.modules.bulbs.detector import BulbDetector
from Pipeline.config import MASTER_DIR, BASELINES_DIR, VALID_EXTENSIONS

# ---------------------------------------------------------------------------
# Global Engine Cache (Avoids re-loading CLIP & YOLO weights on every request)
# ---------------------------------------------------------------------------
_BULB_ENGINE: BulbDetector | None = None
_YOLO_MODEL = load_yolo("yolov8l.pt")


def get_engines() -> tuple[BulbDetector, any]:
    """Initializes or retrieves cached detector models."""
    global _BULB_ENGINE, _YOLO_MODEL

    if _BULB_ENGINE is None:
        print("[INIT] Loading Bulb Detector & CLIP VLM weights into memory...")
        _BULB_ENGINE = BulbDetector()

    if _YOLO_MODEL is None:
        print("[INIT] Loading YOLO model weights into memory...")
        _YOLO_MODEL = load_yolo()

    return _BULB_ENGINE, _YOLO_MODEL


def process_master_image(
    image_input: str | np.ndarray,
    room_name: str,
    output_baseline_dir: str = BASELINES_DIR,
    export_annotated_dir: str | None = "Testing",
) -> dict:
    """Processes a single owner room image and writes local baseline artifacts.

    Args:
        image_input: Local file path string OR already-loaded cv2 numpy array.
        room_name: Name of the room/space (e.g. "Bathroom", "Table 1").
        output_baseline_dir: Folder to save `<room>_baseline.json` &
          `<room>_ref.jpg`.
        export_annotated_dir: Optional folder to save visual detection check.

    Returns:
        dict: The complete baseline metadata dictionary.
    """
    os.makedirs(output_baseline_dir, exist_ok=True)
    bulb_engine, model = get_engines()

    # 1. Load image if path provided
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Master image not found: {image_input}")
        img_path = image_input
        img = cv2.imread(img_path)
    else:
        img = image_input
        img_path = None

    if img is None or img.size == 0:
        raise ValueError(f"Could not load valid image for room: {room_name}")

    # 2. Extract keypoints and furniture baseline data
    # (If using a path, pass img_path; otherwise pass img directly if extract_features supports it)
    if img_path:
        data, _ = extract_features(img_path, model)
    else:
        data, _ = extract_features(img, model)

    # 3. Detect and verify baseline active light sources
    bulb_res = bulb_engine.detect_bulbs(img)
    data["room_name"] = room_name
    data["bulb_count"] = bulb_res.get("count", 0)
    data["bulb_detections"] = bulb_res.get("detections", [])

    # 4. Save local baseline artifacts
    ref_out_path = os.path.join(output_baseline_dir, f"{room_name}_ref.jpg")
    json_out_path = os.path.join(
        output_baseline_dir, f"{room_name}_baseline.json"
    )

    cv2.imwrite(ref_out_path, img)
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # 5. Optional: Save annotated visual check locally (for immediate inspection)
    if export_annotated_dir and bulb_res.get("annotated_frame") is not None:
        os.makedirs(export_annotated_dir, exist_ok=True)
        ann_out_path = os.path.join(
            export_annotated_dir, f"{room_name}_annotated.jpg"
        )
        cv2.imwrite(ann_out_path, bulb_res["annotated_frame"])

    print(
        f"[SUCCESS] Baseline created for '{room_name}' (Active Bulbs: {data['bulb_count']})"
    )
    return data


def generate_all_baselines(master_dir: str = MASTER_DIR):
    """Batch processes all master images found in the local master_images folder."""
    if not os.path.isdir(master_dir):
        print(f"[ERROR] Directory '{master_dir}' does not exist.")
        return

    images = [
        f for f in os.listdir(master_dir) if f.lower().endswith(VALID_EXTENSIONS)
    ]
    print(
        f"[INFO] Found {len(images)} master images in '{master_dir}' to process."
    )

    for img_name in images:
        room_name = os.path.splitext(img_name)[0]
        img_path = os.path.join(master_dir, img_name)
        process_master_image(image_input=img_path, room_name=room_name)


if __name__ == "__main__":
    generate_all_baselines()