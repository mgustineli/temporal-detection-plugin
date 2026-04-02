# Temporal Detection Plugin — Tasks

**Status:** Active — multi-chart panel with label timeline heatmap, instance track chart, label filtering, timestamp display, bidirectional sync across all modes

## Completed

### Design

- [x] Refactor plugin colors and typography to use VOODO design system
- [x] Update demo GIF and README to reflect new design
- [x] Send plugin repo and video recording to Porsche (Matthias)

### Field Selector

- [x] Add `GetTemporalFields` operator — discovers plottable frame-level fields (`FloatField`, `IntField`, `ListField`)
- [x] Add `GetFrameValues` operator — fetches per-frame values for any field, defaults to `detections.detections`
- [x] Keep `GetDetectionCounts` as legacy wrapper for backward compatibility
- [x] Add dropdown/selector UI (native `<select>` styled to VOODO) in JS panel toolbar
- [x] Dynamic Y-axis title and value label based on selected field

### Python-Only Panel (Frame Data Plot)

- [x] Implement `FrameDataPlot` panel using `FrameLoaderView` + `panel.plot()` (Plotly)
- [x] Plotly line chart with area fill and moving dot via `selectedpoints`
- [x] Field selector via `AutocompleteView` dropdown
- [x] VOODO dark theme matching the JS panel
- [x] Timeline sync (video → chart) via `FrameLoaderView` without `timeline_name`

### Reference Review

- [x] Study `FrameLoaderView` timeline sync pattern — used for Python panel
- [x] Research `@voxel51/label_count` plugin source (GitHub: `voxel51/fiftyone-plugins`)
- [x] Confirmed `@voxel51/frame_label_plots` only available on demo deployment

### Dynamic Group Support — Python Operators

- [x] Detect dynamic groups via `ctx.view._is_dynamic_groups` in `_get_fields` and `_get_frame_values`
- [x] Field discovery: `get_field_schema()` for groups vs `get_frame_field_schema()` for video
- [x] Data fetch: `get_dynamic_group(group_key)` via `_get_dynamic_group_key()` — resolves `GroupBy` stage field
- [x] Sequential frame numbers: `list(range(1, len(values) + 1))` for dynamic groups (no `frame_number` field)
- [x] Test with NuScenes `cam_front_video` view on Murilo deployment

### Dynamic Group Support — JS Panel (Pagination mode)

- [x] Read `fos.isDynamicGroup` and `fos.dynamicGroupCurrentElementIndex` for image→chart sync
- [x] Set `dynamicGroupCurrentElementIndex` via `useSetRecoilState` for chart→image seek
- [x] Skip redundant data reloads during intra-group navigation (`groupDataLoadedRef`)

### Bidirectional Sync for All Dynamic Group View Modes

- [x] Fix chart→video seek in "video" mode (ImaVid) — uses timeline `CustomEvent` (`set-frame-number-timeline-{id}`), same mechanism as FiftyOne's built-in seek bar and `set_frame_number` operator
- [x] Fix chart→image seek in "pagination" mode — uses `setDynamicGroupIndex` via `fos.dynamicGroupCurrentElementIndex`
- [x] Fix chart→image seek in "carousel" mode — maps frame→sampleId, navigates via `fos.modalSelector`
- [x] Fix carousel→chart sync — watches `modalSampleId` changes, resolves to frame via `sampleIdToFrame` mapping
- [x] Add `sample_ids` to Python operator response for dynamic groups — enables carousel mode bidirectional sync
- [x] Add `dynamicGroupsViewMode` detection to distinguish carousel from pagination in JS
- [x] Ensure video→chart sync works in all modes
- [x] Clean up debug logging

### Multi-Chart Panel Support

- [x] Add `dataset_name` to `GetTemporalFields` operator response for localStorage key
- [x] Replace single-chart state model with `charts[]` array, `chartStatus{}` object, and `dataStoreRef` cache
- [x] Implement sequential load queue (`loadQueueRef`, `loadingFieldRef`, `processQueue()`) for single `dataExecutor`
- [x] Create `ChartCard` component with header (field label + move up/down/remove buttons) and loading/error/data states
- [x] Add "Add chart" toolbar dropdown showing fields not yet added
- [x] Wire up remove (filter from `charts`), move up/down (swap adjacent in `charts`)
- [x] Implement localStorage persistence per dataset — save on chart change, restore on field discovery
- [x] Handle sample change: clear data cache, preserve chart selections, re-queue all fields
- [x] Shared frame indicator and seek across all charts via `effectiveFrame` and `handleFrameSeek`
- [x] Scrollable container with `maxHeight` for 3+ charts
- [x] Status bar shows chart count instead of "frames with data"

### Label Timeline Chart (Swim Lane Heatmap)

- [x] Add `has_labels` flag to field discovery — query full schema, check for `.label` sub-field
- [x] Implement `_get_label_timeline()` helper — aggregates per-label counts server-side for both native video and dynamic groups
- [x] Add `mode` param to `GetFrameValues` operator — `count` (default) or `labels`
- [x] State model refactored to composite keys (`field:type`) for `dataStoreRef`, `chartStatus`, and load queue
- [x] localStorage format updated to `[{field, type}]` with migration from old string-array format
- [x] `LabelTimelineChart` component — SVG heatmap with color-coded rows per label, opacity-scaled cells
- [x] Frame binning when `plotWidth / totalFrames < 2px` — max count per bin
- [x] Click/drag seeking adapted from SVGChart pattern
- [x] Hover tooltip with portal rendering (`ReactDOM.createPortal`) — overlays other charts
- [x] Top-N filtering (15 labels) with "Show N more…" expander and "Show less ▲" collapser
- [x] `ChartCard` dispatches between `LabelTimelineChart` and `SVGChart` based on `chartType` prop
- [x] Add chart dropdown shows dual entries (labels/count) for label-capable fields
- [x] Default chart prefers `type: "labels"` for first label-capable field
- [x] Panel uses flex layout to fill available space

### Rename

- [x] Repo renamed from `video-detection-chart-plugin` to `temporal-detection-plugin`
- [x] Plugin name: `video-detection-chart` → `temporal-detection`
- [x] Panel name: `Detection Count Plot (Interactive)` → `Temporal Data Explorer`
- [x] Updated operator paths, localStorage prefix, log prefixes, README, and gif

### Label Filtering in Heatmap

- [x] Checkbox dropdown with "Filter labels" button — portal-rendered to overlay other charts
- [x] Each label has checkbox + color swatch + full name
- [x] "Select all" / "Clear all" quick actions at top of dropdown
- [x] "Show all" button appears when filtering is active
- [x] Button highlights blue with count when filter is active (e.g., "Filter labels (3/10)")
- [x] Filtered state is component-local (not persisted)

### Timestamp Display (Frame Number vs Time)

- [x] Read FiftyOne's "Use frame number" setting via `fos.appConfigOption({modal: true, key: "useFrameNumber"})`
- [x] `formatTimestamp()` and `formatTimestampTick()` helpers — `M:SS.s` / `H:MM:SS.s`
- [x] X-axis ticks, frame indicator, tooltip, and status bar all respect the setting
- [x] Both `SVGChart` and `LabelTimelineChart` updated

### Instance Track Chart (Per-Object Binary Timeline)

- [x] Python: `has_tracks` flag in field discovery — checks schema for `.index` and verifies non-None values in first sample
- [x] Python: `_get_instance_tracks()` helper — builds per-instance binary presence arrays keyed by `"label #index"`, sorted by label then index
- [x] Python: `mode="tracks"` dispatch in `GetFrameValues.execute()`
- [x] JS: `colorKeyMap` prop on `LabelTimelineChart` — maps instance names to class names for consistent colors
- [x] JS: data result handler detects `payload.tracks` for instance track data
- [x] JS: dropdown shows `"field (tracks)"` for fields with `has_tracks: true`
- [x] JS: `ChartCard` dispatches tracks data to `LabelTimelineChart` with `colorKeyMap`
- [x] Works for quickstart-video (`index` populated, 10 tracked objects)
- [x] Gracefully unavailable for NuScenes (`index` is None — no tracking attribute)

### ImaVid Seek Fix

- [x] Discovered ImaVid two-layer architecture: legacy canvas layer + React/Jotai timeline layer
- [x] `drawFrameNoAnimation` only updates canvas, not timeline atoms (playback resume point)
- [x] Fixed: now dispatches `CustomEvent("set-frame-number-timeline-{id}")` — same mechanism as FiftyOne's seek bar
- [x] Properly updates canvas, Jotai frame number atom, status indicator ("30/38"), and resume point

## In Progress

(nothing currently)

## Backlog

### Instance Tracking — Extended Attribute Support

- [ ] Support `instance_token` as alternative tracking attribute (NuScenes uses this in the original dataset but it wasn't imported into this FiftyOne dataset)
- [ ] Auto-detect tracking attributes: check `index`, `instance_id`, `track_id`, `instance_token` in schema
- [ ] Allow user to specify custom tracking attribute via dropdown
- [ ] Re-import NuScenes with `instance_token` mapped to test

### Housekeeping

- [ ] Rename local folder from `video-detection-chart-plugin` to `temporal-detection-plugin` (run `mv ~/github/video-detection-chart-plugin ~/github/temporal-detection-plugin`)
- [ ] Send Python-only panel example to Porsche with interactivity trade-off explanation
- [ ] Split Python panel into its own repo — it's a reference example, not part of the production JS plugin

### Future Enhancements

- [ ] Migrate JS dropdown from native `<select>` to VOODO `Select` component (requires build step)
- [ ] Explore support for non-frame-level temporal data (higher-frequency sensor data — Eric's scope)
- [ ] Investigate image loading latency for dynamic group frame navigation (GCS fetch per frame)
- [ ] Server-side frame binning for very long videos (10k+ frames) to reduce payload size
- [ ] Canvas rendering instead of SVG for heatmap charts with many elements (performance)

## Key Files

- `index.umd.js` — JS panel: multi-chart SVG system with label timeline heatmap, instance tracks, line charts, label filtering, timestamp display, bidirectional video sync, localStorage persistence
- `__init__.py` — Python operators: field discovery (`has_labels`, `has_tracks`), count/label timeline/instance track data, both native video and dynamic groups
- `fiftyone.yml` — Plugin manifest (1 panel, 3 operators)

## Architecture Notes

- This plugin targets **native video datasets** AND **dynamically grouped image datasets**
- Dynamic groups have three navigation modes: pagination (images), carousel (filmstrip), video (ImaVid playback)
- ImaVid seek uses timeline `CustomEvent` dispatch (same as FiftyOne's built-in `set_frame_number` operator)
- The Python panel (`FrameDataPlot`) is a reference example — should be split into a separate repo
- The JS panel is the production version with full bidirectional sync
- Key Recoil atoms for dynamic groups: `isDynamicGroup`, `dynamicGroupCurrentElementIndex`, `dynamicGroupsViewMode`, `shouldRenderImaVidLooker`, `imaVidLookerState`
- Key app config: `fos.appConfigOption({modal: true, key: "useFrameNumber"})` for timestamp display
- Instance tracks require a persistent cross-frame identifier (`index` for video datasets, `instance_token` for NuScenes)
- Reference: [FiftyOne dynamic grouping docs](https://docs.voxel51.com/user_guide/app.html#grouping-samples)
