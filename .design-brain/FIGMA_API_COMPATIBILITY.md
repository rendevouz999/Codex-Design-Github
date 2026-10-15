# Figma API Compatibility Guard

This is an active build-execution guard for every Figma/source-template task that uses the Figma Plugin API through `use_figma`.

## Auto-Layout Alignment Enums

Figma Plugin API auto-layout alignment values are not CSS/Flexbox words. Never use `START`, `END`, or `STRETCH` as values for `primaryAxisAlignItems` or `counterAxisAlignItems`.

Use the Figma API values directly:

| Intent | Figma API value |
| --- | --- |
| start | `MIN` |
| center | `CENTER` |
| end | `MAX` |
| distribute along primary axis | `SPACE_BETWEEN` |
| stretch/fill child | child sizing `FILL`, not alignment |

Allowed values:

- `primaryAxisAlignItems`: `MIN`, `CENTER`, `MAX`, `SPACE_BETWEEN`
- `counterAxisAlignItems`: `MIN`, `CENTER`, `MAX`, `BASELINE`

## Mandatory Normalization

Before calling `use_figma`, normalize any conceptual alignment term to the Figma API enum:

```js
const figmaPrimaryAlign = (value) => {
  const key = String(value || "MIN").toUpperCase();
  if (key === "START") return "MIN";
  if (key === "END") return "MAX";
  if (key === "BETWEEN") return "SPACE_BETWEEN";
  if (key === "SPACE-BETWEEN") return "SPACE_BETWEEN";
  if (key === "STRETCH") return "MIN";
  return ["MIN", "CENTER", "MAX", "SPACE_BETWEEN"].includes(key) ? key : "MIN";
};

const figmaCounterAlign = (value) => {
  const key = String(value || "MIN").toUpperCase();
  if (key === "START") return "MIN";
  if (key === "END") return "MAX";
  if (key === "STRETCH") return "MIN";
  return ["MIN", "CENTER", "MAX", "BASELINE"].includes(key) ? key : "MIN";
};
```

`STRETCH` must be expressed through child sizing, for example `child.layoutSizingHorizontal = "FILL"` or `child.layoutSizingVertical = "FILL"`, not through alignment.

## Failure Rule

If generated Figma code contains either of these patterns, stop before build and repair the source:

- `primaryAxisAlignItems = "END"`
- `counterAxisAlignItems = "END"`
- the same assignments using object syntax, for example `counterAxisAlignItems: "END"`

The repair is direct replacement with `MAX`, followed by rerunning the relevant lint, Figma build, and visual/source-hygiene check.

## Receipt Requirement

For Figma template builds, the auto-layout receipt must confirm that Figma API alignment values were normalized before execution. A receipt that only says "alignment set" is not enough when generated code used conceptual alignment terms.
