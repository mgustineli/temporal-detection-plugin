# Video Detection Chart Plugin for FiftyOne

A [FiftyOne](https://github.com/voxel51/fiftyone) plugin that renders an interactive SVG line chart of per-frame detection counts in the modal view, with **bidirectional video sync**.

- **Video → Chart**: a blue vertical line tracks the current video frame in real time during playback
- **Chart → Video**: click or drag anywhere on the chart to seek the video to that frame

![gif](video-detection-chart-plugin.gif)

## Installation

```shell
fiftyone plugins download https://github.com/mgustineli/video-detection-chart-plugin
```

## Operators

### Get Detection Counts

Returns per-frame detection counts for a sample. Called internally by the JS panel — not intended for direct use (unlisted).

## Panel

### Detection Count Plot (Interactive)

Opens in the modal view alongside the video player. Shows a line chart with:

- **Line + area fill** of detection counts per frame
- **Blue frame indicator** (vertical line + dot + count label) tracking the current frame
- **Click/drag to seek** — click anywhere on the chart or drag to scrub through frames
- **Status bar** showing frame number, FPS, and play/pause state

## Usage

1. Open the FiftyOne App and load a **video dataset** with frame-level detections
2. Open a sample in the modal view
3. Open the panel via the **+** button and select **"Detection Count Plot (Interactive)"**
4. Play the video — the blue vertical line tracks the current frame
5. Click or drag on the chart to seek the video to any frame

## How It Works

The plugin is a hybrid Python + JS implementation:

- **Python** (`__init__.py`): `GetDetectionCounts` operator queries frame-level detection counts from the dataset
- **JavaScript** (`index.umd.js`): Hand-written UMD panel (no build step) renders an SVG chart and syncs with the video player

**Video → Chart sync** uses `modalLooker.subscribeToState("frameNumber", callback)` to receive frame updates during playback.

**Chart → Video sync** uses three `modalLooker` methods:

1. `modalLooker.getVideo()` — accesses the `<video>` element (not in the regular DOM)
2. `modalLooker.updater({frameNumber})` — syncs the looker's internal state
3. `modalLooker.pause()` — pauses playback at the seeked frame

For a detailed technical walkthrough, see [PLUGIN_IMPLEMENTATION.md](PLUGIN_IMPLEMENTATION.md).

## Requirements

- FiftyOne >= 0.21.0
- Video dataset with frame-level detections (e.g., `frames.detections`)
