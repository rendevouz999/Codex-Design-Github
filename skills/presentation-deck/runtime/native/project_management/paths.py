#!/usr/bin/env python3
"""
PPT Master - Project Management Paths

Own the repository and Skill resource roots used by project-management modules.

Usage:
    Import the required path constants from project_management.paths.

Examples:
    from project_management.paths import PROJECTS_ROOT, SCHEMA_DIR

Dependencies:
    None (only uses the standard library)
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PACKAGE_DIR.parent
SKILL_DIR = SCRIPTS_DIR.parents[1]
REPO_ROOT = SKILL_DIR.parent.parent
PROJECTS_ROOT = Path.cwd() / "presentations"
SOURCE_TO_MD_DIR = SCRIPTS_DIR / "source_to_md"
CHARTS_DIR = SKILL_DIR / "resources" / "charts"
SCHEMA_DIR = SKILL_DIR / "resources" / "schemas"
SCAFFOLD_DIR = SKILL_DIR / "resources" / "scaffolds"
