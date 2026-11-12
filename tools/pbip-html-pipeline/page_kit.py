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


def lint(html):
    bad = [label for pat, label in FORBIDDEN if re.search(pat, html, re.I)]
    if re.search(r"\binfinite\b", html):
        bad.append("infinite animation (every loop must stop: finite iteration counts, done by ~6 s)")
    if html.count("<style") > 1:
        bad.append("more than one <style> (one per measure)")
    return bad


def fluid(html, design_w=1920, design_h=1080):
    if "var(--u)" not in html:
        html = re.sub(r"(?<![\w#.-])(-?\d*\.?\d+)px", lambda m: f"calc({m.group(1)}*var(--u))", html)
        html = html.replace("<style>", f"<style>:root{{--u:min(calc(100vw/{design_w}),calc(100vh/{design_h}))}}", 1)
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


def dax_literal(html, chunk=3000):
    parts = [html[i:i + chunk] for i in range(0, len(html), chunk)]
    return "\n& ".join('"' + p.replace('"', '""') + '"' for p in parts)
