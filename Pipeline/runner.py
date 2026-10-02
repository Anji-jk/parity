from __future__ import annotations
from typing import Any, Callable
from Pipeline.context import PipelineContext

# Import stages directly from their respective files to avoid circular imports:
from Pipeline.stages.step1_alignment import run as run_step1
from Pipeline.stages.step2_feature_extraction import run as run_step2
from Pipeline.stages.step3_ssim_lighting import run as run_step3
from Pipeline.stages.step3b_bulb_detection import run as run_step3b
from Pipeline.stages.step4_delta_checklist import run as run_step4
from Pipeline.stages.step5_vlm_inspection import run as run_step5

StepCallable = Callable[[PipelineContext], bool]


class PipelineRunner:
    """Pluggable pipeline execution engine."""

    def __init__(self, steps: list[Any] | None = None):
        self.steps: list[StepCallable] = []
        default_steps = steps or [
            run_step1,
            run_step2,
            run_step3,
            run_step3b,
            run_step4,
            run_step5,
        ]
        for step in default_steps:
            self.register_step(step)

    def register_step(self, step: Any) -> None:
        """Registers a step function or module with a run() method."""
        if hasattr(step, "run") and callable(step.run):
            self.steps.append(step.run)
        elif callable(step):
            self.steps.append(step)
        else:
            raise ValueError(f"Step {step} must be a callable or a module with a run() function.")

    def _get_step_label(self, step_fn: StepCallable) -> str:
        module_name = getattr(step_fn, "__module__", "")

        name_map = {
            "step1_alignment": "Image Alignment & Homography",
            "step2_feature_extraction": "Object & Feature Extraction",
            "step3_ssim_lighting": "Lighting & SSIM Comparison",
            "step3b_bulb_detection": "Bulb & Fixture Verification",
            "step4_delta_checklist": "Delta & Inventory Checklist",
            "step5_vlm_inspection": "Multimodal VLM Visual Inspection",
        }

        for key, display_name in name_map.items():
            if key in module_name:
                return display_name

        return getattr(step_fn, "__name__", "Processing Step").replace("_", " ").title()

    def run(self, ctx: PipelineContext) -> PipelineContext:
        """Executes registered pipeline steps sequentially."""
        for step_fn in self.steps:
            step_name = self._get_step_label(step_fn)

            if getattr(ctx, "halt", False):
                print(f"\n[PIPELINE ABORTED] Inspection stopped early.")
                break

            success = step_fn(ctx)

            if not success or getattr(ctx, "halt", False):
                ctx.halt = True
                print("\n" + "=" * 55)
                print(f"[PIPELINE STOPPED] Verification failed at: {step_name}")
                errors = getattr(ctx, "errors", [])
                if errors:
                    print(f"Reason: {errors[-1]}")
                print("Downstream verification skipped.")
                print("=" * 55 + "\n")
                break

        return ctx