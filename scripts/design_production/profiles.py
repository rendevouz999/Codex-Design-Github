"""Capability records describe this plugin's callable adapters, not host app branding."""
PROFILES = {
    "presentation": {"status": "PARTIAL", "formats": ["pptx"], "adapter": "native_pptx", "unit_kinds": ["slide"], "scope": "Editable shapes/text from assigned source units; native PowerPoint preview. No arbitrary PPTX round-trip, Slide Master authoring, or Google Slides transport exposed to this worker yet."},
    "social_graphic": {"status": "SUPPORTED", "formats": ["svg"], "adapter": "editable_svg", "unit_kinds": ["artboard"], "scope": "Editable SVG posts/stories/carousels/ads with PNG previews; independent per-job sizes. Shapes, text, and text-clue placeholders."},
    "vector": {"status": "SUPPORTED", "formats": ["svg"], "adapter": "editable_svg", "unit_kinds": ["graphic", "artboard"], "scope": "Native editable SVG primitives and typography with PNG previews. Does not claim AI/EPS application equivalence."},
    "editorial_svg": {"status": "PARTIAL", "formats": ["svg"], "adapter": "editable_svg", "unit_kinds": ["page", "spread"], "scope": "Editable SVG pages/spreads; no InDesign text-flow or publication packaging."},
    "web_deck": {"status": "PARTIAL", "formats": [], "adapter": None, "unit_kinds": ["slide"], "scope": "Existing presentation web plan/audit/render remains available to Main; arbitrary HTML/JS is not exposed to the Specialist."},
    "google_slides": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["slide"], "scope": "No authenticated Google Slides adapter in this runtime."},
    "photoshop": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["artboard"], "scope": "No PSD/PSB or Smart Object application adapter."},
    "illustrator": {"status": "PARTIAL", "formats": [], "adapter": None, "unit_kinds": ["artboard"], "scope": "SVG is available through vector profile; native AI/EPS is not wired."},
    "after_effects": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["composition"], "scope": "No AEP/MOGRT/JSX application adapter."},
    "indesign": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["page", "spread"], "scope": "No INDD/IDML application adapter."},
    "figma": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["artboard"], "scope": "Host connector is not an authenticated callable adapter for this SDK runtime."},
    "canva": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["artboard"], "scope": "Host connector is not an authenticated callable adapter for this SDK runtime."},
    "typeface": {"status": "UNSUPPORTED", "formats": [], "adapter": None, "unit_kinds": ["glyph"], "scope": "Typography on supported artifacts is available; no OTF/TTF font authoring adapter."},
}


def select(task):
    profile = PROFILES.get(task.artifact_type)
    if not profile or not profile["adapter"] or task.output_format not in profile["formats"]:
        raise ValueError(f"UNSUPPORTED production format: {task.artifact_type}/{task.output_format}")
    if task.operation not in profile['operations']:
        raise ValueError('UNSUPPORTED operation for selected profile')
    enabled = set(profile.get('features', BASE_FEATURES))
    if set(task.required_features) - enabled:
        raise ValueError("UNSUPPORTED native feature: " + ", ".join(sorted(set(task.required_features) - enabled)))
    if task.presentation and task.artifact_type != 'presentation' or task.editorial and task.artifact_type != 'editorial_svg':
        raise ValueError('Medium contract does not match profile')
    if task.artifact_type == 'presentation':
        mode = task.presentation.structure if task.presentation else 'flat'
        if task.presentation and task.presentation.reusable_template and mode != 'structured':
            raise ValueError('Reusable template workflow requires structured mode')
        if 'reusable_template' in task.required_features and (not task.presentation or not task.presentation.reusable_template):
            raise ValueError('Reusable template feature requires its explicit contract')
        if set(task.required_features) & {'slide_masters', 'native_placeholders', 'theme'} and mode != 'structured':
            raise ValueError('Master/layout/placeholder/theme features require a structured presentation contract')
        if mode == 'structured' and any(not u.layout for u in task.units):
            raise ValueError('Structured slides require an explicit reusable layout ID')
        if mode == 'preserve' and (task.operation not in {'edit', 'refine', 'repair', 'render', 'qa'} or any(u.source_slide is None for u in task.units)):
            raise ValueError('Preserve mode requires existing-source operation and selected source slides')
        if 'existing_pptx_text_edit' in task.required_features and mode != 'preserve':
            raise ValueError('Existing PPTX text edit requires preserve mode')
    if task.artifact_type == 'web_deck' and any((u.width,u.height) != (1920,1080) for u in task.units):
        raise ValueError('Web deck requires the internal 1920x1080 stage contract')
    if set(task.required_features) & {'linked_text_flow', 'editorial_grid'} and not task.editorial:
        raise ValueError('Editorial flow/grid requires an editorial contract')
    if any(unit.kind not in profile["unit_kinds"] for unit in task.units):
        raise ValueError("Work unit kind does not match selected artifact profile")
    if task.output_format == "pptx" and len({(u.width, u.height) for u in task.units}) != 1:
        raise ValueError("A single PowerPoint file requires consistent slide dimensions")
    return profile


BASE_FEATURES = ['editable_text', 'editable_shapes', 'text_clue_placeholders']
PROFILES['presentation'].update(features=BASE_FEATURES + ['slide_masters', 'native_placeholders', 'theme', 'native_charts', 'native_tables', 'existing_pptx_text_edit', 'reusable_template'], scope='Native flat/structured PPTX, reusable master/layout and typed placeholders, theme, native chart/table; bounded slide-local text edits through the internal preserving importer/exporter. Verification is feature-specific.')
PROFILES['editorial_svg'].update(features=BASE_FEATURES + ['linked_text_flow', 'editorial_grid'], scope='Editable SVG pages/spreads plus JSON linked stories, typography and frame offsets; browser-measured reflow/overset QA. No INDD/IDML claim.')
PROFILES['web_deck'].update(formats=['html'], adapter='web_deck', features=BASE_FEATURES + ['navigation', 'reduced_motion', 'print'], scope='Typed source units compiled with internal stage/runtime, offline browser render and internal audits; arbitrary HTML/JS import is not enabled.')
PROFILES['illustrator'].update(status='UNSUPPORTED', scope='Native AI/EPS blocked: no locally registered Illustrator application or callable adapter found. SVG remains a separate vector capability.')
for record in PROFILES.values():
    record['operations']=['create','edit','refine','assets','render','qa','repair'] if record['adapter'] else []
PROFILES['editorial_svg']['status']='SUPPORTED'
PROFILES['web_deck']['status']='SUPPORTED'
PROFILES['presentation']['status']='SUPPORTED'
