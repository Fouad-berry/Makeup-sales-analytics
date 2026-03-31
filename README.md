# 💄 Makeup Sales Analytics — ELT Pipeline & Looker Dashboard

> Pipeline ELT complet sur un dataset de ventes cosmétiques 2025 :  
> extraction CSV → nettoyage → enrichissement → data marts → visualisation Looker Studio.

---

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Dataset](#dataset)
- [Architecture ELT](#architecture-elt)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Data Marts](#data-marts)
- [Dashboard Looker](#dashboard-looker)
- [Tests](#tests)
- [Insights clés](#insights-clés)

---

## Aperçu

Ce projet implémente un pipeline **ELT (Extract → Load → Transform)** complet sur un dataset de ventes maquillage couvrant **8 marques**, **8 pays**, **5 canaux de vente** et **9 types de produits** sur l'année 2025.

**Stack technique :**
- Python (pandas, matplotlib, seaborn)
- SQLite (base de données locale)
- Google Looker Studio (visualisation)
- pytest (tests unitaires)

---

## Dataset

**Fichier source :** `data/raw/makeup_sales_dataset_2025.csv`

| Colonne | Type | Description |
|---|---|---|
| `Sale_ID` | int | Identifiant unique de la vente |
| `Date` | date | Date de la transaction |
| `Brand` | str | Marque (MAC, Dior, L'Oreal, etc.) |
| `Product_Type` | str | Type de produit (Lipstick, Blush, etc.) |
| `Country` | str | Pays de vente |
| `Sales_Channel` | str | Canal (Online, Retail Store, Mall, Beauty Salon) |
| `Payment_Method` | str | Mode de paiement (Card, Cash, Digital Wallet) |
| `Price_USD` | float | Prix unitaire en USD |
| `Units_Sold` | int | Nombre d'unités vendues |
| `Revenue_USD` | float | Chiffre d'affaires de la transaction |

**Marques :** MAC, Dior, L'Oreal, Fenty Beauty, Huda Beauty, Estee Lauder, NARS, Maybelline  
**Pays :** USA, UK, France, Germany, UAE, India, Canada, Saudi Arabia

---

## Architecture ELT

```
┌──────────────────────────────────────────────────────────────────┐
│                        PIPELINE ELT                              │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐  │
│  │   EXTRACT   │──▶│    LOAD     │──▶│     TRANSFORM        │  │
│  │             │   │  (raw DB)   │   │                      │  │
│  │ CSV → pandas│   │ raw_sales   │   │ Nettoyage            │  │
│  │             │   │ (SQLite)    │   │ Enrichissement       │  │
│  └─────────────┘   └─────────────┘   └──────────┬───────────┘  │
│                                                  │              │
│                                                  ▼              │
│                                    ┌─────────────────────────┐  │
│                                    │    LOAD (DATA MARTS)    │  │
│                                    │                         │  │
│                                    │ mart_kpis               │  │
│                                    │ mart_brand              │  │
│                                    │ mart_product            │  │
│                                    │ mart_country            │  │
│                                    │ mart_channel            │  │
│                                    │ mart_monthly_trend      │  │
│                                    │ mart_brand_country      │  │
│                                    │ mart_product_channel    │  │
│                                    │ mart_payment            │  │
│                                    │ mart_price_segment      │  │
│                                    └────────────┬────────────┘  │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │    LOOKER STUDIO        │
                                    │    DASHBOARD            │
                                    │                         │
                                    │  Page 1 : Overview      │
                                    │  Page 2 : Brands        │
                                    │  Page 3 : Geo & Channels│
                                    │  Page 4 : Segmentation  │
                                    └─────────────────────────┘
```

---

## Structure du projet

```
makeup_sales_analytics/
│
├── data/
│   ├── raw/
│   │   └── makeup_sales_dataset_2025.csv   ← dataset source
│   ├── processed/
│   │   └── makeup_sales_processed.csv      ← données nettoyées + enrichies
│   ├── mart/
│   │   ├── mart_kpis.csv
│   │   ├── mart_brand.csv
│   │   ├── mart_product.csv
│   │   ├── mart_country.csv
│   │   ├── mart_channel.csv
│   │   ├── mart_monthly_trend.csv
│   │   ├── mart_brand_country.csv
│   │   ├── mart_product_channel.csv
│   │   ├── mart_payment.csv
│   │   └── mart_price_segment.csv
│   └── makeup_sales.db                     ← SQLite (généré)
│
├── elt/
│   ├── extract/
│   │   └── extract.py                      ← Lecture CSV → raw DB
│   ├── transform/
│   │   └── transform.py                    ← Nettoyage + enrichissement
│   └── load/
│       └── load.py                         ← Construction des data marts
│
├── analysis/
│   ├── eda.py                              ← Analyse exploratoire + figures
│   └── figures/                            ← Graphiques générés (PNG)
│
├── dashboard/
│   └── LOOKER_GUIDE.md                     ← Guide de construction du dashboard
│
├── tests/
│   └── test_pipeline.py                    ← Tests unitaires (pytest)
│
├── logs/                                   ← Logs des exécutions pipeline
├── pipeline.py                             ← Orchestrateur ELT principal
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

```bash
# 1. Cloner le repo
git https://github.com/Fouad-berry/Makeup-sales-analytics.git
cd makeup-sales-analytics

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate        # Mac/Linux
# ou : venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Utilisation

### Lancer le pipeline complet ELT

```bash
python pipeline.py
```

Cela exécute en séquence :
1. **Extract** — lit le CSV source
2. **Load (raw)** — charge dans SQLite sans transformation
3. **Transform** — nettoie et enrichit les données
4. **Load (marts)** — génère les 10 tables agrégées + CSV

### Lancer uniquement un step

```bash
python elt/extract/extract.py
python elt/transform/transform.py
python elt/load/load.py
```

### Générer l'analyse exploratoire

```bash
python analysis/eda.py
```

Les figures PNG sont sauvegardées dans `analysis/figures/`.

---

## Data Marts

| Mart | Description | Granularité |
|---|---|---|
| `mart_kpis` | KPIs globaux (revenue total, nb ventes…) | 1 ligne |
| `mart_brand` | Revenue, unités, transactions par marque | Par marque |
| `mart_product` | Revenue, unités par type de produit | Par produit |
| `mart_country` | Revenue par pays + part marché | Par pays |
| `mart_channel` | Revenue par canal de vente | Par canal |
| `mart_monthly_trend` | Tendance mensuelle + cumul | Par mois |
| `mart_brand_country` | Croisement marque × pays | Par marque × pays |
| `mart_product_channel` | Croisement produit × canal | Par produit × canal |
| `mart_payment` | Revenue par méthode de paiement | Par paiement |
| `mart_price_segment` | Budget / Mid / Premium / Luxury | Par segment |

---

## Dashboard Looker

Voir le guide détaillé : [`dashboard/LOOKER_GUIDE.md`](dashboard/LOOKER_GUIDE.md)

**4 pages :**
- **Overview** — KPIs, courbe mensuelle, carte géographique
- **Brands & Products** — Revenue par marque et produit, tableau croisé
- **Geo & Channels** — Pays, canaux, méthodes de paiement
- **Segmentation** — Prix segments, distribution, détail transactions

---

## Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ -v --tb=short
```

Les tests couvrent :
- Suppression des doublons
- Filtrage des valeurs négatives
- Harmonisation de la casse
- Création des colonnes temporelles
- Cohérence prix × unités = revenue
- Qualité des données (nulls, types)

---

## Insights clés

> Ces insights sont calculés automatiquement par `analysis/eda.py`

- **Revenue total** : calculé sur toutes les transactions valides
- **Marque top** : identifiée par agrégation de revenue
- **Canal dominant** : Online ou Retail selon la période
- **Saisonnalité** : pic visible sur certains mois (voir courbe mensuelle)
- **Segment prix** : la majorité des ventes tombe en Mid-range (30-60$)

---

## Auteur

**Fouad MOUTAIROU** — Analytics engineer

Stack : Python · Pandas · SQLite · Looker Studio · pytest

---
