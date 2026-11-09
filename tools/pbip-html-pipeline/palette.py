# -*- coding: utf-8 -*-
"""Color tokens for the dashboard. measures.py writes @@token@@ placeholders; add() resolves them
with the ACTIVE palette. 'ocean' reproduces the original hand-tuned colors exactly (regression baseline).

Switch:  set environment variable DASH_PALETTE=midnight (or edit ACTIVE) and rebuild.
Every palette defines every token; text-on-soft tokens (*_text) are chosen for WCAG >= 4.5:1.
"""
import os

PALETTES = {
    "ocean": {  # light, enterprise-calm (original)
        "page_bg": "#F4F7FA", "outspace_bg": "#F4F7FA",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#F4F7FA", "bg_mid": "#F4F7FA", "bg_to": "#F4F7FA", "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#1F2937", "fg2": "#605E5C", "fg3": "#4B5563", "muted": "#8A8886",
        "primary": "#0F6CBD", "primary_text": "#0F4C8A", "active_text": "#0F6CBD", "primary_soft": "#E6F0FA",
        "design": "#8764B8", "design_text": "#6B4C9A", "design_soft": "#F1ECF8",   # v002: text darkened for WCAG 4.5:1
        "maint": "#00A3AE", "maint_text": "#00747C", "maint_soft": "#E0F6F7",
        "done": "#107C10", "done_text": "#107C10", "done_soft": "#E5F2E5",
        "bad": "#D13438", "bad_soft": "#FBE7E7", "neutral_soft": "#F3F2F1",
        "track": "#EEF2F6", "border": "#E1E5EA", "divider": "#EEF1F4", "divider2": "#F0F2F5",
        "grid": "#E8ECF1", "connector": "#D6DCE3", "arrow": "#A0A8B3", "inset": "#F6F8FB",
        "series3": "#5B5FC7", "series4": "#CA5010", "shadow": "rgba(16,24,40,.10)",
        "slicer_fg": "#1F2937", "slicer_bg": "#FFFFFF", "slicer_border": "#C8CED6",
    },
    "midnight": {  # dark, full system (bg + surface + fg), from library/palettes.md #5
        "page_bg": "#141A22", "outspace_bg": "#141A22",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#141A22", "bg_mid": "#141A22", "bg_to": "#141A22", "surface": "#1D2632", "on_accent": "#FFFFFF",
        "fg": "#E8EDF2", "fg2": "#A9B4C0", "fg3": "#C3CCD6", "muted": "#7A8794",
        "primary": "#4EA3F1", "primary_text": "#9CCBF7", "active_text": "#9CCBF7", "primary_soft": "#1F3B57",
        "design": "#9B8AFB", "design_text": "#C4B9FD", "design_soft": "#2E2A4F",
        "maint": "#34D3BE", "maint_text": "#7FE6D8", "maint_soft": "#163A3A",
        "done": "#4CC38A", "done_text": "#8EDDB6", "done_soft": "#173826",
        "bad": "#F16B6B", "bad_soft": "#3D2024", "neutral_soft": "#2A3646",
        "track": "#2A3646", "border": "#33404F", "divider": "#2A3646", "divider2": "#2A3646",
        "grid": "#2E3A49", "connector": "#3E4C5C", "arrow": "#6E7C8B", "inset": "#18212C",
        "series3": "#9B8AFB", "series4": "#F0B35E", "shadow": "rgba(0,0,0,.35)",
        "slicer_fg": "#E8EDF2", "slicer_bg": "#1D2632", "slicer_border": "#3E4C5C",
    },
    "berry": {  # light, colorful (marketing/product), from library/palettes.md #4
        "page_bg": "#FAF5F8", "outspace_bg": "#FAF5F8",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#FAF5F8", "bg_mid": "#FAF5F8", "bg_to": "#FAF5F8", "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#2B1F29", "fg2": "#6B5A68", "fg3": "#4A3B47", "muted": "#A79AA4",
        "primary": "#7C2D5E", "primary_text": "#6A2550", "active_text": "#7C2D5E", "primary_soft": "#F4E6EF",
        "design": "#4A3B76", "design_text": "#4A3B76", "design_soft": "#ECE8F5",
        "maint": "#E56BA0", "maint_text": "#A8336A", "maint_soft": "#FBE7F0",
        "done": "#3E7D4E", "done_text": "#2F6A3E", "done_soft": "#E6F2E9",
        "bad": "#D13438", "bad_soft": "#FBE7E7", "neutral_soft": "#F1E4EC",
        "track": "#F1E4EC", "border": "#E8D8E2", "divider": "#F3EAF0", "divider2": "#F3EAF0",
        "grid": "#EEE2EA", "connector": "#DCCAD6", "arrow": "#B3A2AE", "inset": "#FBF7FA",
        "series3": "#D9A441", "series4": "#4A3B76", "shadow": "rgba(43,31,41,.10)",
        "slicer_fg": "#2B1F29", "slicer_bg": "#FFFFFF", "slicer_border": "#DCCAD6",
    },
    "vivid": {  # colorful: gradient page (indigo -> violet -> pink), filled KPI cards, saturated status colors
        "page_bg": "#4C1D95", "outspace_bg": "#312E81",
        "kpi_filled": "1", "bg_layer": "1", "bg_from": "#312E81", "bg_mid": "#6D28D9", "bg_to": "#BE185D",
        "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#1E1B4B", "fg2": "#475569", "fg3": "#334155", "muted": "#94A3B8",
        "primary": "#1D4ED8", "primary_text": "#1E3A8A", "active_text": "#1D4ED8", "primary_soft": "#DBEAFE",
        "design": "#7C3AED", "design_text": "#5B21B6", "design_soft": "#EDE9FE",
        "maint": "#0F766E", "maint_text": "#115E59", "maint_soft": "#CCFBF1",
        "done": "#15803D", "done_text": "#166534", "done_soft": "#DCFCE7",
        "bad": "#C81E1E", "bad_soft": "#FEE2E2", "neutral_soft": "#EEF2FF",
        "track": "#EEF2FF", "border": "#E0E7FF", "divider": "#EEF2FF", "divider2": "#EEF2FF",
        "grid": "#E0E7FF", "connector": "#C7D2FE", "arrow": "#A5B4FC", "inset": "#F5F3FF",
        "series3": "#DB2777", "series4": "#F59E0B", "shadow": "rgba(30,27,75,.30)",
        "slicer_fg": "#1E1B4B", "slicer_bg": "#FFFFFF", "slicer_border": "#C7D2FE",
    },
}

ACTIVE = os.environ.get("DASH_PALETTE", "ocean")
P = PALETTES[ACTIVE]
assert all(set(v) == set(PALETTES["ocean"]) for v in PALETTES.values()), "every palette must define every token"


def resolve(text, palette=None):
    pal = PALETTES[palette] if palette else P
    for k, v in pal.items():
        text = text.replace(f"@@{k}@@", v)
    assert "@@" not in text, "unresolved color token"
    return text
