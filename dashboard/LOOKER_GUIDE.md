# 📊 Guide Looker Studio — Makeup Sales Dashboard

Ce document décrit comment connecter les données et construire le dashboard
dans **Google Looker Studio** à partir des marts CSV générés par le pipeline ELT.

---

## 1. Sources de données à connecter

Importe chacun de ces fichiers CSV dans Looker Studio via **"Ajouter des données" → CSV Upload** :

| Fichier | Utilisation |
|---|---|
| `data/mart/mart_kpis.csv` | Cartes KPI (scorecards) |
| `data/mart/mart_brand.csv` | Graphiques par marque |
| `data/mart/mart_product.csv` | Graphiques par produit |
| `data/mart/mart_country.csv` | Carte géographique + barres |
| `data/mart/mart_channel.csv` | Donut / barres canaux |
| `data/mart/mart_monthly_trend.csv` | Graphique en courbe temporelle |
| `data/mart/mart_brand_country.csv` | Tableau croisé |
| `data/mart/mart_payment.csv` | Donut paiement |
| `data/mart/mart_price_segment.csv` | Barres segmentation prix |

---

## 2. Architecture du dashboard (4 pages)

### Page 1 — Vue d'ensemble (Overview)
```
┌────────────┬────────────┬────────────┬────────────┐
│ Total Rev. │ Nb Ventes  │ Unités     │ Prix moyen │  ← Scorecards KPI
│ $XXX,XXX   │   500      │  XX,XXX    │  $XX.XX    │
└────────────┴────────────┴────────────┴────────────┘
┌─────────────────────────┬──────────────────────────┐
│  Courbe mensuelle       │  Donut canal de vente    │
│  (mart_monthly_trend)   │  (mart_channel)          │
└─────────────────────────┴──────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  Carte géographique revenue par pays                 │
│  (mart_country)                                      │
└──────────────────────────────────────────────────────┘
```

### Page 2 — Analyse Marques & Produits
```
┌─────────────────────────┬──────────────────────────┐
│  Barres : Revenue/marque│  Barres : Revenue/produit│
│  (mart_brand)           │  (mart_product)          │
└─────────────────────────┴──────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  Tableau : Marque × Pays (mart_brand_country)        │
│  Colonnes : Brand | Country | Revenue | Units        │
└──────────────────────────────────────────────────────┘
```

### Page 3 — Géographie & Canaux
```
┌─────────────────────────┬──────────────────────────┐
│  Barres horizontales    │  Donut méthode paiement  │
│  Revenue par pays       │  (mart_payment)          │
│  (mart_country)         │                          │
└─────────────────────────┴──────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  Tableau : Produit × Canal (mart_product_channel)    │
└──────────────────────────────────────────────────────┘
```

### Page 4 — Segmentation & Prix
```
┌─────────────────────────┬──────────────────────────┐
│  Barres : Segments prix │  Scatter : Prix vs Rev.  │
│  (mart_price_segment)   │  (processed_sales)       │
└─────────────────────────┴──────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  Tableau détail transactions (processed_sales)       │
│  avec filtre : Pays, Marque, Produit, Canal, Mois    │
└──────────────────────────────────────────────────────┘
```

---

## 3. Filtres recommandés (contrôles de données)

Ajoute ces filtres en haut de chaque page :

- **Sélecteur de période** → champ `Date` (mart_monthly_trend ou processed_sales)
- **Filtre Pays** → `Country`
- **Filtre Marque** → `Brand`
- **Filtre Produit** → `Product_Type`
- **Filtre Canal** → `Sales_Channel`

---

## 4. Métriques calculées dans Looker Studio

Crée ces champs calculés directement dans Looker :

```
Revenue_Per_Unit = Revenue_USD / Units_Sold
Revenue_Share    = Revenue_USD / SUM(Revenue_USD)
Avg_Revenue      = AVG(Revenue_USD)
```

---

## 5. Palette de couleurs recommandée

Utilise cette palette cohérente dans tout le dashboard :

| Couleur | Hex | Usage |
|---|---|---|
| Violet | `#8B5CF6` | Marques, couleur principale |
| Cyan | `#06B6D4` | Produits |
| Ambre | `#F59E0B` | Pays, alertes |
| Rose | `#EC4899` | Canaux |
| Vert | `#10B981` | KPIs positifs |
| Rouge | `#EF4444` | KPIs négatifs |

---

## 6. Étapes pour publier

1. Va sur [lookerstudio.google.com](https://lookerstudio.google.com)
2. Clique **"Créer" → "Rapport"**
3. **"Ajouter des données"** → choisis **"Importer des fichiers"** ou connecte Google Sheets
4. Upload les fichiers CSV depuis `data/mart/`
5. Construis les visuels selon l'architecture ci-dessus
6. Clique **"Partager"** → génère un lien public ou restreint