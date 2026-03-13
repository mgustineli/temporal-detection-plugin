# Detection Count Plot — Plugin Implementation Guide

## Overview

A hybrid Python + JS FiftyOne plugin that renders an interactive SVG line chart of per-frame detection counts in the modal view, with **bidirectional video sync**:

- **Video → Chart**: a red vertical line on the chart tracks the current video frame in real time
- **Chart → Video**: clicking or dragging on the chart seeks the video to that frame

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  FiftyOne App (Browser)                                 │
│                                                         │
│  ┌──────────────┐    Recoil atom     ┌───────────────┐  │
│  │ Video Player │───(modalLooker)───→│ JS Panel      │  │
│  │              │                    │ (index.umd.js)│  │
│  │              │←── getVideo() ─────│               │  │
│  │              │←── updater()  ─────│               │  │
│  │              │←── pause()   ──────│               │  │
│  └──────────────┘                    └───────┬───────┘  │
│                                              │          │
│                              useOperatorExecutor()      │
│                                              │          │
│  ┌───────────────────────────────────────────▼───────┐  │
│  │  Python Operator (GetDetectionCounts)             │  │
│  │  __init__.py                                      │  │
│  │  Returns {frames, counts, fps, total_frames}      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
plugin/
├── __init__.py      # Python panels + operator
├── index.umd.js     # JS panel (hand-written UMD, no build step)
├── fiftyone.yml     # Plugin manifest
└── package.json     # Points FiftyOne to index.umd.js
```

## Key Components

### 1. Python Operator — `GetDetectionCounts` (`__init__.py`)

Called from the JS panel via `useOperatorExecutor`. Loads per-frame detection counts for a given sample.

```python
def execute(self, ctx):
    sample = ctx.dataset[sample_id]
    frame_numbers = sample_view.values("frames.frame_number")[0]
    det_lists = sample_view.values("frames.detections.detections")[0]
    counts = [len(d) if d else 0 for d in det_lists]
    return {"frames": frame_numbers, "counts": counts, "fps": fps, "total_frames": total_frames}
```

### 2. JS Panel — `DetectionCountPlotInteractive` (`index.umd.js`)

Hand-written UMD module (no JSX, no build step). Uses `React.createElement` directly. Accesses FiftyOne internals via window globals:

| Global | Purpose |
|--------|---------|
| `__fos__` | Recoil atoms — `modalSampleId`, `modalLooker`, ImaVid state |
| `__foo__` | Operator execution — `useOperatorExecutor()` |
| `__fop__` | Plugin registration — `registerComponent()` |
| `__mui__` | MUI components — `Box`, `Typography`, `CircularProgress` |

#### Component Hierarchy

```
DetectionCountPlotPanel (main component)
├── useVideoState()          — reads frame number + playing state
├── useOperatorExecutor()    — loads detection data from Python
├── SVGChart                 — pure SVG rendering + mouse interaction
└── Status Bar               — frame counter, FPS, play/pause indicator
```

## Bidirectional Sync — How It Works

### Video → Chart (reading state)

Uses the **`modalLooker`** object from Recoil (`fos.modalLooker`). The `useVideoState` hook subscribes to live frame updates:

```js
// The modalLooker is the video player's looker instance, shared via Recoil
var modalLooker = useRecoilValue(fos.modalLooker);

// Subscribe to frame number changes (fires on every frame during playback)
modalLooker.subscribeToState("frameNumber", function(v) {
    // Update chart's red vertical line position
});

// Also subscribe to play/pause state
modalLooker.subscribeToState("playing", function(v) { ... });
```

Supports both regular video and ImaVid (image-as-video) modes via feature detection.

### Chart → Video (seeking)

This was the hardest part. The `seekVideoToFrame` function uses three `modalLooker` methods:

```js
function seekVideoToFrame(frameNumber, modalLooker, fps) {
    // 1. Seek the actual <video> element
    //    The video element is NOT in the regular DOM (canvas-based rendering).
    //    Only accessible via modalLooker.getVideo().
    var video = modalLooker.getVideo();
    video.currentTime = (frameNumber - 1) / fps;

    // 2. Sync the looker's internal state
    //    updater() pushes state changes into the looker's React state,
    //    which updates the frame counter overlay, detection labels, etc.
    modalLooker.updater({ frameNumber: frameNumber });

    // 3. Pause playback (stay on the seeked frame)
    modalLooker.pause();
}
```

#### Why other approaches don't work

| Approach | Why it fails |
|----------|-------------|
| `fopb.seekTo()` via `useTimelineVizUtils` | Writes to jotai atoms, but UMD plugins have a different jotai store context than the video player. Atom writes are invisible to the video player. |
| `fopb.dispatchTimelineSetFrameNumberEvent()` | Dispatches a CustomEvent on `window`, but the listener (`useCreateTimeline`) is not active in this FOE version. |
| `document.querySelector("video")` | Returns `null` — the `<video>` element is not in the regular DOM. FiftyOne renders video through a canvas-based Looker that manages the `<video>` element internally. |
| `modalLooker.updateOptions({frameNumber})` | Updates viewer options (zoom, pan, etc.), not playback state. |

#### Why `modalLooker` works

The `modalLooker` is the actual Looker instance, shared between the video player and plugin panels via a **Recoil atom** (`fos.modalLooker`). Recoil atoms are shared across the entire app, unlike jotai atoms which can be scoped to different Providers. This gives the plugin direct access to:

- `getVideo()` — the hidden `<video>` element
- `updater()` — the state synchronization function
- `pause()` / `play()` — playback control
- `subscribeToState()` — live state subscriptions

## Data Flow

1. **Panel opens** in modal → reads `fos.modalSampleId` from Recoil
2. **Calls Python operator** via `useOperatorExecutor("timeline-sync-test/get_detection_counts")`
3. **Python operator** queries the dataset, returns `{frames, counts, fps, total_frames}`
4. **SVG chart renders** with line + area fill + axis labels
5. **During playback**: `subscribeToState("frameNumber")` fires on each frame → red vertical line moves
6. **On chart click/drag**: `mouseDown` handler calculates frame number from mouse X → calls `seekVideoToFrame()` → video jumps to that frame

## SVG Chart Details

The chart is pure SVG (no charting library). Key elements:

- **Data line**: `<polyline>` connecting detection counts per frame
- **Area fill**: `<path>` with low-opacity fill under the line
- **Gridlines**: dashed horizontal lines with Y-axis labels
- **Frame indicator**: red vertical `<line>` + `<circle>` dot + count label
- **Click overlay**: transparent `<rect>` on top capturing `mouseDown`
- **Drag support**: `mouseDown` registers `mousemove`/`mouseup` on `document` for continuous seeking

## Deployment

```bash
# Zip the plugin
cd plugin && zip -r ../plugin.zip . && cd ..

# Upload plugin.zip via FiftyOne UI (Settings → Plugins)

# Restart plugins container
docker restart <deployment>-teams-plugins-1

# Hard refresh browser (Cmd+Shift+R)
```

## Version Requirements

- FiftyOne Enterprise >= v2.16.2 (OSS >= v1.13.2) for timeline sync
- PR [#7044](https://github.com/voxel51/fiftyone/pull/7044) fixed a jotai store mismatch that prevented timeline subscribers from receiving frame updates
