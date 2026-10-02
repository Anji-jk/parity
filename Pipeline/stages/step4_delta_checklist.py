from __future__ import annotations
import math
from Pipeline.config import MAX_DRIFT_PIXELS
from Pipeline.context import PipelineContext


def run(ctx: PipelineContext) -> bool:
  """STEP 4: Delta Calculations (Inventory Missing, Drift, Clutter)."""
  master_objs = ctx.master_data.get("objects", [])
  current_objs = ctx.current_data.get("objects", []).copy()
  matched_master = []
  ctx.drift_alerts = []

  for m_obj in master_objs:
    best_match_idx = None
    min_dist = float("inf")

    for idx, c_obj in enumerate(current_objs):
      if m_obj["label"] == c_obj["label"]:
        dist = math.hypot(
            m_obj["centroid"][0] - c_obj["centroid"][0],
            m_obj["centroid"][1] - c_obj["centroid"][1],
        )
        if dist < min_dist:
          min_dist = dist
          best_match_idx = idx

    if best_match_idx is not None:
      c_obj = current_objs.pop(best_match_idx)
      matched_master.append(m_obj)
      if min_dist > MAX_DRIFT_PIXELS:
        ctx.drift_alerts.append(
            f"{m_obj['label'].capitalize()} shifted {int(min_dist)}px"
        )

  ctx.missing_items = [
      obj["label"] for obj in master_objs if obj not in matched_master
  ]
  ctx.clutter_items = [obj["label"] for obj in current_objs]

  checklist = []
  print("\n--- Reset Checklist ---")
  if not ctx.missing_items:
    checklist.append("[OK] All required room items present.")
  else:
    for item in set(ctx.missing_items):
      msg = f"[MISSING] {ctx.missing_items.count(item)} x {item}"
      checklist.append(msg)
      print(msg)

  if not ctx.drift_alerts:
    checklist.append("[OK] Furniture positions verified.")
  else:
    for alert in ctx.drift_alerts:
      msg = f"[DRIFT] {alert}"
      checklist.append(msg)
      print(msg)

  if not ctx.clutter_items:
    checklist.append("[OK] Room is clean (No clutter detected).")
  else:
    for item in set(ctx.clutter_items):
      msg = f"[CLUTTER] Remove {ctx.clutter_items.count(item)} x {item}"
      checklist.append(msg)
      print(msg)

  # Bulb status
  current_bulbs = getattr(ctx, "current_bulb_count", 0)
  baseline_bulbs = getattr(ctx, "baseline_bulb_count", 0)

  if current_bulbs == baseline_bulbs:
    checklist.append(
        f"[OK] Bulb status verified: All {current_bulbs} expected light(s) are"
        " active."
    )
  elif current_bulbs < baseline_bulbs:
    turned_off = baseline_bulbs - current_bulbs
    checklist.append(
        f"[LIGHTS OFF] {turned_off} expected light source(s) appear inactive or"
        " turned off."
    )
  else:
    extra = current_bulbs - baseline_bulbs
    checklist.append(
        f"[EXTRA LIGHTS] {extra} unexpected active light source(s) detected."
    )

  ctx.reset_checklist = checklist

  # Pass/Fail determination
  is_rejected = (current_bulbs < baseline_bulbs) or (len(ctx.missing_items) > 0)
  ctx.verdict = "REJECTED" if is_rejected else "OK"

  return True