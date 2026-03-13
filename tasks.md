# Video Detection Chart Plugin — Tasks

**Status:** In progress — field selector and Python panel complete, dynamic group support next

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

## In Progress

### Dynamic Group Support

- [ ] Support dynamically grouped image datasets (e.g., NuScenes)
- [ ] Handle `ctx.view._is_dynamic_groups` branch for fetching frame data
- [ ] Use `get_dynamic_group(sample_id)` instead of `select()` for grouped views
- [ ] Branch field discovery: `get_field_schema()` for groups vs `get_frame_field_schema()` for video

## Backlog

- [ ] Send Python-only panel example to Porsche with interactivity trade-off explanation
- [ ] Support multiple plots (multiple fields visualized simultaneously)
- [ ] Migrate JS dropdown from native `<select>` to VOODO `Select` component (requires build step)
- [ ] Explore support for non-frame-level temporal data (higher-frequency sensor data — Eric's scope)

## Key Files

- `index.umd.js` — JS panel: SVG chart with bidirectional video sync and field selector
- `__init__.py` — Python operators (`GetTemporalFields`, `GetFrameValues`, `GetDetectionCounts`) + `FrameDataPlot` panel
- `fiftyone.yml` — Plugin manifest (2 panels, 3 operators)
- `proposal.md` — Architecture decisions and implementation notes
