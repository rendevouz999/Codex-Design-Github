# Canvas Format Specification

> See [`shared-standards-core.md`](shared-standards-core.md) §4.1 for the normative root `viewBox` grammar, compatibility spellings, and fail-closed validation rules.

## Format Quick Reference

| ID | Format | Size | viewBox | Ratio | Use Case |
|----|--------|------|---------|-------|----------|
| `ppt169onscreen` | PPT On-screen Show (16:9) | `960x540` | `0 0 960 540` | 16:9 | New native PPTX default: 10 × 5.625 inches landscape |
| `xiaohongshu` | Xiaohongshu (RED) | `1242x1660` | `0 0 1242 1660` | 3:4 | Image-text sharing, knowledge posts |
| `moments` | WeChat Moments / IG | `1080x1080` | `0 0 1080 1080` | 1:1 | Square posters, brand showcases |
| `story` | Story / TikTok | `1080x1920` | `0 0 1080 1920` | 9:16 | Vertical stories, short video covers |
| `wechat` | WeChat Article Header | `900x383` | `0 0 900 383` | 2.35:1 | WeChat article cover images |
| `banner` | Landscape Banner | `1920x1080` | `0 0 1920 1080` | 16:9 | Web banners, digital screens |
| `a4` | A4 Print | `1240x1754` | `0 0 1240 1754` | 1:sqrt(2) | Print posters, flyers |

Custom canvases likewise use `0 0 W H` with positive integer pixels; a fractional canvas is accepted only as compatible input for an imported custom PowerPoint slide size. All pages and internal Layout prototypes in one export share one numeric canvas within PowerPoint's slide range (914,400–51,206,400 EMU per side, about 96–5,376 SVG px). `ppt169onscreen` is exactly `960x540`; `banner` shares the ratio, not the coordinate system. Removed PPTX presets are not selectable.

```xml
<svg viewBox="0 0 960 540">    <!-- PPT On-screen Show (16:9) -->
<svg viewBox="0 0 1080 1920">  <!-- Story -->
```

## Platform Keep-clear

Canvas dimensions imply no title band, topology, or recurring chrome; reserve space only for a real output obstruction. For `story`, keep meaning-bearing text, identity, and calls to action within `y=120..1740` by default because mobile story controls occupy the top and bottom; images and texture may bleed. An exact platform overlay guide or installed template overrides this band. Story starting geometry: 80 px margins, 920 px measure, title band ≈ 90 px; regions stack, side by side only for near-square halves, and the band below 1740 carries bleed, texture, or a cropped element, not dead space.

## Typography Scale Start

For new native PPTX, the physical default is owned by `../../workflows/PPTX_SIZE_POLICY.md`. The former PPTX presets are removed from active selection. Recompute layout at 960 × 540 before authoring. Standalone non-PPTX products retain their own preset/size; do not impose this preference globally.

**Hard rule — normative owner**: this section owns the initial body-size anchor and sanity band for every registered or custom canvas. Strategist and Quick consume it directly; Confirm UI maintains an exact executable mirror and must not infer alternate canvas classes or values. Values are unitless SVG px.

| Canvas | Reading mode | Advisory body band | Initial body |
|---|---|---:|---:|
| `ppt169onscreen` | `text` | 18–21 | 20 |
| `ppt169onscreen` | `balanced` | 22–25 | 24 |
| `ppt169onscreen` | `presentation` | 28–32 | 32 |

Non-PPT registered and custom canvases derive one effective span from `W x H`:

```text
short = min(W, H); long = max(W, H); span = min(long, 3 * short)
low = round(span * 0.025); start = round(span * 0.029); high = round(span * 0.033)
```

| Canvas | Effective span | Advisory body band | Initial body |
|---|---:|---:|---:|
| `wechat` | 900 | 23–30 | 26 |
| `moments` | 1080 | 27–36 | 31 |
| `xiaohongshu` | 1660 | 42–55 | 48 |
| `banner` | 1920 | 48–63 | 56 |
| `story` | 1920 | 48–63 | 56 |
| `a4` | 1754 | 44–58 | 51 |

`story` and `banner` share one span but not one measure: the same body sits on a 1920 px line in `banner` and a 1080 px line in `story`, so portrait pages settle low. Executor's layout values and icon sizes are 1280-wide: scale by canvas width ÷ 1280, and stack regions instead of splitting once a column holds under about 30 body characters.

**Default — starting anchor, not a floor (confirmed identity, source fidelity, or viewing conditions may override)**: start from the table or formula, then resolve the role ramp and page density from content and delivery context; the band only flags unusual values and is not a validation gate. Apply the viewing-distance baseline in [`shared-standards-core.md`](shared-standards-core.md) instead of silently shrinking a recurring role to make content fit.
