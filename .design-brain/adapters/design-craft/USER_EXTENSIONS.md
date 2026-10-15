# User Extensions

Use local extensions when you want to add private product families, aliases, or structure patterns without changing the core Design Craft files.

1. Copy `data/user_extensions.example.json` to `data/user_extensions.local.json`.
2. Add aliases under `custom_aliases`.
3. Add product families under `custom_product_families`.
4. Add structure patterns under `custom_structure_patterns`.

Example product family:

```json
{
  "id": "custom_local_service",
  "keywords": ["custom service", "local booking"],
  "depth_rule": {
    "min_sections": 8,
    "recommended_sections": "8-12"
  },
  "structure_pattern": {
    "name": "Custom Local Service Website System",
    "unit_label": "sections",
    "sections": [
      "Service hero",
      "Service categories",
      "How booking works",
      "Featured services",
      "Trust proof",
      "Pricing",
      "FAQ",
      "CTA booking",
      "Footer"
    ]
  }
}
```

Safety overrides are disabled by default. Keep `allow_override_safety` false unless you are testing privately and understand the risk. Public exports exclude `data/user_extensions.local.json`.
