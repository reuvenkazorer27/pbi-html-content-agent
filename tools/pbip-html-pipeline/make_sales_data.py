# -*- coding: utf-8 -*-
"""Invented sales orders for measures_example_sales.py (seeded, reproducible, no real names).
Writes <project>/data/orders.csv when this folder is <project>/_build."""
import csv, os, random
from datetime import date, timedelta

random.seed(20261110)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "orders.csv")

REGIONS = {"North": 1.25, "South": 0.9, "East": 1.1, "West": 1.0, "Central": 0.7}
CATS = {"Hardware": ["Laptop", "Monitor", "Dock", "Headset"], "Software": ["Suite license", "Security add-on", "Analytics seat"],
        "Services": ["Onboarding", "Support plan", "Training day"]}
PRICE = {"Laptop": 1450, "Monitor": 320, "Dock": 210, "Headset": 95, "Suite license": 540, "Security add-on": 180,
         "Analytics seat": 720, "Onboarding": 2400, "Support plan": 1100, "Training day": 1800}
CHANNELS = {"Direct": 0.45, "Partner": 0.35, "Online": 0.20}
REPS = ["Alex Rivera", "Sam Taylor", "Jordan Lee", "Casey Brooks", "Riley Chen", "Morgan Patel", "Taylor Kim", "Jamie Ortiz",
        "Avery Shah", "Quinn Novak"]
STATUS = [("Delivered", 0.78), ("Shipped", 0.10), ("Processing", 0.07), ("Returned", 0.05)]


def pick(d):
    r, acc = random.random() * sum(d.values()), 0
    for k, w in d.items():
        acc += w
        if r <= acc:
            return k
    return k


start = date(2025, 12, 1)
rows = []
for i in range(1, 901):
    d = start + timedelta(days=int(random.random() ** 0.8 * 344))
    region = pick(REGIONS)
    cat = pick({"Hardware": 0.5, "Software": 0.3, "Services": 0.2})
    prod = random.choice(CATS[cat])
    units = max(1, int(random.gauss(4 if cat == "Hardware" else 2, 2)))
    disc = random.choice([0, 0, 0, 0.05, 0.1, 0.15])
    amount = round(PRICE[prod] * units * (1 - disc) * random.uniform(0.92, 1.08) * REGIONS[region] ** 0.3, 2)
    status = pick(dict(STATUS))
    rep = random.choice(REPS[:7] if region != "Central" else REPS[5:]) if random.random() < 0.95 else ""
    rows.append({"OrderID": f"SO-{10000 + i}", "OrderDate": d.isoformat(), "Region": region, "Category": cat, "Product": prod,
                 "Channel": pick(CHANNELS), "Rep": rep, "Units": units, "Amount": amount, "Discount": disc, "Status": status})

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} invented orders -> {os.path.normpath(OUT)}")
