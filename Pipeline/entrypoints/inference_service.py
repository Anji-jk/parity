"""
Worker Inference Service
Audits runtime room captures against registered baselines and paints visual discrepancy annotations.
"""
from __future__ import annotations
import os
import json
import cv2
import numpy as np

from Pipeline.config import BASELINES_DIR, OUTPUT_DIR
from Pipeline.context import PipelineContext
from Pipeline.runner import PipelineRunner
from Pipeline.utils.model import load_yolo

_RUNNER: PipelineRunner | None = None
_YOLO_MODEL = None


def get_inference_engines():
    global _RUNNER, _YOLO_MODEL
    if _RUNNER is None:
        print("[INIT] Loading PipelineRunner engine...")
        _RUNNER = PipelineRunner()
    if _YOLO_MODEL is None:
        print("[INIT] Loading YOLO furniture model into memory...")
        _YOLO_MODEL = load_yolo("yolov8l.pt")
    return _RUNNER, _YOLO_MODEL


def draw_discrepancy_annotations(ctx: PipelineContext) -> np.ndarray:
    """
    Paints all detected issues directly onto the image:
    1. Active bulbs in GREEN.
    2. Expected bulbs that are TURNED OFF in RED (with 4-corner perspective warp).
    3. An on-screen HUD badge listing all discrepancies.
    """
    canvas = (
        ctx.raw_current_img.copy()
        if ctx.raw_current_img is not None
        else (ctx.aligned_current_img.copy() if ctx.aligned_current_img is not None else None)
    )
    if canvas is None:
        return np.zeros((480, 640, 3), dtype=np.uint8)

    h, w = canvas.shape[:2]

    # 1. Draw Active Bulbs in GREEN
    for bulb in ctx.bulb_detections:
        bbox = bulb.get("draw_bbox") or bulb.get("bbox", [])
        if len(bbox) == 4:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            conf = bulb.get("confidence", 1.0)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                canvas,
                f"Bulb ON ({conf*100:.0f}%)",
                (x1, max(18, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

    # 2. Draw Inactive Expected Bulbs in RED (if lights are off)
    expected_bulbs = ctx.master_data.get("bulb_detections") or ctx.master_data.get("bulbs", [])
    if ctx.current_bulb_count < ctx.baseline_bulb_count and expected_bulbs:
        H_inv = None
        if ctx.homography_matrix is not None:
            try:
                H_inv = np.linalg.inv(ctx.homography_matrix)
            except Exception:
                H_inv = None

        for b_idx, m_bulb in enumerate(expected_bulbs, start=1):
            m_box = m_bulb.get("bbox", [])
            if len(m_box) == 4:
                bx1, by1, bx2, by2 = m_box
                
                # Transform all 4 bounding box corners through homography
                if H_inv is not None:
                    corners = np.float32([
                        [[bx1, by1]],
                        [[bx2, by1]],
                        [[bx2, by2]],
                        [[bx1, by2]],
                    ])
                    warped = cv2.perspectiveTransform(corners, H_inv)
                    rx1 = int(np.min(warped[:, 0, 0]))
                    ry1 = int(np.min(warped[:, 0, 1]))
                    rx2 = int(np.max(warped[:, 0, 0]))
                    ry2 = int(np.max(warped[:, 0, 1]))
                else:
                    rx1, ry1, rx2, ry2 = int(bx1), int(by1), int(bx2), int(by2)

                rx1, ry1 = max(0, min(w - 1, rx1)), max(0, min(h - 1, ry1))
                rx2, ry2 = max(0, min(w - 1, rx2)), max(0, min(h - 1, ry2))

                # Skip degenerate transformed boxes
                if rx2 <= rx1 or ry2 <= ry1:
                    continue

                # Draw bold red box indicating OFF light
                cv2.rectangle(canvas, (rx1, ry1), (rx2, ry2), (0, 0, 255), 3)
                label_txt = f"LIGHT OFF #{b_idx}"
                (lw, lh), _ = cv2.getTextSize(label_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(canvas, (rx1, max(0, ry1 - lh - 6)), (rx1 + lw + 6, ry1), (0, 0, 255), -1)
                cv2.putText(
                    canvas,
                    label_txt,
                    (rx1 + 3, max(14, ry1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

    # 3. Overlay Discrepancy Checklist HUD Box on the top-left
    hud_items = []
    if ctx.current_bulb_count < ctx.baseline_bulb_count:
        off_count = ctx.baseline_bulb_count - ctx.current_bulb_count
        hud_items.append(f"LIGHTS OFF: {off_count} inactive")
    for missing in set(ctx.missing_items):
        hud_items.append(f"MISSING: {missing}")
    for drift in ctx.drift_alerts:
        hud_items.append(f"DRIFT: {drift}")
    for clutter in set(ctx.clutter_items):
        hud_items.append(f"CLUTTER: {clutter}")

    if hud_items:
        badge_w = min(w - 20, 380)
        badge_h = 35 + len(hud_items) * 22
        overlay = canvas.copy()
        cv2.rectangle(overlay, (10, 10), (10 + badge_w, 10 + badge_h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)

        verdict_color = (0, 0, 255) if ctx.verdict == "REJECTED" else (0, 255, 0)
        cv2.putText(
            canvas,
            f"VERDICT: {ctx.verdict}",
            (20, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            verdict_color,
            2,
            cv2.LINE_AA,
        )

        for idx, item in enumerate(hud_items):
            cv2.putText(
                canvas,
                f"! {item}",
                (20, 56 + idx * 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    return canvas


def evaluate_worker_capture(
    current_image_input: str | np.ndarray | bytes,
    room_name: str,
    baseline_dir: str = BASELINES_DIR,
    output_dir: str = OUTPUT_DIR,
) -> dict:
    runner, model = get_inference_engines()

    json_path = os.path.join(baseline_dir, f"{room_name}_baseline.json")
    ref_img_path = os.path.join(baseline_dir, f"{room_name}_ref.jpg")

    if not os.path.exists(json_path) or not os.path.exists(ref_img_path):
        raise FileNotFoundError(f"Missing baseline files for room '{room_name}' in {baseline_dir}")

    with open(json_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    master_img = cv2.imread(ref_img_path)

    # Handle path, raw bytes, or numpy array
    if isinstance(current_image_input, str):
        raw_current_img = cv2.imread(current_image_input)
        filename = os.path.basename(current_image_input)
        img_path = current_image_input
    elif isinstance(current_image_input, bytes):
        raw_current_img = cv2.imdecode(np.frombuffer(current_image_input, np.uint8), cv2.IMREAD_COLOR)
        filename = f"{room_name}_capture.jpg"
        img_path = "in_memory"
    else:
        raw_current_img = current_image_input
        filename = f"{room_name}_capture.jpg"
        img_path = "in_memory"

    if raw_current_img is None or raw_current_img.size == 0:
        raise ValueError(f"Could not load valid image from input: {current_image_input}")

    # Build context
    ctx = PipelineContext(
        room_name=room_name,
        raw_current_img=raw_current_img,
        master_img=master_img,
        master_data=master_data,
        model=model,
        img_path=img_path,
        filename=filename,
    )

    # Run pipeline stages
    ctx = runner.run(ctx)

    # Paint visual annotations
    annotated_canvas = draw_discrepancy_annotations(ctx)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{room_name}_annotated_result.jpg")
    cv2.imwrite(out_path, annotated_canvas)
    print(f"[SAVED] Inspection visual written to: {out_path}")
    print(f"[VERDICT] Status: {ctx.verdict}")

    # Provide lighting_delta directly from ctx (fallback to brightness_diff if set)
    l_delta = getattr(ctx, "lighting_delta", 0.0) or getattr(ctx, "brightness_diff", 0.0)

    return {
        "room_name": ctx.room_name,
        "verdict": ctx.verdict,
        "ssim_score": ctx.ssim_score,
        "lighting_delta": l_delta,
        "active_bulbs": ctx.current_bulb_count,
        "expected_bulbs": ctx.baseline_bulb_count,
        "checklist": ctx.reset_checklist,
        "annotated_image_path": out_path,
    }