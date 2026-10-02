"""
Local Pipeline Verification Script
Tests both the Master Registration and Worker Capture Audit workflows.
"""
import os
import sys

# Ensure repository root is on Python path
CURRENT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR_PATH)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from Pipeline.config import MASTER_DIR, CURRENT_DIR, BASELINES_DIR
from Pipeline.entrypoints.master_service import process_master_image
from Pipeline.entrypoints.inference_service import evaluate_worker_capture


def run_pipeline_test():
    print("\n" + "=" * 60)
    print(" 🚀 STARTING LOCAL PIPELINE VERIFICATION TEST")
    print("=" * 60)
    print(f"[PATH CHECK] Master images dir : {MASTER_DIR}")
    print(f"[PATH CHECK] Current images dir: {CURRENT_DIR}")
    print(f"[PATH CHECK] Baselines dir     : {BASELINES_DIR}")

    if not os.path.isdir(MASTER_DIR):
        print(f"\n[ERROR] Could not find folder 'master_images' at {MASTER_DIR}")
        print("Please verify where your sample master images are stored.")
        return

    # ---------------------------------------------------------
    # TEST 1: Master Baseline Registration (Owner Flow)
    # ---------------------------------------------------------
    print("\n[TEST 1/2] Testing Master Baseline Registration...")

    valid_files = [f for f in os.listdir(MASTER_DIR) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    if not valid_files:
        print(f"[FAIL] No images found inside '{MASTER_DIR}'.")
        return

    # Prefer Bathroom_Light if present, otherwise pick the first image
    if "Bathroom_Light.jpg" in valid_files:
        chosen_file = "Bathroom_Light.jpg"
    else:
        chosen_file = valid_files[0]

    test_room = os.path.splitext(chosen_file)[0]
    master_image_path = os.path.join(MASTER_DIR, chosen_file)

    print(f" -> Processing master image: {master_image_path}")
    baseline_data = process_master_image(
        image_input=master_image_path,
        room_name=test_room,
        output_baseline_dir=BASELINES_DIR,
        export_annotated_dir="Testing"
    )

    assert baseline_data is not None, "Failed to generate baseline data"
    assert "bulb_count" in baseline_data, "Baseline data missing bulb_count"
    print(f"[PASS] Master baseline generated successfully for '{test_room}'!")
    print(f"       Active Bulbs: {baseline_data['bulb_count']}")

    # ---------------------------------------------------------
    # TEST 2: Worker Capture Audit (Worker Flow)
    # ---------------------------------------------------------
    print("\n[TEST 2/2] Testing Worker Capture Audit...")

    worker_image_path = os.path.join(CURRENT_DIR, chosen_file)
    if not os.path.exists(worker_image_path):
        valid_curr = [f for f in os.listdir(CURRENT_DIR) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        if not valid_curr:
            print(f"[FAIL] No test images found in '{CURRENT_DIR}'.")
            return
        worker_image_path = os.path.join(CURRENT_DIR, valid_curr[0])
        test_room = os.path.splitext(valid_curr[0])[0]

    print(f" -> Auditing worker image: {worker_image_path}")
    audit_report = evaluate_worker_capture(
        current_image_input=worker_image_path,
        room_name=test_room,
        baseline_dir=BASELINES_DIR,
        output_dir="output_images"
    )

    assert audit_report is not None, "Failed to generate audit report"
    print(f"[PASS] Worker capture audit completed successfully!")
    print(f"       Verdict:       {audit_report.get('verdict')}")
    print(f"       SSIM Score:    {audit_report.get('ssim_score'):.2f}")
    print(f"       Active Bulbs:  {audit_report.get('active_bulbs')} (Expected: {audit_report.get('expected_bulbs')})")
    print(f"       Checklist:     {audit_report.get('checklist')}")

    print("\n" + "=" * 60)
    print(" 🎉 ALL PIPELINE LOCAL TESTS COMPLETED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_pipeline_test()