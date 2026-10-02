from __future__ import annotations
import os
import cv2
from utils.vlm import analyze_room_with_vlm, load_prompt
from Pipeline.utils.rules import get_room_rule
from Pipeline.context import PipelineContext
from Pipeline.config import BASELINES_DIR,MASTER_PROMPT_PATH


def run(ctx: PipelineContext) -> bool:
    """STEP 5: VLM Multimodal Visual Inspection."""
    print("\n--- VLM Visual Inspection ---")
    prompt_path = os.path.join("prompts", "master_prompt.txt")
    if os.path.exists(MASTER_PROMPT_PATH):
        base_prompt = load_prompt(MASTER_PROMPT_PATH)
    else:
        base_prompt = "Compare the CURRENT IMAGE against the baseline state established by the MASTER IMAGE and MASTER JSON."

    ctx.room_rule = get_room_rule(ctx.room_name)
    if ctx.room_rule:
        print(f"[INFO] Applied Room Rule for '{ctx.room_name}': {ctx.room_rule}")
        combined_prompt = (
            f"{base_prompt}\n\n### SPECIFIC ROOM RULES FOR"
            f" {ctx.room_name.upper()}\n{ctx.room_rule}"
        )
    else:
        combined_prompt = base_prompt

    if ctx.aligned_current_img is None:
        print("[VLM ERROR] No aligned image available for VLM inspection.")
        return False

    ref_img_path = os.path.join(BASELINES_DIR, f"{ctx.room_name}_ref.jpg")

    success, encoded_img = cv2.imencode(".jpg", ctx.aligned_current_img)
    if success:
        try:
            ctx.vlm_result = analyze_room_with_vlm(
                processed_image=encoded_img.tobytes(),
                master_image=ref_img_path,
                master_json=ctx.master_data,
                master_prompt=combined_prompt,
            )
            if hasattr(ctx.vlm_result, "summary"):
                print(f"[VLM SUMMARY] {ctx.vlm_result.summary}")
        except Exception as e:
            print(f"[VLM WARN] Inspection skipped or unavailable: {e}")
    else:
        print("[VLM ERROR] Failed to encode aligned image for VLM processing.")

    return True