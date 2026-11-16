# -*- coding: utf-8 -*-
"""Helpers for a full-page HTML Content visual (Pattern A, one fullscreen measure) built with
skills/motion-design-dashboards. Python stdlib only.

  lint(html)          -> list of Secure-edition violations ([] = clean) + counts
  fluid(html)         -> every Npx becomes calc(N*var(--u)); --u = 1px at the design size, scales with the visual;
                         also pins the root line-height/font-size (HTML Content injects its own - measured in Desktop)
  dax_literal(html)   -> the HTML as a DAX string expression (chunks joined with &, quotes doubled) for a static measure

Measured in Power BI Desktop (Secure edition, Nov 2026):
  * a fixed-px 1920x1080 page was clipped at the bottom of its cards; the cause was the visual's own injected
    line-height/font-size, fixed by an explicit root line-height:normal;font-size:16px (gated render unchanged)
  * fluid() keeps the render pixel-identical at the design size (checked with an image diff)"""
import re

FORBIDDEN = [(r"<script", "script"), (r"\son[a-z]+\s*=", "inline on* handler"), (r"<link", "<link>"),
             (r"@import", "@import"), (r"url\(\s*['\"]?(https?:)?//", "external url()"), (r"<video", "<video>"),
             (r"<iframe", "<iframe>"), (r"<input", "form control"), (r"<button", "button (fake control)"),
             (r"<form", "<form>"), (r"<img[^>]+src=['\"]?https?:", "remote image"),
             (r"prefers-reduced-motion", "prefers-reduced-motion query (Desktop reports 'reduce' when Windows animation effects are off and the query hid all motion)")]


def _code(html):
    """the markup and CSS only (tags + <style> bodies), so page text such as 'infinite scroll' or ' on = ' never trips lint"""
    return " ".join(re.findall(r"<[^>]+>", html) + re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))


def lint(html):
    code = _code(html)
    bad = [label for pat, label in FORBIDDEN if re.search(pat, code, re.I)]
    if re.search(r"\binfinite\b", code):
        bad.append("infinite animation (every loop must stop: finite iteration counts, done by ~6 s)")
    if html.count("<style") > 1:
        bad.append("more than one <style> (one per measure)")
    return bad


def fluid(html, design_w=1920, design_h=1080):
    if "zoom:min(calc(100vw" in html:   # a live-DAX page scaled by zoom_root_style(): already scales, leave it as it is
        return html
    if "var(--u)" not in html:
        px = lambda t: re.sub(r"(?<![\w#.-])(-?\d*\.?\d+)px", lambda m: f"calc({m.group(1)}*var(--u))", t)
        # only CSS: <style> bodies and style='...' attributes - never visible text or other attribute values
        html = re.sub(r"(<style[^>]*>)(.*?)(</style>)", lambda m: m.group(1) + px(m.group(2)) + m.group(3), html, flags=re.S)
        html = re.sub(r"""(\sstyle=)(['"])(.*?)\2""", lambda m: m.group(1) + m.group(2) + px(m.group(3)) + m.group(2), html, flags=re.S)
        root_u = f":root{{--u:min(calc(100vw/{design_w}),calc(100vh/{design_h}))}}"
        # every converted px needs --u: a <style> with attributes, or a page with inline styles only, left it undefined
        html, n = re.subn(r"(<style[^>]*>)", lambda m: m.group(1) + root_u, html, count=1)
        if not n:
            html = f"<style>{root_u}</style>" + html
    if "data-lh='1'" not in html:
        # merge into the root's own style attribute: a second style attribute is dropped by the browser, and a wrapper
        # element makes the fit gate treat the real root as a child touching the edge (both caught on a real page)
        html = html.strip()
        m = re.match(r"<div\b([^>]*)>", html)
        if m:
            attrs = m.group(1)
            sm = re.search(r"""style=(['"])(.*?)\1""", attrs, re.S)
            if sm:
                attrs = attrs.replace(sm.group(0), f"style={sm.group(1)}line-height:normal;font-size:16px;{sm.group(2)}{sm.group(1)}", 1)
            else:
                attrs += " style='line-height:normal;font-size:16px'"
            html = f"<div data-lh='1'{attrs}>" + html[m.end():]
    return html


def zoom_root_style(design_w=1920, design_h=1080):
    """style for EVERY root <div> of a LIVE DAX page (incl. the empty-state branch): its px values are partly computed
    in DAX (FORMAT(...) & "px"), so fluid() cannot convert them. The root keeps the design size and CSS zoom scales it
    to the visual (measured in Desktop with the filter pane open: complete page, nothing clipped). Gate at the design
    size, where zoom = 1 - at other sizes the fit gate reads scrollHeight in unzoomed units (false 'taller')."""
    return (f"line-height:normal;font-size:16px;width:{design_w}px;height:{design_h}px;"
            f"zoom:min(calc(100vw / {design_w}px),calc(100vh / {design_h}px))")


def dax_literal(html, chunk=3000):
    parts = [html[i:i + chunk] for i in range(0, len(html), chunk)]
    return "\n& ".join('"' + p.replace('"', '""') + '"' for p in parts)
