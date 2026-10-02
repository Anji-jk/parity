from __future__ import annotations
import cv2
from utils.align_images import align_images
from Pipeline.context import PipelineContext


def run(ctx: PipelineContext) -> bool:
  """STEP 1: Alignment & Homography Warp."""
  try:
    ctx.aligned_current_img = align_images(
        ctx.master_img, ctx.raw_current_img
    )
    print(
        "[PASS] Homography Alignment Successful (Image perspective rectified)."
    )
    return True
  except ValueError as e:
    print(f"[FAIL] Alignment failed ({e}). Halting pipeline.")
    if hasattr(ctx, "errors"):
      ctx.errors.append(str(e))
    ctx.halt = True
    return False