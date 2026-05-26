"""
generate_scale_data.py
----------------------
Creates a synthetic 500 000-row dataset that mirrors the real Superstore
schema, distributions, and edge cases. Used to stress-test the pipeline,
dashboard, and dbt models at scale.

Usage:
    python scripts/generate_scale_data.py           # default 500k rows
    python scripts/generate_scale_data.py --rows 1000000
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "Superstore_500k.csv"

# ── domain pools ─────────────────────────────────────────────────
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
REGIONS = ["West", "East", "Central", "South"]

STATES_BY_REGION = {
    "West": ["California", "Washington", "Oregon", "Colorado", "Arizona",
             "Utah", "Nevada", "New Mexico", "Montana", "Idaho", "Wyoming"],
    "East": ["New York", "Pennsylvania", "New Jersey", "Massachusetts",
             "Connecticut", "Virginia", "Maryland", "North Carolina",
             "Florida", "Georgia"],
    "Central": ["Texas", "Illinois", "Ohio", "Michigan", "Indiana",
                "Minnesota", "Missouri", "Wisconsin", "Iowa", "Kansas"],
    "South": ["Tennessee", "Kentucky", "Louisiana", "Alabama",
              "Mississippi", "Arkansas", "Oklahoma", "South Carolina"],
}

CITIES_BY_STATE = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose"],
    "New York": ["New York City", "Buffalo", "Rochester", "Albany"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Illinois": ["Chicago", "Springfield", "Peoria", "Naperville"],
    "Washington": ["Seattle", "Tacoma", "Spokane", "Olympia"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Harrisburg", "Allentown"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
}

CATEGORIES = {
    "Technology": ["Phones", "Accessories", "Copiers", "Machines"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Storage", "Binders", "Paper", "Appliances",
                        "Art", "Envelopes", "Labels", "Fasteners", "Supplies"],
}

PRODUCT_PREFIXES = {
    "Phones": ["Samsung Galaxy", "Apple iPhone", "Motorola Edge", "Cisco IP Phone"],
    "Accessories": ["Logitech Mouse", "USB Hub", "Wireless Keyboard", "Webcam"],
    "Copiers": ["Canon MF", "HP LaserJet", "Brother MFC", "Xerox WorkCentre"],
    "Machines": ["HP Printer", "Epson Projector", "Dell Monitor", "Lenovo Dock"],
    "Chairs": ["Hon Task Chair", "Mesh Office Chair", "Executive Chair", "Folding Chair"],
    "Tables": ["Conference Table", "Adjustable Desk", "Round Table", "Corner Desk"],
    "Bookcases": ["Sauder Bookcase", "Metal Shelf", "O'Sullivan Bookcase", "Bush Bookcase"],
    "Furnishings": ["Desk Lamp", "Wall Clock", "Coat Rack", "Whiteboard"],
    "Storage": ["File Cabinet", "Storage Box", "Drawer Organizer", "Shelf Unit"],
    "Binders": ["GBC Binder", "Avery Binder", "Wilson Jones Binder", "Cardinal Binder"],
    "Paper": ["Xerox Copy Paper", "HP Multipurpose", "Hammermill Paper", "Southworth Paper"],
    "Appliances": ["Belkin Surge", "Holmes Heater", "Cuisinart Coffeemaker", "Hoover Vacuum"],
    "Art": ["Newell Pens", "Sanford Markers", "Faber Castell Set", "Prismacolor Pencils"],
    "Envelopes": ["Staples Envelopes", "Columbian Envelopes", "#10 White Envelopes"],
    "Labels": ["Avery Labels", "Staples Labels", "Self-Adhesive Labels"],
    "Fasteners": ["Staples Box", "Paper Clips", "Binder Clips", "Rubber Bands"],
    "Supplies": ["Scissors", "Tape Dispenser", "Glue Sticks", "Correction Tape"],
}

# sales distributions by category (mean, std)
SALES_PARAMS = {
    "Technology": (350, 500),
    "Furniture": (280, 400),
    "Office Supplies": (50, 80),
}

# discount probability weights by category
DISCOUNT_WEIGHTS = {
    "Technology": [0.45, 0.25, 0.15, 0.10, 0.05],
    "Furniture": [0.35, 0.20, 0.20, 0.15, 0.10],
    "Office Supplies": [0.50, 0.25, 0.10, 0.10, 0.05],
}
DISCOUNT_VALUES = [0.0, 0.10, 0.20, 0.30, 0.45]


def generate(n_rows: int = 500_000, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic Superstore dataset with realistic distributions."""
    rng = np.random.default_rng(seed)
    logger.info(f"Generating {n_rows:,} synthetic rows (seed={seed}) ...")

    # ── order structure ──────────────────────────────────────────
    n_orders = n_rows // 4  # ~4 items per order on average
    order_ids = [f"SYN-{y}-{i:06d}" for y in range(2014, 2018)
                 for i in range(n_orders // 4)]
    order_ids = rng.choice(order_ids, size=n_rows, replace=True)

    # dates spread across 2014-2017
    start = pd.Timestamp("2014-01-01")
    end = pd.Timestamp("2017-12-31")
    days_range = (end - start).days
    order_dates = start + pd.to_timedelta(rng.integers(0, days_range, size=n_rows), unit="D")

    ship_delays = rng.choice([0, 1, 2, 3, 4, 5, 6, 7], size=n_rows,
                             p=[0.05, 0.10, 0.15, 0.25, 0.20, 0.10, 0.10, 0.05])
    ship_dates = order_dates + pd.to_timedelta(ship_delays, unit="D")

    ship_modes = rng.choice(SHIP_MODES, size=n_rows,
                            p=[0.55, 0.20, 0.15, 0.10])

    # ── customers ────────────────────────────────────────────────
    n_customers = min(n_rows // 6, 5000)
    customer_ids = [f"CS-{i:05d}" for i in range(n_customers)]
    customer_names = [f"Customer_{i}" for i in range(n_customers)]

    cust_idx = rng.integers(0, n_customers, size=n_rows)
    segments = rng.choice(SEGMENTS, size=n_rows, p=[0.50, 0.30, 0.20])

    # ── geography ────────────────────────────────────────────────
    regions = rng.choice(REGIONS, size=n_rows, p=[0.30, 0.30, 0.25, 0.15])
    all_states = []
    for r in regions:
        all_states.append(rng.choice(STATES_BY_REGION[r]))
    states = np.array(all_states)

    cities = []
    for s in states:
        pool = CITIES_BY_STATE.get(s, [f"{s} City"])
        cities.append(rng.choice(pool))

    postal_codes = rng.integers(10000, 99999, size=n_rows)

    # ── products ─────────────────────────────────────────────────
    categories = rng.choice(list(CATEGORIES.keys()), size=n_rows,
                            p=[0.30, 0.30, 0.40])
    sub_categories = []
    product_names = []
    product_ids = []

    for cat in categories:
        sub = rng.choice(CATEGORIES[cat])
        sub_categories.append(sub)
        prefix = rng.choice(PRODUCT_PREFIXES.get(sub, [sub]))
        product_names.append(f"{prefix} #{rng.integers(100, 9999)}")
        product_ids.append(f"SYN-{cat[:3].upper()}-{rng.integers(1000, 9999)}")

    # ── financials ───────────────────────────────────────────────
    sales = np.zeros(n_rows)
    discounts = np.zeros(n_rows)
    profits = np.zeros(n_rows)
    quantities = rng.integers(1, 14, size=n_rows)

    for i in range(n_rows):
        cat = categories[i]
        mean, std = SALES_PARAMS[cat]
        s = max(rng.normal(mean, std), 1.0)
        sales[i] = round(s, 2)

        d = rng.choice(DISCOUNT_VALUES, p=DISCOUNT_WEIGHTS[cat])
        discounts[i] = d

        # profit margin: base 15%, eroded by discount
        base_margin = rng.normal(0.15, 0.05)
        margin = base_margin - d * rng.uniform(0.8, 1.5)
        profits[i] = round(sales[i] * margin, 2)

    # ── assemble DataFrame ───────────────────────────────────────
    df = pd.DataFrame({
        "Row ID": np.arange(1, n_rows + 1),
        "Order ID": order_ids,
        "Order Date": order_dates.strftime("%m/%d/%Y"),
        "Ship Date": ship_dates.strftime("%m/%d/%Y"),
        "Ship Mode": ship_modes,
        "Customer ID": [customer_ids[i] for i in cust_idx],
        "Customer Name": [customer_names[i] for i in cust_idx],
        "Segment": segments,
        "Country": "United States",
        "City": cities,
        "State": states,
        "Postal Code": postal_codes,
        "Region": regions,
        "Product ID": product_ids,
        "Category": categories,
        "Sub-Category": sub_categories,
        "Product Name": product_names,
        "Sales": sales,
        "Quantity": quantities,
        "Discount": discounts,
        "Profit": profits,
    })

    logger.info(f"Generated DataFrame: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Superstore data")
    parser.add_argument("--rows", type=int, default=500_000,
                        help="Number of rows to generate (default: 500000)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    df = generate(n_rows=args.rows, seed=args.seed)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved to {OUTPUT_PATH}")

    # quick sanity checks
    loss_pct = (df["Profit"] < 0).sum() / len(df) * 100
    logger.info(f"Sanity check — Loss rate: {loss_pct:.1f}%, "
                f"Avg sales: ${df['Sales'].mean():.2f}, "
                f"Avg discount: {df['Discount'].mean():.1%}")


if __name__ == "__main__":
    main()
