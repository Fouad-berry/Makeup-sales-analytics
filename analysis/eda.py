"""
analysis/eda.py — Analyse Exploratoire (EDA)
Génère des statistiques et graphiques pour comprendre le dataset.
Exporte les figures dans analysis/figures/
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

DB_PATH = Path("data/makeup_sales.db")
FIG_DIR = Path("analysis/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = ["#8B5CF6", "#06B6D4", "#F59E0B", "#EC4899", "#10B981", "#EF4444", "#3B82F6", "#F97316"]
sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams["figure.dpi"] = 120
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False


def load() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM processed_sales", conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. Vue générale ────────────────────────────────────────────────────────
def overview(df):
    print_section("VUE GÉNÉRALE")
    print(f"Lignes       : {len(df):,}")
    print(f"Colonnes     : {df.shape[1]}")
    print(f"Période      : {df['Date'].min().date()} → {df['Date'].max().date()}")
    print(f"\nValeurs manquantes :\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"\nStatistiques numériques :\n{df[['Price_USD','Units_Sold','Revenue_USD']].describe().round(2)}")


# ── 2. Revenue par marque ──────────────────────────────────────────────────
def plot_brand_revenue(df):
    brand = df.groupby("Brand")["Revenue_USD"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(brand.index, brand.values, color=PALETTE[:len(brand)])
    ax.bar_label(bars, labels=[f"${v/1000:.1f}K" for v in brand.values], padding=4, fontsize=9)
    ax.set_title("Revenue total par marque", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_revenue_by_brand.png")
    plt.close()
    print("✓ Figure 1 : Revenue par marque")


# ── 3. Revenue par produit ─────────────────────────────────────────────────
def plot_product_revenue(df):
    prod = df.groupby("Product_Type")["Revenue_USD"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(prod.index, prod.values, color=PALETTE)
    ax.bar_label(bars, labels=[f"${v/1000:.1f}K" for v in prod.values], padding=4, fontsize=9)
    ax.set_title("Revenue total par type de produit", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_revenue_by_product.png")
    plt.close()
    print("✓ Figure 2 : Revenue par produit")


# ── 4. Tendance mensuelle ──────────────────────────────────────────────────
def plot_monthly_trend(df):
    monthly = df.groupby(["Year", "Month"])["Revenue_USD"].sum().reset_index()
    monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly["Period"], monthly["Revenue_USD"], marker="o", color=PALETTE[0], linewidth=2)
    ax.fill_between(monthly["Period"], monthly["Revenue_USD"], alpha=0.15, color=PALETTE[0])
    ax.set_title("Tendance mensuelle du Revenue", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "03_monthly_trend.png")
    plt.close()
    print("✓ Figure 3 : Tendance mensuelle")


# ── 5. Revenue par pays ────────────────────────────────────────────────────
def plot_country_revenue(df):
    country = df.groupby("Country")["Revenue_USD"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(country.index, country.values, color=PALETTE[:len(country)])
    ax.bar_label(bars, labels=[f"${v/1000:.1f}K" for v in country.values], padding=4, fontsize=9)
    ax.set_title("Revenue par pays", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    plt.tight_layout()
    plt.savefig(FIG_DIR / "04_revenue_by_country.png")
    plt.close()
    print("✓ Figure 4 : Revenue par pays")


# ── 6. Canal de vente ──────────────────────────────────────────────────────
def plot_channel(df):
    channel = df.groupby("Sales_Channel")["Revenue_USD"].sum().sort_values(ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].pie(channel.values, labels=channel.index, autopct="%1.1f%%", colors=PALETTE[:len(channel)], startangle=90)
    axes[0].set_title("Part de revenue par canal", fontweight="bold")
    bars = axes[1].bar(channel.index, channel.values, color=PALETTE[:len(channel)])
    axes[1].bar_label(bars, labels=[f"${v/1000:.1f}K" for v in channel.values], padding=4, fontsize=9)
    axes[1].set_title("Revenue par canal de vente", fontweight="bold")
    axes[1].set_ylabel("Revenue (USD)")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "05_revenue_by_channel.png")
    plt.close()
    print("✓ Figure 5 : Canal de vente")


# ── 7. Heatmap marque × pays ───────────────────────────────────────────────
def plot_heatmap(df):
    pivot = df.pivot_table(values="Revenue_USD", index="Brand", columns="Country", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(pivot / 1000, annot=True, fmt=".1f", cmap="Purples", ax=ax, linewidths=0.5, cbar_kws={"label": "Revenue (K$)"})
    ax.set_title("Heatmap Revenue (K$) : Marque × Pays", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "06_heatmap_brand_country.png")
    plt.close()
    print("✓ Figure 6 : Heatmap marque × pays")


# ── 8. Distribution prix & revenue ────────────────────────────────────────
def plot_distributions(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(df["Price_USD"], bins=20, color=PALETTE[0], edgecolor="white", alpha=0.85)
    axes[0].set_title("Distribution des prix (USD)", fontweight="bold")
    axes[0].set_xlabel("Price_USD")
    axes[1].hist(df["Revenue_USD"], bins=20, color=PALETTE[2], edgecolor="white", alpha=0.85)
    axes[1].set_title("Distribution du revenue (USD)", fontweight="bold")
    axes[1].set_xlabel("Revenue_USD")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "07_distributions.png")
    plt.close()
    print("✓ Figure 7 : Distributions")


# ── 9. Top insights ────────────────────────────────────────────────────────
def print_insights(df):
    print_section("TOP INSIGHTS")
    top_brand = df.groupby("Brand")["Revenue_USD"].sum().idxmax()
    top_product = df.groupby("Product_Type")["Revenue_USD"].sum().idxmax()
    top_country = df.groupby("Country")["Revenue_USD"].sum().idxmax()
    top_channel = df.groupby("Sales_Channel")["Revenue_USD"].sum().idxmax()
    top_payment = df.groupby("Payment_Method")["Revenue_USD"].sum().idxmax()
    total_rev = df["Revenue_USD"].sum()
    print(f"Revenue total     : ${total_rev:,.2f}")
    print(f"Marque #1         : {top_brand}")
    print(f"Produit #1        : {top_product}")
    print(f"Pays #1           : {top_country}")
    print(f"Canal #1          : {top_channel}")
    print(f"Paiement #1       : {top_payment}")
    print(f"Vente max         : ${df['Revenue_USD'].max():,.2f}")
    print(f"Prix moyen        : ${df['Price_USD'].mean():.2f}")
    print(f"Unités moy./vente : {df['Units_Sold'].mean():.1f}")


if __name__ == "__main__":
    df = load()
    overview(df)
    print_section("GÉNÉRATION DES FIGURES")
    plot_brand_revenue(df)
    plot_product_revenue(df)
    plot_monthly_trend(df)
    plot_country_revenue(df)
    plot_channel(df)
    plot_heatmap(df)
    plot_distributions(df)
    print_insights(df)
    print(f"\nToutes les figures sauvegardées dans : {FIG_DIR}/")