"""Detection Count Chart Plugin

Interactive SVG chart panel showing per-frame detection counts with
bidirectional video sync. Click or drag on the chart to seek the video.

Panels (JS — registered in index.umd.js):
  - DetectionCountPlotInteractive — SVG chart with bidirectional video sync

Operators:
  - get_detection_counts — returns per-frame detection counts for a sample
"""

import fiftyone.operators as foo
import fiftyone.operators.types as types


class GetDetectionCounts(foo.Operator):
    """Returns per-frame detection counts for a sample.

    Called from the JS panel to load chart data.
    """

    @property
    def config(self):
        return foo.OperatorConfig(
            name="get_detection_counts",
            label="Get Detection Counts",
            unlisted=True,
        )

    def resolve_input(self, ctx):
        inputs = types.Object()
        inputs.str("sample_id", required=True)
        return types.Property(inputs)

    def execute(self, ctx):
        sample_id = ctx.params.get("sample_id")
        if not sample_id:
            return {}

        try:
            sample = ctx.dataset[sample_id]

            fps = sample.metadata.frame_rate if sample.metadata else 30
            total_frames = (
                sample.metadata.total_frame_count if sample.metadata else 0
            )

            sample_view = ctx.dataset.select(sample_id)
            frame_numbers = sample_view.values("frames.frame_number")[0]
            det_lists = sample_view.values("frames.detections.detections")[0]
            counts = [len(d) if d else 0 for d in det_lists]

            ctx.ops.notify(f"Loaded {len(frame_numbers)} frames")

            return {
                "frames": frame_numbers,
                "counts": counts,
                "fps": fps,
                "total_frames": total_frames,
            }
        except Exception as e:
            print(f"[GetDetectionCounts] Error: {e}")
            return {"error": str(e)}


def register(p):
    p.register(GetDetectionCounts)
