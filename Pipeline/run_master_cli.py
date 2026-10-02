"""
Owner Master Registration CLI (Bulk GUI File Picker)
Opens a native file explorer window to let the owner multi-select room photos
and register all baselines in a single cached execution.
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog

# Ensure repository root is on sys.path
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(PIPELINE_DIR)
for p in (REPO_ROOT, PIPELINE_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from Pipeline.config import MASTER_DIR, BASELINES_DIR, TESTING_DIR
from Pipeline.entrypoints.master_service import process_master_image, get_engines


def open_bulk_file_dialog(initial_dir: str) -> list[str]:
    """Opens a native multi-select file explorer dialog."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    start_dir = initial_dir if os.path.isdir(initial_dir) else os.getcwd()

    print("[INFO] Opening File Explorer window... Hold Ctrl/Shift to select multiple images.")
    file_paths = filedialog.askopenfilenames(
        title="Select Master Baseline Images (Bulk Select)",
        initialdir=start_dir,
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png *.webp"),
            ("All Files", "*.*"),
        ],
    )
    root.destroy()
    return list(file_paths) if file_paths else []


def main():
    print("\n" + "=" * 60)
    print(" 🏢 OWNER MASTER BASELINE REGISTRATION (BULK UPLOAD)")
    print("=" * 60)

    # 1. Open multi-select file dialog
    selected_image_paths = open_bulk_file_dialog(MASTER_DIR)

    if not selected_image_paths:
        print("\n[CANCELLED] No files were selected. Exiting.")
        return

    print(f"\n[SELECTED] {len(selected_image_paths)} image(s) selected for registration:")
    for idx, path in enumerate(selected_image_paths, start=1):
        filename = os.path.basename(path)
        room_name = os.path.splitext(filename)[0]
        print(f"  [{idx}] {filename} -> Room: '{room_name}'")

    confirm = input("\nProceed with batch baseline registration? (Y/n): ").strip().lower()
    if confirm and confirm != "y":
        print("[ABORTED] Registration cancelled by user.")
        return

    # 2. Warm up engines once before looping
    print("\n[INIT] Initializing shared vision models (YOLO & CLIP)...")
    get_engines()

    # 3. Process each image sequentially
    results = []
    print("\n" + "=" * 60)
    print(" ⚙️ PROCESSING BATCH REGISTRATIONS")
    print("=" * 60)

    for idx, img_path in enumerate(selected_image_paths, start=1):
        filename = os.path.basename(img_path)
        room_name = os.path.splitext(filename)[0]

        print(f"\n[{idx}/{len(selected_image_paths)}] Processing '{room_name}' ({filename})...")
        try:
            baseline_data = process_master_image(
                image_input=img_path,
                room_name=room_name,
                output_baseline_dir=BASELINES_DIR,
                export_annotated_dir=TESTING_DIR,
            )
            bulb_count = baseline_data.get("bulb_count", 0)
            results.append((room_name, "SUCCESS", f"{bulb_count} bulbs"))
        except Exception as exc:
            print(f"[ERROR] Failed processing '{room_name}': {exc}")
            results.append((room_name, "FAILED", str(exc)))

    # 4. Display final batch summary
    print("\n" + "=" * 60)
    print(" 📊 BATCH REGISTRATION SUMMARY")
    print("=" * 60)
    for room_name, status, details in results:
        icon = "✅" if status == "SUCCESS" else "❌"
        print(f"  {icon} {room_name:<20} : {status:<8} ({details})")
    print(f"\nAll baselines saved to: {BASELINES_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()