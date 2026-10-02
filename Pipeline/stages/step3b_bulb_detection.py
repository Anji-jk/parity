from __future__ import annotations
import os
import cv2
from Pipeline.context import PipelineContext
from Pipeline.modules.bulbs.detector import BulbDetector

_BULB_DETECTOR: BulbDetector | None = None


def get_bulb_detector() -> BulbDetector:
  global _BULB_DETECTOR
  if _BULB_DETECTOR is None:
    _BULB_DETECTOR = BulbDetector()
  return _BULB_DETECTOR


def run(ctx: PipelineContext) -> bool:
  """STEP 3b: Bulb Detection & Lighting Discrepancy Verification."""
  # Use raw_current_img to prevent warped black border artifacts
  target_img = (
      ctx.raw_current_img
      if ctx.raw_current_img is not None
      else ctx.aligned_current_img
  )
  if target_img is None:
    return False

  detector = getattr(ctx, "bulb_engine", None) or get_bulb_detector()

  bulb_result = detector.detect_bulbs(target_img)

  current_count = bulb_result.get("count", 0)
  baseline_count = ctx.master_data.get("bulb_count", 0)

  ctx.current_bulb_count = current_count
  ctx.baseline_bulb_count = baseline_count
  ctx.bulb_detections = bulb_result.get("detections", [])

  print(
      f"[INFO] Active Bulbs Detected: {current_count} (Baseline:"
      f" {baseline_count})"
  )

  # Save visual inspection locally before step 5 runs
  annotated_frame = bulb_result.get("annotated_frame")
  if annotated_frame is not None:
    out_dir = "output_images"
    os.makedirs(out_dir, exist_ok=True)
    room_tag = getattr(ctx, "room_name", "room")
    save_path = os.path.join(out_dir, f"{room_tag}_bulbs_annotated.jpg")
    cv2.imwrite(save_path, annotated_frame)
    print(
        f"[INFO] Bulb detection visual saved to: {save_path} ({current_count}"
        " bulb(s) marked)"
    )

  return True