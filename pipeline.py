"""
pipeline.py — Orchestrateur ELT complet
Exécute Extract → Load (raw) → Transform → Load (marts) en séquence.
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"),
    ],
)
log = logging.getLogger(__name__)


def run_pipeline():
    start = datetime.utcnow()
    log.info("=" * 60)
    log.info("  MAKEUP SALES — PIPELINE ELT")
    log.info(f"  Démarrage : {start.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    log.info("=" * 60)

    try:
        # ── STEP 1 : EXTRACT ──────────────────────────────────────────────
        log.info("STEP 1/3 — EXTRACT")
        from elt.extract.extract import run as extract_run
        extract_run()

        # ── STEP 2 : TRANSFORM ───────────────────────────────────────────
        log.info("STEP 2/3 — TRANSFORM")
        from elt.transform.transform import run as transform_run
        transform_run()

        # ── STEP 3 : LOAD (DATA MARTS) ───────────────────────────────────
        log.info("STEP 3/3 — LOAD MARTS")
        from elt.load.load import run as load_run
        load_run()

        duration = (datetime.utcnow() - start).total_seconds()
        log.info("=" * 60)
        log.info(f"  PIPELINE TERMINÉ EN {duration:.1f}s")
        log.info("=" * 60)

    except Exception as e:
        log.error(f"ERREUR PIPELINE : {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import os
    os.makedirs("logs", exist_ok=True)
    run_pipeline()