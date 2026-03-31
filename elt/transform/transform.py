"""
ELT - TRANSFORM
Transformation des données raw vers la couche processed (nettoyage, enrichissement).
"""

import pandas as pd
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRANSFORM] %(message)s")
log = logging.getLogger(__name__)

DB_PATH = Path("data/makeup_sales.db")


def load_raw() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM raw_sales", conn)
    conn.close()
    log.info(f"{len(df)} lignes chargées depuis raw_sales")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    log.info("--- Nettoyage ---")
    initial = len(df)

    # Supprimer doublons
    df = df.drop_duplicates(subset=["Sale_ID"])
    log.info(f"Doublons supprimés : {initial - len(df)}")

    # Supprimer NaN sur colonnes critiques
    df = df.dropna(subset=["Date", "Brand", "Product_Type", "Revenue_USD"])

    # Harmoniser la casse
    df["Brand"] = df["Brand"].str.strip()
    df["Product_Type"] = df["Product_Type"].str.strip().str.capitalize()
    df["Country"] = df["Country"].str.strip()
    df["Sales_Channel"] = df["Sales_Channel"].str.strip()
    df["Payment_Method"] = df["Payment_Method"].str.strip()

    # Supprimer prix et revenus négatifs ou nuls
    df = df[df["Price_USD"] > 0]
    df = df[df["Revenue_USD"] > 0]
    df = df[df["Units_Sold"] > 0]

    log.info(f"Lignes après nettoyage : {len(df)} (supprimées : {initial - len(df)})")
    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    log.info("--- Enrichissement ---")

    # Conversion date
    df["Date"] = pd.to_datetime(df["Date"])

    # Colonnes temporelles
    df["Year"]    = df["Date"].dt.year
    df["Month"]   = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%B")
    df["Quarter"] = df["Date"].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
    df["Week"]    = df["Date"].dt.isocalendar().week.astype(int)
    df["Day_of_Week"] = df["Date"].dt.day_name()

    # Revenue par unité (vérification cohérence)
    df["Revenue_Per_Unit"] = (df["Revenue_USD"] / df["Units_Sold"]).round(2)

    # Segment prix
    df["Price_Segment"] = pd.cut(
        df["Price_USD"],
        bins=[0, 30, 60, 90, float("inf")],
        labels=["Budget (<30$)", "Mid-range (30-60$)", "Premium (60-90$)", "Luxury (90$+)"],
    )

    # Segment volume
    df["Volume_Segment"] = pd.cut(
        df["Units_Sold"],
        bins=[0, 10, 25, 40, float("inf")],
        labels=["Low (1-10)", "Medium (11-25)", "High (26-40)", "Very High (41+)"],
    )

    # Revenue flag (top 25%)
    q75 = df["Revenue_USD"].quantile(0.75)
    df["Is_Top_Revenue"] = df["Revenue_USD"] >= q75

    log.info("Enrichissement terminé")
    return df


def save_processed(df: pd.DataFrame) -> None:
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("processed_sales", conn, if_exists="replace", index=False)
    df.to_csv("data/processed/makeup_sales_processed.csv", index=False)
    log.info(f"{len(df)} lignes sauvegardées dans processed_sales + CSV")
    conn.close()


def run():
    log.info("=== DÉMARRAGE TRANSFORMATION ===")
    df = load_raw()
    df = clean(df)
    df = enrich(df)
    save_processed(df)
    log.info("=== TRANSFORMATION TERMINÉE ===")
    return df


if __name__ == "__main__":
    run()