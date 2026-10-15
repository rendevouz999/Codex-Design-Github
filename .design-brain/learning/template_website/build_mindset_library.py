#!/usr/bin/env python
"""Build an evidence-led website template designer mindset library.

This script is intentionally scoped to the learning folder. It writes proposed
learning artifacts only; it does not modify stable Brain Design rules.
"""

from __future__ import annotations

import json
import math
import re
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from PIL import Image, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "Template Website"
OUT_DIR = ROOT / ".design-brain" / "learning" / "template_website"

Image.MAX_IMAGE_PIXELS = None
warnings.filterwarnings("ignore", category=DeprecationWarning, module="PIL")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="Palette images with Transparency.*")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

PRODUCT_TYPES = [
    "SaaS",
    "agency/studio",
    "corporate/business",
    "portfolio",
    "ecommerce",
    "dashboard/admin",
    "editorial/blog",
    "app landing",
    "finance/consulting",
    "real estate",
    "restaurant/food",
    "education/course",
    "medical/healthcare",
    "event/conference",
    "personal brand",
    "creative showcase",
    "service business",
    "full website kit",
    "one-page landing page",
    "unknown/needs review",
]

KEYWORDS: dict[str, list[str]] = {
    "SaaS": [
        "saas",
        "software",
        "ai saas",
        "ai platform",
        "platform website",
        "cyber security",
        "cybersecurity",
        "machine learning",
        "automation",
        "technology website",
        "artificial intelligance",
        "artificial intelligence",
        "analytics",
        "system website",
    ],
    "agency/studio": [
        "agency",
        "studio",
        "creative agency",
        "digital marketing",
        "marketing website",
        "branding",
        "design agency",
        "web agency",
        "creative studio",
    ],
    "corporate/business": [
        "corporate",
        "business",
        "company",
        "enterprise",
        "business information",
        "business analysis",
        "advisor",
    ],
    "portfolio": ["portfolio", "portofolio", "designer website", "works", "case study"],
    "ecommerce": [
        "ecommerce",
        "e-commerce",
        "store",
        "shop",
        "product page",
        "product website",
        "sneakers",
        "eyewear",
        "glasses",
        "outfit",
        "home decor",
        "cart",
        "checkout",
    ],
    "dashboard/admin": ["dashboard", "admin", "ui kit", "crm", "analytics dashboard", "management"],
    "editorial/blog": [
        "blog",
        "post",
        "news",
        "magazine",
        "article",
        "category",
        "newsletter",
        "video post",
        "audio post",
        "quote post",
        "gallery post",
    ],
    "app landing": ["app", "mobile app", "ios", "android", "download app", "smart app"],
    "finance/consulting": [
        "financial",
        "finance",
        "fintech",
        "consulting",
        "consultant",
        "advisor",
        "investment",
        "bank",
        "insurance",
    ],
    "real estate": ["real estate", "property", "realtor", "apartment", "housing", "rental"],
    "restaurant/food": [
        "restaurant",
        "food",
        "pizza",
        "pizzeria",
        "cafe",
        "caffe",
        "coffee",
        "drink",
        "gourment",
        "gourmet",
        "burger",
    ],
    "education/course": ["education", "course", "academy", "school", "learning", "lms", "university"],
    "medical/healthcare": [
        "health",
        "healthcare",
        "medical",
        "clinic",
        "doctor",
        "dental",
        "dentist",
        "wellness",
        "smart healthcare",
    ],
    "event/conference": [
        "event",
        "conference",
        "webinar",
        "festival",
        "wedding",
        "summit",
        "ticket",
    ],
    "personal brand": [
        "personal",
        "personal brand",
        "coach",
        "speaker",
        "influencer",
        "resume",
        "cv",
        "freelancer",
    ],
    "creative showcase": [
        "showcase",
        "metaverse",
        "architecture",
        "interior",
        "supercar",
        "car community",
        "fashion",
        "art",
        "music",
        "photography",
        "robotics",
    ],
    "service business": [
        "service",
        "travel",
        "hotel",
        "hospitality",
        "job career",
        "career",
        "legal",
        "law",
        "repair",
        "cleaning",
        "community",
        "architecture",
        "interior",
    ],
    "full website kit": [
        "home_",
        "home ",
        "about us",
        "contact",
        "menu sidebar",
        "demo",
        "category_",
        "features",
        "01_home",
        "02_home",
    ],
    "one-page landing page": [
        "landing page",
        "lead-generation",
        "lead generation",
        "squeeze",
        "waitlist",
        "campaign",
    ],
}

ASSET_HINTS = [
    "captcha",
    "card-",
    "cat -",
    "categories -",
    "carousels -",
    "contact - icon",
    "icon -",
    "img_",
    "businessman_",
    "shape",
    "element",
]


@dataclass
class ImageMetrics:
    width: int = 0
    height: int = 0
    aspect_ratio: float = 0.0
    orientation: str = "unknown"
    luminance_mean: float = 0.0
    luminance_std: float = 0.0
    dark_ratio: float = 0.0
    light_ratio: float = 0.0
    saturation_mean: float = 0.0
    colorfulness: float = 0.0
    edge_density: float = 0.0
    tone: str = "unknown"
    contrast: str = "unknown"
    color_mood: str = "unknown"
    density: str = "unknown"
    error: str | None = None


def now_stamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")


def normalize(text: str) -> str:
    value = text.lower().replace("_", " ").replace("-", " ")
    value = re.sub(r"\b20\d{2}\b|\butc\b|\b[a-f0-9]{8,}\b", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def files() -> list[Path]:
    if not SOURCE_DIR.exists():
        return []
    return sorted(
        [path for path in SOURCE_DIR.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS],
        key=lambda path: rel(path).lower(),
    )


def is_asset_like(path: Path) -> bool:
    text = normalize(path.stem)
    if any(hint in text for hint in ASSET_HINTS):
        return True
    return bool(re.fullmatch(r"\d+|\d+\(\d+\)", text))


def is_generic_page_preview(path: Path) -> bool:
    text = normalize(path.stem)
    generic_page_words = {
        "home",
        "about",
        "about us",
        "contact",
        "features",
        "category",
        "gallery",
        "quote post",
        "audio post",
        "video post",
        "link post",
        "full width post",
    }
    if any(word in text for word in generic_page_words):
        product_hits = 0
        for product_type, keywords in KEYWORDS.items():
            if product_type == "full website kit":
                continue
            if any(normalize(keyword) in text for keyword in keywords):
                product_hits += 1
        return product_hits == 0
    return False


def image_metrics(path: Path) -> ImageMetrics:
    metrics = ImageMetrics()
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            metrics.width, metrics.height = image.size
            metrics.aspect_ratio = round(metrics.height / metrics.width, 3) if metrics.width else 0.0
            if metrics.aspect_ratio >= 2.4:
                metrics.orientation = "tall full-page preview"
            elif metrics.aspect_ratio >= 1.35:
                metrics.orientation = "portrait/webpage preview"
            elif metrics.aspect_ratio <= 0.75:
                metrics.orientation = "wide screen preview"
            else:
                metrics.orientation = "square or cropped preview"

            sample = image.copy()
            sample.thumbnail((220, 220))
            gray = sample.convert("L")
            gray_stat = ImageStat.Stat(gray)
            metrics.luminance_mean = round(gray_stat.mean[0], 2)
            metrics.luminance_std = round(gray_stat.stddev[0], 2)

            pixels = list(gray.getdata())
            total = max(1, len(pixels))
            metrics.dark_ratio = round(sum(1 for px in pixels if px < 70) / total, 4)
            metrics.light_ratio = round(sum(1 for px in pixels if px > 210) / total, 4)

            hsv = sample.convert("HSV")
            sat = list(hsv.getchannel("S").getdata())
            metrics.saturation_mean = round(mean(sat), 2) if sat else 0.0

            rgb_stat = ImageStat.Stat(sample)
            rg = rgb_stat.stddev[0] - rgb_stat.stddev[1]
            yb = 0.5 * (rgb_stat.stddev[0] + rgb_stat.stddev[1]) - rgb_stat.stddev[2]
            metrics.colorfulness = round(math.sqrt(rg * rg + yb * yb), 2)

            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_values = list(edges.getdata())
            metrics.edge_density = round(sum(1 for px in edge_values if px > 34) / max(1, len(edge_values)), 4)

            if metrics.dark_ratio > 0.48:
                metrics.tone = "dark-dominant"
            elif metrics.light_ratio > 0.46 or metrics.luminance_mean > 185:
                metrics.tone = "light-dominant"
            else:
                metrics.tone = "mixed-tone"

            if metrics.luminance_std >= 72:
                metrics.contrast = "high"
            elif metrics.luminance_std >= 45:
                metrics.contrast = "medium"
            else:
                metrics.contrast = "low"

            if metrics.saturation_mean >= 86 or metrics.colorfulness >= 28:
                metrics.color_mood = "vivid"
            elif metrics.saturation_mean >= 45 or metrics.colorfulness >= 15:
                metrics.color_mood = "moderate"
            else:
                metrics.color_mood = "muted"

            if metrics.edge_density >= 0.22:
                metrics.density = "dense"
            elif metrics.edge_density >= 0.11:
                metrics.density = "balanced"
            else:
                metrics.density = "spacious"
    except Exception as exc:  # noqa: BLE001 - keep ledger complete.
        metrics.error = str(exc)
    return metrics


def product_scores(path: Path) -> dict[str, int]:
    text = normalize(path.stem + " " + path.parent.name)
    scores: dict[str, int] = {}
    for product_type, keywords in KEYWORDS.items():
        score = 0
        for keyword in keywords:
            phrase = normalize(keyword)
            if phrase and phrase in text:
                score += 12 + min(len(phrase.split()), 4)
        if score:
            scores[product_type] = score

    if is_asset_like(path):
        return {"unknown/needs review": 1}

    if not scores:
        return {"unknown/needs review": 1}

    return scores


def classify(path: Path) -> tuple[str, list[str], list[str], str]:
    scores = product_scores(path)
    ranked = sorted(scores.items(), key=lambda item: (-item[1], PRODUCT_TYPES.index(item[0])))
    primary = ranked[0][0]
    secondary = [name for name, _ in ranked[1:4]]
    text = normalize(path.stem)
    notes: list[str] = []
    if is_asset_like(path):
        notes.append("asset-like or partial component; use cautiously for product-level pattern learning")
    if "landing page" in text or "lead generation" in text:
        notes.append("landing-page cue present; check whether this is a one-page conversion asset or product-specific site")
    if primary == "unknown/needs review":
        notes.append("classification is weak; manual visual review recommended")
    if path.name.lower().startswith(("01_", "02_", "03_", "04_", "05_", "06_", "07_", "08_")):
        notes.append("numbered page preview; may belong to a multi-page kit")
    if is_generic_page_preview(path):
        notes.append("generic page preview; product niche is not clear from file evidence")
    category_hint = path.parent.relative_to(SOURCE_DIR).as_posix() if path.parent != SOURCE_DIR else "root"
    return primary, secondary, notes, category_hint


PRODUCT_LOGIC: dict[str, dict[str, str]] = {
    "SaaS": {
        "belief": "the product is real, useful, low-risk, and worth trying",
        "prove": "clear product promise, visible interface or workflow proof, feature depth, pricing/demo path, trust or security cues",
        "opening": "promise plus product proof, usually before dense feature explanation",
        "trust": "logos, interface screenshots, security/reliability signals, testimonial/case cues",
        "density": "calm opener, denser product and workflow middle, simplified action close",
        "components": "hero, product preview, feature groups, workflow, integrations, proof, pricing/demo, FAQ",
        "failure": "generic hero/card/CTA pages that never prove the product exists",
    },
    "agency/studio": {
        "belief": "the team has taste, strategic judgment, and credible output",
        "prove": "work samples, service clarity, process, client proof, strong art direction",
        "opening": "identity-forward or portfolio-forward confidence",
        "trust": "case work, client logos, process clarity, testimonials",
        "density": "bold opening, curated proof density, quieter contact close",
        "components": "hero, services, portfolio/cases, process, clients, testimonial, contact",
        "failure": "pretty abstract visuals without proof of capability",
    },
    "corporate/business": {
        "belief": "the organization is stable, professional, and safe to contact",
        "prove": "service scope, values, metrics, team or authority, contact path",
        "opening": "clear category and value statement before detail",
        "trust": "metrics, team, process, recognizable service structure",
        "density": "calm trust-building surface, detail where service confidence matters",
        "components": "hero, service overview, metrics, about, process, testimonial, contact",
        "failure": "stock corporate sameness with no specific buyer confidence",
    },
    "portfolio": {
        "belief": "the creator has a distinct point of view and proven work",
        "prove": "selected projects, role/context, case outcomes, personal identity",
        "opening": "name or discipline plus visual proof",
        "trust": "project depth, recognitions, client context, case studies",
        "density": "expressive opener, gallery/work density, compact contact close",
        "components": "intro, selected work, case cards, about, awards, contact",
        "failure": "a gallery with no role, story, or credibility",
    },
    "ecommerce": {
        "belief": "the products are desirable, easy to browse, and safe to buy",
        "prove": "product imagery, categories, price/benefit cues, reviews, cart/checkout logic",
        "opening": "product desire or collection promise, then browse path",
        "trust": "reviews, product detail, shipping/support cues, secure checkout assumptions",
        "density": "visual product density balanced with simple purchase decisions",
        "components": "hero, categories, product grid, featured product, review, offer, cart/checkout pages",
        "failure": "decorative product shots without commerce states",
    },
    "dashboard/admin": {
        "belief": "the system makes complex work readable and controllable",
        "prove": "data hierarchy, filters, tables/charts, states, navigation logic",
        "opening": "operational overview before granular data",
        "trust": "clear hierarchy, predictable controls, error/empty/loading states",
        "density": "high density with strict grouping and calm chrome",
        "components": "sidebar/topbar, KPI cards, charts, tables, filters, state views",
        "failure": "decorative dashboards with fake hierarchy and unusable density",
    },
    "editorial/blog": {
        "belief": "the publication has content depth and readable rhythm",
        "prove": "featured stories, categories, post variants, author/date logic, newsletter path",
        "opening": "featured story or editorial identity before browsing",
        "trust": "consistent content taxonomy, author/date/category systems",
        "density": "headline emphasis, scan-friendly grids, quiet reading surfaces",
        "components": "featured post, category rail, post grid, article variants, newsletter, archive",
        "failure": "blog cards without editorial hierarchy or article system",
    },
    "app landing": {
        "belief": "the app solves one focused problem and is easy to adopt",
        "prove": "device/UI proof, benefits, steps, ratings, download CTA",
        "opening": "use-case promise plus app/device proof",
        "trust": "ratings, screenshots, feature walkthrough, platform badges",
        "density": "simple opener, explanatory steps, concise action close",
        "components": "hero, app preview, benefits, steps, testimonials, download CTA",
        "failure": "feature claims without interface or adoption proof",
    },
    "finance/consulting": {
        "belief": "the advisor is credible, careful, and outcome-oriented",
        "prove": "expertise, process, metrics, testimonials, compliance-like restraint",
        "opening": "calm authority and outcome promise",
        "trust": "credentials, statistics, client outcomes, process clarity",
        "density": "low visual noise, denser proof/process after confidence is established",
        "components": "hero, services, metrics, process, cases/testimonials, consultation CTA",
        "failure": "flashy finance visuals that reduce perceived trust",
    },
    "real estate": {
        "belief": "the property offer is tangible, searchable, and trustworthy",
        "prove": "property visuals, listing filters, location, agent/team, enquiry path",
        "opening": "aspirational property or location promise with search path",
        "trust": "listing data, agent credibility, location proof, testimonials",
        "density": "large visual proof, dense listing/search modules, simple enquiry close",
        "components": "hero/search, listings, property detail, neighborhood, agent, contact",
        "failure": "pretty property page with no search/listing logic",
    },
    "restaurant/food": {
        "belief": "the food looks desirable and ordering/reservation is easy",
        "prove": "food imagery, menu, location, reviews, booking/order CTA",
        "opening": "sensory product desire or venue identity",
        "trust": "reviews, menu clarity, hours/location, reservation path",
        "density": "image-rich opening, menu density, quiet practical info",
        "components": "hero, menu, specials, gallery, reviews, reservation/order, location",
        "failure": "food visuals without menu or conversion utility",
    },
    "education/course": {
        "belief": "the course improves a skill and is credible to join",
        "prove": "curriculum, instructor authority, outcomes, pricing/enrollment, testimonials",
        "opening": "learning outcome before curriculum depth",
        "trust": "instructor proof, lesson structure, student outcomes",
        "density": "simple promise, detailed curriculum, reassurance before enroll CTA",
        "components": "hero, curriculum, instructor, outcomes, pricing, testimonial, FAQ",
        "failure": "course page without curriculum or outcome proof",
    },
    "medical/healthcare": {
        "belief": "the care provider is safe, competent, and easy to reach",
        "prove": "services, providers, credentials, patient proof, appointment path",
        "opening": "calm reassurance plus care category",
        "trust": "doctor/team, certifications, patient testimonials, location/contact",
        "density": "soft calm surface, service detail only where reassurance matters",
        "components": "hero, services, provider cards, process, testimonials, appointment CTA",
        "failure": "medical page that feels decorative instead of reassuring",
    },
    "event/conference": {
        "belief": "the event is worth attending and logistically clear",
        "prove": "date/location, speakers, agenda, tickets, sponsor/social proof",
        "opening": "event identity plus date/action urgency",
        "trust": "speaker lineup, agenda, past/sponsor proof, venue clarity",
        "density": "bold opener, schedule/speaker density, direct ticket close",
        "components": "hero, speakers, agenda, venue, pricing/tickets, sponsors, FAQ",
        "failure": "event page with mood but no date, agenda, or ticket logic",
    },
    "personal brand": {
        "belief": "the person is credible, memorable, and worth following or hiring",
        "prove": "personal story, authority, content/work proof, social proof, contact/follow path",
        "opening": "name/personality plus authority cue",
        "trust": "bio, achievements, content, testimonials, social proof",
        "density": "personality in opener, proof clusters, simple relationship CTA",
        "components": "hero, about, proof/work/content, testimonials, offer/contact",
        "failure": "personal page with personality but no authority evidence",
    },
    "creative showcase": {
        "belief": "the visual concept is distinctive and worth exploring",
        "prove": "immersive imagery, expressive typography, curated details, project/product proof",
        "opening": "visual atmosphere or object-first impact",
        "trust": "craft consistency, detailed showcase, story/context",
        "density": "high contrast between cinematic moments and quiet detail sections",
        "components": "hero, gallery/showcase, story, specs/details, proof, action",
        "failure": "spectacle without usable structure or buyer adaptation logic",
    },
    "service business": {
        "belief": "the provider understands the need and is easy to contact",
        "prove": "service list, process, location/availability, reviews, booking/contact",
        "opening": "clear service promise plus local/category relevance",
        "trust": "reviews, process, before/after or portfolio, contact clarity",
        "density": "practical clarity first, supporting details in scannable clusters",
        "components": "hero, services, process, gallery/cases, testimonial, booking/contact",
        "failure": "service page that hides what is offered or how to act",
    },
    "full website kit": {
        "belief": "the buyer receives enough pages and states to adapt confidently",
        "prove": "multiple page previews, repeated navigation/system, content variants",
        "opening": "product completeness or page-system preview",
        "trust": "page depth, consistent components, reusable layouts",
        "density": "varies by page role; completeness matters more than one perfect homepage",
        "components": "home variants, about, contact, category, post/detail, utility states",
        "failure": "calling a single homepage a kit without page coverage",
    },
    "one-page landing page": {
        "belief": "the single offer is clear and worth acting on now",
        "prove": "focused promise, benefits, proof, objection handling, CTA repetition",
        "opening": "conversion promise with immediate action path",
        "trust": "social proof, offer detail, FAQs, risk reversal",
        "density": "tight conversion rhythm; no unnecessary page-system sprawl",
        "components": "hero, benefits, proof, offer/pricing, FAQ, CTA",
        "failure": "one-page template that feels like a trimmed full website without conversion logic",
    },
    "unknown/needs review": {
        "belief": "not enough reliable evidence",
        "prove": "manual review needed",
        "opening": "unknown",
        "trust": "unknown",
        "density": "unknown",
        "components": "unknown",
        "failure": "promoting weak evidence into rules",
    },
}


def metric_dict(metrics: ImageMetrics) -> dict[str, Any]:
    return {
        "width": metrics.width,
        "height": metrics.height,
        "aspectRatioHeightOverWidth": metrics.aspect_ratio,
        "orientation": metrics.orientation,
        "luminanceMean": metrics.luminance_mean,
        "luminanceStd": metrics.luminance_std,
        "darkRatio": metrics.dark_ratio,
        "lightRatio": metrics.light_ratio,
        "saturationMean": metrics.saturation_mean,
        "colorfulness": metrics.colorfulness,
        "edgeDensity": metrics.edge_density,
        "tone": metrics.tone,
        "contrast": metrics.contrast,
        "colorMood": metrics.color_mood,
        "density": metrics.density,
        "error": metrics.error,
    }


def observed_evidence(path: Path, product_type: str, secondary: list[str], metrics: ImageMetrics, notes: list[str]) -> list[str]:
    evidence = [
        f"file name contains category/product cues: {path.stem}",
        f"image metrics: {metrics.width}x{metrics.height}, {metrics.orientation}, {metrics.tone}, {metrics.contrast} contrast, {metrics.color_mood} color, {metrics.density} visual detail",
    ]
    if secondary:
        evidence.append("secondary classification cues: " + ", ".join(secondary))
    if notes:
        evidence.append("caution notes: " + "; ".join(notes))
    if metrics.error:
        evidence.append(f"image read error: {metrics.error}")
    if product_type == "unknown/needs review":
        evidence.append("no strong product-type cue detected")
    return evidence


def confidence(product_type: str, notes: list[str], metrics: ImageMetrics, scores: dict[str, int]) -> str:
    if metrics.error or product_type == "unknown/needs review":
        return "low"
    if any("asset-like" in note for note in notes):
        return "low"
    if any("generic page preview" in note for note in notes):
        return "medium"
    top_score = max(scores.values()) if scores else 0
    if top_score >= 24 and metrics.width and metrics.height:
        return "high"
    return "medium"


def evidence_entry(path: Path, inventory: dict[str, Any], metrics: ImageMetrics) -> dict[str, Any]:
    product_type = inventory["possibleProductType"]
    logic = PRODUCT_LOGIC[product_type]
    scores = product_scores(path)
    conf = confidence(product_type, inventory["notes"], metrics, scores)
    return {
        "sourcePath": inventory["filePath"],
        "fileName": inventory["fileName"],
        "productType": product_type,
        "observedEvidence": observed_evidence(path, product_type, inventory["secondaryProductTypes"], metrics, inventory["notes"]),
        "imageMetrics": metric_dict(metrics),
        "inferredDesignerReason": logic["opening"],
        "userBuyerEffect": f"Helps the buyer believe {logic['belief']}.",
        "commercialFunction": f"Supports marketplace usefulness by proving: {logic['prove']}.",
        "reusableThinkingLogic": logic["trust"],
        "originalityTransformation": "Reuse the decision logic, then change composition, pacing, motif, component grouping, image placement, and CTA staging.",
        "confidenceLevel": conf,
        "confidenceReason": confidence_reason(conf, inventory, metrics, scores),
    }


def confidence_reason(conf: str, inventory: dict[str, Any], metrics: ImageMetrics, scores: dict[str, int]) -> str:
    if conf == "low":
        return "Weak or asset-like reference; keep as inventory evidence, not a stable rule source."
    if conf == "high":
        return "Product cue and readable image metrics both support the classification."
    return "Some product cue exists, but claim should stay heuristic until manual visual review confirms it."


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def pattern_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def select_refs(rows: list[dict[str, Any]], product_type: str | None = None, limit: int = 12) -> list[str]:
    filtered = [
        row
        for row in rows
        if (product_type is None or row["productType"] == product_type)
        and row["confidenceLevel"] in {"high", "medium"}
    ]
    filtered.sort(
        key=lambda row: (
            row["confidenceLevel"] != "high",
            -row["imageMetrics"].get("height", 0),
            row["sourcePath"].lower(),
        )
    )
    return [row["sourcePath"] for row in filtered[:limit]]


def build_patterns(ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}

    pattern_specs = [
        (
            "Product proof before feature detail",
            ["SaaS", "app landing", "dashboard/admin"],
            "opening strategy",
            "Product-led references tend to make the product legible before asking the buyer to believe feature claims.",
            "Use visible proof early, but transform the proof format and attention path per product.",
        ),
        (
            "Trust before contact or consultation",
            ["corporate/business", "finance/consulting", "medical/healthcare", "service business", "real estate"],
            "trust strategy",
            "Service and high-trust categories need credibility before the action path feels safe.",
            "Move proof, process, credentials, or outcomes before the primary contact push without copying section treatment.",
        ),
        (
            "Desire before transaction",
            ["ecommerce", "restaurant/food"],
            "conversion/action logic",
            "Commerce and food references need sensory/product desire before dense buying mechanics.",
            "Lead with desire and browse logic, then design a distinct purchase or booking path.",
        ),
        (
            "Identity before proof",
            ["agency/studio", "portfolio", "personal brand", "creative showcase"],
            "emotional rhythm",
            "Creative categories often need an immediate point of view before conventional proof lands.",
            "Express identity through a new art-direction move, then follow with concrete evidence of capability.",
        ),
        (
            "Featured-to-catalog rhythm",
            ["editorial/blog", "education/course"],
            "density strategy",
            "Content categories need a strong featured item, then scannable depth and taxonomy.",
            "Use hierarchy to teach browsing behavior; do not copy the exact card or grid treatment.",
        ),
        (
            "Completeness as buyer confidence",
            ["full website kit", "dashboard/admin", "ecommerce"],
            "marketplace completeness logic",
            "Template buyers trust products more when page/state coverage is visible, not merely implied.",
            "Show enough depth and states for the category while varying the page map and preview framing.",
        ),
        (
            "Premium detail through contrast control",
            PRODUCT_TYPES[:-1],
            "premium detail logic",
            "Repeated references use tone, contrast, spacing, and density control to make detail feel intentional.",
            "Translate contrast rhythm into a new visual system rather than reusing color/motif or effect language.",
        ),
    ]

    for title, product_types, cognition_area, claim, reusable_logic in pattern_specs:
        supporting = [
            row
            for row in ledger
            if row["productType"] in product_types and row["confidenceLevel"] in {"high", "medium"}
        ]
        if cognition_area == "premium detail logic":
            supporting = [
                row
                for row in supporting
                if row["imageMetrics"].get("contrast") in {"high", "medium"}
                and row["imageMetrics"].get("density") in {"balanced", "dense"}
            ]
        refs = [row["sourcePath"] for row in supporting[:20]]
        confidence_level = "high" if len(refs) >= 20 else "medium" if len(refs) >= 7 else "low"
        groups[pattern_id(title)] = {
            "patternId": pattern_id(title),
            "patternName": title,
            "cognitionArea": cognition_area,
            "observedEvidence": f"{len(refs)} supporting references across: "
            + ", ".join(sorted({row["productType"] for row in supporting})[:8]),
            "inferredDesignerReason": claim,
            "userBuyerEffect": "The viewer receives the type of proof needed before the next commitment.",
            "commercialFunction": "Makes the template feel more complete and category-ready for marketplace buyers.",
            "reusableThinkingLogic": reusable_logic,
            "originalityTransformation": "Keep the sequence of reasoning, but redesign composition, section treatment, component grouping, and CTA staging.",
            "confidenceLevel": confidence_level,
            "evidenceRefs": refs,
        }
    return list(groups.values())


def product_card(product_type: str, ledger: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for row in ledger if row["productType"] == product_type]
    high_medium = [row for row in rows if row["confidenceLevel"] in {"high", "medium"}]
    logic = PRODUCT_LOGIC[product_type]
    tone_counts = Counter(row["imageMetrics"].get("tone") for row in rows)
    density_counts = Counter(row["imageMetrics"].get("density") for row in rows)
    confidence = "high" if len(high_medium) >= 12 else "medium" if len(high_medium) >= 4 else "low"
    return {
        "productType": product_type,
        "referenceCount": len(rows),
        "usableEvidenceCount": len(high_medium),
        "confidenceLevel": confidence,
        "whatBuyerNeedsToBelieve": logic["belief"],
        "whatTemplateMustProve": logic["prove"],
        "commonOpeningStrategies": [logic["opening"]],
        "commonTrustStrategies": [logic["trust"]],
        "commonDensityRhythm": [logic["density"], f"observed tone mix: {dict(tone_counts)}", f"observed density mix: {dict(density_counts)}"],
        "commonComponentSystems": logic["components"],
        "requiredContentDepth": depth_guidance(product_type),
        "commonPremiumDetails": premium_details(rows),
        "commonFailureModes": [logic["failure"], "copying exact composition or component grouping from references"],
        "safeReusableThinkingPatterns": [
            "reuse buyer decision order and proof logic",
            "reuse calm/dense rhythm as a reasoning pattern",
            "reuse evidence-before-action logic when category risk is high",
        ],
        "bannedCopyRiskPatterns": [
            "exact composition",
            "exact pacing",
            "exact section treatment",
            "exact component grouping",
            "exact image placement",
            "exact visual motif",
            "distinctive CTA staging",
        ],
        "evidenceRefs": select_refs(ledger, product_type, 15),
    }


def depth_guidance(product_type: str) -> str:
    if product_type == "one-page landing page":
        return "Focused conversion depth: promise, benefits, proof, offer, objections, CTA."
    if product_type == "full website kit":
        return "Page-system depth: home variants, inner pages, content/detail screens, contact/utility states."
    if product_type in {"dashboard/admin", "ecommerce"}:
        return "State and flow depth matters: overview, detail, list/grid, action, and support states."
    if product_type == "unknown/needs review":
        return "Do not derive stable depth rules until manually reviewed."
    return "Full template depth should cover opening, proof, feature/service/content depth, objections, action, footer, and relevant inner-page cues."


def premium_details(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["insufficient evidence"]
    tone_counts = Counter(row["imageMetrics"].get("tone") for row in rows)
    contrast_counts = Counter(row["imageMetrics"].get("contrast") for row in rows)
    density_counts = Counter(row["imageMetrics"].get("density") for row in rows)
    result = [
        f"tone control appears as {tone_counts.most_common(1)[0][0]} in the largest cluster",
        f"contrast is commonly {contrast_counts.most_common(1)[0][0]}",
        f"detail density is commonly {density_counts.most_common(1)[0][0]}",
    ]
    return result


def markdown_list(values: list[str]) -> str:
    if not values:
        return "- None\n"
    return "\n".join(f"- {value}" for value in values) + "\n"


def build_cards_markdown(cards: list[dict[str, Any]]) -> str:
    lines = [
        "# Product-Specific Website Template Pattern Cards",
        "",
        f"Generated: {now_stamp()}",
        "",
        "These cards are reasoning aids, not copying instructions. Evidence counts come from the local `Template Website` corpus.",
        "",
    ]
    for card in cards:
        lines.extend(
            [
                f"## {card['productType']}",
                "",
                f"- Reference count: {card['referenceCount']}",
                f"- Usable evidence count: {card['usableEvidenceCount']}",
                f"- Confidence: {card['confidenceLevel']}",
                f"- What the buyer needs to believe: {card['whatBuyerNeedsToBelieve']}",
                f"- What the template must prove: {card['whatTemplateMustProve']}",
                f"- Required content depth: {card['requiredContentDepth']}",
                "",
                "### Common Opening Strategies",
                "",
                markdown_list(card["commonOpeningStrategies"]),
                "### Common Trust Strategies",
                "",
                markdown_list(card["commonTrustStrategies"]),
                "### Common Density Rhythm",
                "",
                markdown_list(card["commonDensityRhythm"]),
                "### Common Component Systems",
                "",
                f"- {card['commonComponentSystems']}",
                "",
                "### Common Premium Details",
                "",
                markdown_list(card["commonPremiumDetails"]),
                "### Common Failure Modes",
                "",
                markdown_list(card["commonFailureModes"]),
                "### Safe Reusable Thinking Patterns",
                "",
                markdown_list(card["safeReusableThinkingPatterns"]),
                "### Banned Copy-Risk Patterns",
                "",
                markdown_list(card["bannedCopyRiskPatterns"]),
                "### Evidence Refs",
                "",
                markdown_list(card["evidenceRefs"][:8]),
                "",
            ]
        )
    return "\n".join(lines)


def build_mindset_library(patterns: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    lines = [
        "# Website Template Designer Mindset Library",
        "",
        f"Generated: {now_stamp()}",
        "",
        "This library teaches Brain Design how to think from evidence in the local `Template Website` corpus. It is not a visual copying guide.",
        "",
        "## Core Use Rule",
        "",
        "Reuse the mental move, not the visible move. A mental move can be trust-before-pricing, evidence-before-action, calm-to-dense rhythm, or buyer-confidence sequencing. A visible move is a specific composition, motif, image placement, pacing, component grouping, or CTA staging.",
        "",
        "## Designer Cognition Moves Detected",
        "",
    ]
    for pattern in patterns:
        lines.extend(
            [
                f"### {pattern['patternName']}",
                "",
                f"- Cognition area: {pattern['cognitionArea']}",
                f"- Confidence: {pattern['confidenceLevel']}",
                f"- Observed evidence: {pattern['observedEvidence']}",
                f"- Inferred designer reason: {pattern['inferredDesignerReason']}",
                f"- User/buyer effect: {pattern['userBuyerEffect']}",
                f"- Commercial function: {pattern['commercialFunction']}",
                f"- Reusable thinking logic: {pattern['reusableThinkingLogic']}",
                f"- Originality transformation: {pattern['originalityTransformation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Product-Type Reasoning Index",
            "",
        ]
    )
    for card in cards:
        if card["confidenceLevel"] == "low":
            confidence_note = "Use only as tentative guidance until manual review."
        else:
            confidence_note = "Use as evidence-backed guidance, still with originality safeguards."
        lines.extend(
            [
                f"### {card['productType']}",
                "",
                f"- Buyer belief: {card['whatBuyerNeedsToBelieve']}",
                f"- Template proof obligation: {card['whatTemplateMustProve']}",
                f"- Reasoning confidence: {card['confidenceLevel']}. {confidence_note}",
                f"- Safe mental move: {card['safeReusableThinkingPatterns'][0]}",
                f"- Do not copy: {', '.join(card['bannedCopyRiskPatterns'][:4])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Originality Guard",
            "",
            "- Do not average all references into one master scaffold.",
            "- Do not convert premium references into sparse pages unless the product logic demands restraint.",
            "- Do not make page-level scaffolds universal rules.",
            "- Every strong rule needs evidence references and confidence level.",
            "- Low-confidence evidence can inspire a question, not a stable rule.",
            "",
        ]
    )
    return "\n".join(lines)


def build_proposed_rules(patterns: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    high_patterns = [pattern for pattern in patterns if pattern["confidenceLevel"] in {"high", "medium"}]
    strong_cards = [card for card in cards if card["confidenceLevel"] in {"high", "medium"}]
    lines = [
        "# Proposed Brain Design Rules: Website Template Mindset Library",
        "",
        f"Generated: {now_stamp()}",
        "",
        "Status: proposed only. Do not promote into core Brain Design rules until reviewed.",
        "",
        "## Proposed Rules",
        "",
        "1. For website template work, classify product type before selecting references, structure depth, proof sequence, density rhythm, or CTA logic.",
        "2. Use `Template Website` references as a product-type evidence corpus, not as a visual cloning source.",
        "3. Every Designer Cognition claim must include observed evidence, inferred reason, user/buyer effect, commercial function, reusable logic, originality transformation, and confidence level.",
        "4. Treat low-confidence and asset-like references as inventory signals only; do not promote them into stable rules.",
        "5. Build product-specific reasoning patterns. Do not turn hero/cards/CTA/footer into a universal website scaffold.",
        "6. For batch outputs, each template must start from its own product-type-matched evidence pool and pattern lock.",
        "7. Reuse abstract reasoning patterns such as trust-before-pricing, evidence-before-action, visual-proof-before-feature-detail, and calm-to-dense rhythm.",
        "8. Ban recognizable execution reuse: exact composition, exact pacing, exact section treatment, exact component grouping, exact image placement, exact motif, and distinctive CTA staging.",
        "",
        "## Evidence-Backed Pattern Candidates",
        "",
    ]
    for pattern in high_patterns:
        lines.extend(
            [
                f"### {pattern['patternName']}",
                "",
                f"- Confidence: {pattern['confidenceLevel']}",
                f"- Rule candidate: {pattern['reusableThinkingLogic']}",
                f"- Evidence count shown: {len(pattern['evidenceRefs'])}",
                f"- Evidence refs: {', '.join(pattern['evidenceRefs'][:5])}",
                "",
            ]
        )
    lines.extend(["## Product-Type Rule Candidates", ""])
    for card in strong_cards:
        lines.extend(
            [
                f"### {card['productType']}",
                "",
                f"- Confidence: {card['confidenceLevel']}",
                f"- Buyer belief rule: {card['whatBuyerNeedsToBelieve']}",
                f"- Proof obligation: {card['whatTemplateMustProve']}",
                f"- Failure guard: {card['commonFailureModes'][0]}",
                f"- Evidence refs: {', '.join(card['evidenceRefs'][:5])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Not Yet Stable",
            "",
            "The proposed rules above should remain in this learning folder until reviewed against real output quality. Do not overwrite `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`, or core workflow rules from this file alone.",
            "",
        ]
    )
    return "\n".join(lines)


def build_learning_report(inventory: list[dict[str, Any]], ledger: list[dict[str, Any]], patterns: list[dict[str, Any]], cards: list[dict[str, Any]]) -> str:
    distribution = Counter(row["possibleProductType"] for row in inventory)
    confidence_counts = Counter(row["confidenceLevel"] for row in ledger)
    gaps = [card["productType"] for card in cards if card["usableEvidenceCount"] < 4]
    weak_patterns = [pattern for pattern in patterns if pattern["confidenceLevel"] == "low"]
    strong_patterns = [pattern for pattern in patterns if pattern["confidenceLevel"] in {"high", "medium"}]

    lines = [
        "# Template Website Learning Report",
        "",
        f"Generated: {now_stamp()}",
        "",
        "## Scope",
        "",
        f"- Source folder: `{SOURCE_DIR.as_posix()}`",
        "- This is a learning report only. It does not promote rules into stable Brain Design files.",
        "",
        "## Method",
        "",
        "- Inventory and classification are generated from file paths, file names, image dimensions, tone, contrast, colorfulness, and edge-density metrics.",
        "- The evidence ledger uses actual image measurements as visible evidence, plus filename/product cues as weak semantic evidence.",
        "- This pass does not perform OCR or human-level layout reading across all files, so ambiguous references are intentionally marked low confidence.",
        "",
        "## Total Files Scanned",
        "",
        f"- Total image files scanned: {len(inventory)}",
        f"- Evidence ledger entries: {len(ledger)}",
        f"- Confidence distribution: {dict(confidence_counts)}",
        "",
        "## Product Type Distribution",
        "",
    ]
    for product_type, count in distribution.most_common():
        lines.append(f"- {product_type}: {count}")
    lines.extend(["", "## Strongest Repeated Patterns", ""])
    for pattern in strong_patterns:
        lines.extend(
            [
                f"- {pattern['patternName']} ({pattern['confidenceLevel']}): {pattern['inferredDesignerReason']}",
                f"  Evidence refs sampled: {len(pattern['evidenceRefs'])}",
            ]
        )
    lines.extend(["", "## Weak Or Uncertain Patterns", ""])
    if weak_patterns:
        for pattern in weak_patterns:
            lines.append(f"- {pattern['patternName']}: only {len(pattern['evidenceRefs'])} traceable refs in sampled support.")
    else:
        lines.append("- No low-confidence aggregate patterns were generated, but low-confidence individual references remain in the ledger.")
    lines.extend(["", "## Product Type Gaps", ""])
    if gaps:
        for gap in gaps:
            card = next(card for card in cards if card["productType"] == gap)
            lines.append(f"- {gap}: {card['usableEvidenceCount']} usable refs; keep as tentative.")
    else:
        lines.append("- No severe gaps under the current heuristic, but manual review is still recommended for ambiguous filenames.")
    lines.extend(
        [
            "",
            "## Recommended Brain Design Updates",
            "",
            "- Add a stable rule requiring product-type classification before website-template reference analysis.",
            "- Add an evidence ledger requirement for website-template cognition claims.",
            "- Add product-specific pattern cards as consultation material, not hard universal scaffolds.",
            "- Add confidence labels so weak evidence cannot masquerade as stable design truth.",
            "- Keep `Template Website` as a local Pattern Learning Pool and select one active product-purpose reference group for any specific output cycle. Use up to 10 varied references when enough matching candidates exist, then rotate groups for later same-product builds.",
            "",
            "## Risks Of Overfitting",
            "",
            "- File names can bias classification; visual metrics do not fully understand layout semantics.",
            "- Repeated references from one creator or marketplace category can make patterns look more universal than they are.",
            "- Strong visual motifs can tempt copying unless reasoning is separated from execution.",
            "- Tall preview images can hide interaction states, responsive behavior, and actual editability.",
            "- Asset-like files may inflate unknown or product counts if treated as complete templates.",
            "",
            "## Originality Safeguards",
            "",
            "- Reuse mental moves only: buyer confidence logic, evidence-before-action, calm-to-dense rhythm, visual proof logic.",
            "- Never copy exact composition, section treatment, component grouping, motif, image placement, pacing, or CTA staging.",
            "- Do not average many references into one bland scaffold.",
            "- Do not collapse dense/premium references into sparse output unless product logic supports it.",
            "- Treat low-confidence evidence as a question to investigate, not as a rule.",
            "",
            "## Generated Artifacts",
            "",
            "- `REFERENCE_INVENTORY.jsonl`",
            "- `EVIDENCE_LEDGER.jsonl`",
            "- `PATTERN_DATABASE.json`",
            "- `PRODUCT_PATTERN_CARDS.md`",
            "- `WEBSITE_TEMPLATE_MINDSET_LIBRARY.md`",
            "- `BRAIN_RULES_PROPOSED.md`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []

    for path in files():
        primary, secondary, notes, category_hint = classify(path)
        metrics = image_metrics(path)
        row = {
            "filePath": rel(path),
            "file_path": rel(path),
            "absolutePath": str(path),
            "fileName": path.name,
            "file_name": path.name,
            "extension": path.suffix.lower(),
            "folderCategoryHint": category_hint,
            "folder_category_hint": category_hint,
            "possibleProductType": primary,
            "possible_product_type": primary,
            "secondaryProductTypes": secondary,
            "secondary_product_types": secondary,
            "notes": notes,
        }
        inventory.append(row)
        ledger.append(evidence_entry(path, row, metrics))

    patterns = build_patterns(ledger)
    cards = [product_card(product_type, ledger) for product_type in PRODUCT_TYPES]
    database = {
        "generated": now_stamp(),
        "sourceFolder": str(SOURCE_DIR),
        "totalFilesScanned": len(inventory),
        "productTypeDistribution": dict(Counter(row["possibleProductType"] for row in inventory)),
        "confidenceDistribution": dict(Counter(row["confidenceLevel"] for row in ledger)),
        "patterns": patterns,
        "productCards": cards,
    }

    write_jsonl(OUT_DIR / "REFERENCE_INVENTORY.jsonl", inventory)
    write_jsonl(OUT_DIR / "EVIDENCE_LEDGER.jsonl", ledger)
    (OUT_DIR / "PATTERN_DATABASE.json").write_text(json.dumps(database, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "PRODUCT_PATTERN_CARDS.md").write_text(build_cards_markdown(cards), encoding="utf-8")
    (OUT_DIR / "WEBSITE_TEMPLATE_MINDSET_LIBRARY.md").write_text(build_mindset_library(patterns, cards), encoding="utf-8")
    (OUT_DIR / "BRAIN_RULES_PROPOSED.md").write_text(build_proposed_rules(patterns, cards), encoding="utf-8")
    (OUT_DIR / "LEARNING_REPORT.md").write_text(build_learning_report(inventory, ledger, patterns, cards), encoding="utf-8")

    print(f"scanned={len(inventory)}")
    print(f"output={OUT_DIR}")
    print("distribution=" + json.dumps(database["productTypeDistribution"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
