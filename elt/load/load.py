"""
ELT - LOAD (Data Marts)
Création des tables agrégées prêtes pour Looker Studio.
"""

import pandas as pd
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LOAD] %(message)s")
log = logging.getLogger(__name__)

DB_PATH = Path("data/makeup_sales.db")
MART_DIR = Path("data/mart")


def load_processed() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM processed_sales", conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def save_mart(df: pd.DataFrame, name: str, conn: sqlite3.Connection) -> None:
    df.to_sql(name, conn, if_exists="replace", index=False)
    df.to_csv(MART_DIR / f"{name}.csv", index=False)
    log.info(f"Mart '{name}' : {len(df)} lignes")


def build_marts(df: pd.DataFrame) -> None:
    conn = sqlite3.connect(DB_PATH)

    # ── Mart 1 : KPIs globaux ──────────────────────────────────────────────
    kpis = pd.DataFrame([{
        "Total_Revenue_USD":   round(df["Revenue_USD"].sum(), 2),
        "Total_Units_Sold":    int(df["Units_Sold"].sum()),
        "Total_Transactions":  len(df),
        "Avg_Revenue_Per_Sale": round(df["Revenue_USD"].mean(), 2),
        "Avg_Price_USD":       round(df["Price_USD"].mean(), 2),
        "Avg_Units_Per_Sale":  round(df["Units_Sold"].mean(), 2),
        "Max_Revenue_Sale":    round(df["Revenue_USD"].max(), 2),
        "Min_Revenue_Sale":    round(df["Revenue_USD"].min(), 2),
    }])
    save_mart(kpis, "mart_kpis", conn)

    # ── Mart 2 : Revenue par marque ────────────────────────────────────────
    brand = (
        df.groupby("Brand")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Transactions=("Sale_ID", "count"),
            Avg_Price=("Price_USD", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    brand["Revenue_Share_Pct"] = (brand["Revenue_USD"] / brand["Revenue_USD"].sum() * 100).round(2)
    save_mart(brand, "mart_brand", conn)

    # ── Mart 3 : Revenue par produit ───────────────────────────────────────
    product = (
        df.groupby("Product_Type")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Transactions=("Sale_ID", "count"),
            Avg_Price=("Price_USD", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    product["Revenue_Share_Pct"] = (product["Revenue_USD"] / product["Revenue_USD"].sum() * 100).round(2)
    save_mart(product, "mart_product", conn)

    # ── Mart 4 : Revenue par pays ──────────────────────────────────────────
    country = (
        df.groupby("Country")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Transactions=("Sale_ID", "count"),
            Avg_Price=("Price_USD", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    country["Revenue_Share_Pct"] = (country["Revenue_USD"] / country["Revenue_USD"].sum() * 100).round(2)
    save_mart(country, "mart_country", conn)

    # ── Mart 5 : Revenue par canal de vente ───────────────────────────────
    channel = (
        df.groupby("Sales_Channel")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Transactions=("Sale_ID", "count"),
        )
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    channel["Revenue_Share_Pct"] = (channel["Revenue_USD"] / channel["Revenue_USD"].sum() * 100).round(2)
    save_mart(channel, "mart_channel", conn)

    # ── Mart 6 : Tendance mensuelle ────────────────────────────────────────
    monthly = (
        df.groupby(["Year", "Month", "Month_Name", "Quarter"])
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Transactions=("Sale_ID", "count"),
        )
        .round(2)
        .reset_index()
        .sort_values(["Year", "Month"])
    )
    monthly["Revenue_Cumsum"] = monthly["Revenue_USD"].cumsum().round(2)
    save_mart(monthly, "mart_monthly_trend", conn)

    # ── Mart 7 : Croisement marque × pays ────────────────────────────────
    brand_country = (
        df.groupby(["Brand", "Country"])
        .agg(Revenue_USD=("Revenue_USD", "sum"), Units_Sold=("Units_Sold", "sum"))
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    save_mart(brand_country, "mart_brand_country", conn)

    # ── Mart 8 : Croisement produit × canal ──────────────────────────────
    product_channel = (
        df.groupby(["Product_Type", "Sales_Channel"])
        .agg(Revenue_USD=("Revenue_USD", "sum"), Units_Sold=("Units_Sold", "sum"))
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    save_mart(product_channel, "mart_product_channel", conn)

    # ── Mart 9 : Méthode de paiement ──────────────────────────────────────
    payment = (
        df.groupby("Payment_Method")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Transactions=("Sale_ID", "count"),
            Units_Sold=("Units_Sold", "sum"),
        )
        .round(2)
        .reset_index()
        .sort_values("Revenue_USD", ascending=False)
    )
    payment["Revenue_Share_Pct"] = (payment["Revenue_USD"] / payment["Revenue_USD"].sum() * 100).round(2)
    save_mart(payment, "mart_payment", conn)

    # ── Mart 10 : Segment prix ─────────────────────────────────────────────
    price_seg = (
        df.groupby("Price_Segment")
        .agg(
            Revenue_USD=("Revenue_USD", "sum"),
            Transactions=("Sale_ID", "count"),
            Units_Sold=("Units_Sold", "sum"),
            Avg_Price=("Price_USD", "mean"),
        )
        .round(2)
        .reset_index()
    )
    save_mart(price_seg, "mart_price_segment", conn)

    conn.close()
    log.info("Tous les marts ont été créés.")


def run():
    log.info("=== DÉMARRAGE LOAD (MARTS) ===")
    df = load_processed()
    build_marts(df)
    log.info("=== LOAD TERMINÉ ===")


if __name__ == "__main__":
    run()