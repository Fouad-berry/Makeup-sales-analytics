"""
ELT - EXTRACT
Extraction du dataset brut CSV vers la couche raw (SQLite).
"""

import pandas as pd
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EXTRACT] %(message)s")
log = logging.getLogger(__name__)

RAW_CSV = Path("data/raw/makeup_sales_dataset_2025.csv")
DB_PATH = Path("data/makeup_sales.db")


def extract() -> pd.DataFrame:
    """Charge le CSV brut sans transformation."""
    log.info(f"Lecture du fichier source : {RAW_CSV}")
    df = pd.read_csv(RAW_CSV)
    log.info(f"{len(df)} lignes extraites, {df.shape[1]} colonnes")
    log.info(f"Colonnes : {list(df.columns)}")
    return df


def load_to_raw(df: pd.DataFrame) -> None:
    """Charge les données brutes telles quelles dans la table raw."""
    conn = sqlite3.connect(DB_PATH)
    df["_extracted_at"] = datetime.utcnow().isoformat()
    df.to_sql("raw_sales", conn, if_exists="replace", index=False)
    log.info(f"{len(df)} lignes chargées dans raw_sales (DB : {DB_PATH})")
    conn.close()


def run():
    log.info("=== DÉMARRAGE EXTRACTION ===")
    df = extract()
    load_to_raw(df)
    log.info("=== EXTRACTION TERMINÉE ===")
    return df


if __name__ == "__main__":
    run()