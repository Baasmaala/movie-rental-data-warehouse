"""
Movie Rental Data Warehouse - Visualization Script
====================================================
Reads the CSV outputs from business_queries.sql and generates
chart images (PNG) for the 10 main business questions.

Author: Basmala
Course: Data Warehousing
Project: Movie Rental DW
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# =====================================================
# CONFIGURATION
# =====================================================
RESULTS_DIR = "results"      # folder where the CSV files live
CHARTS_DIR = "charts"        # folder where the PNG files will be saved

# Make sure the output folder exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# A consistent visual style across all charts
plt.style.use("seaborn-v0_8-whitegrid")

# Color palettes (so charts look cohesive, not random)
BAR_COLOR = "#2E86AB"        # blue
ACCENT_COLOR = "#E63946"     # red
SUCCESS_COLOR = "#06A77D"    # green
NEUTRAL_COLOR = "#6C757D"    # gray

print("Generating charts...\n")


# =====================================================
# CHART 1: TOP 10 MOST RENTED FILMS
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/mostrentedfilms.csv").head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df["Film_Title"], df["Total_Rentals"], color=BAR_COLOR)
ax.invert_yaxis()                         # top film at the top
ax.set_xlabel("Total Rentals")
ax.set_title("Top 10 Most Rented Films", fontsize=14, fontweight="bold")

# Put the number at the end of each bar
for i, v in enumerate(df["Total_Rentals"]):
    ax.text(v + 0.3, i, str(v), va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/01_most_rented_films.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 1: Most rented films")


# =====================================================
# CHART 2: TOP 10 HIGHEST REVENUE FILMS
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/highestrevcsv.csv").head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df["Film_Title"], df["Revenue"], color=SUCCESS_COLOR)
ax.invert_yaxis()
ax.set_xlabel("Revenue ($)")
ax.set_title("Top 10 Highest Revenue Films", fontsize=14, fontweight="bold")

for i, v in enumerate(df["Revenue"]):
    ax.text(v + 1, i, f"${v:.2f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/02_highest_revenue_films.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 2: Highest revenue films")


# =====================================================
# CHART 3: TOP 10 CUSTOMERS BY RENTAL COUNT
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/customorswithmostrent.csv").head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df["Full_Name"], df["Rental_Count"], color=BAR_COLOR)
ax.invert_yaxis()
ax.set_xlabel("Number of Rentals")
ax.set_title("Top 10 Customers by Rental Count", fontsize=14, fontweight="bold")

for i, v in enumerate(df["Rental_Count"]):
    ax.text(v + 0.3, i, str(v), va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/03_top_customers_by_rentals.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 3: Top customers by rentals")


# =====================================================
# CHART 4: TOP 10 CUSTOMERS BY SPENDING
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/customorshighestrev.csv").head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df["Full_Name"], df["Total_Spent"], color=SUCCESS_COLOR)
ax.invert_yaxis()
ax.set_xlabel("Total Spent ($)")
ax.set_title("Top 10 Customers by Total Spending", fontsize=14, fontweight="bold")

for i, v in enumerate(df["Total_Spent"]):
    ax.text(v + 1, i, f"${v:.2f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/04_top_customers_by_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 4: Top customers by spending")


# =====================================================
# CHART 5: RENTAL TRENDS OVER TIME (LINE CHART)
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/rentalbymont.csv")

# Build a proper "Month-Year" label
df["Period"] = df["Month_Name"] + " " + df["Year"].astype(str)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["Period"], df["Rentals"], marker="o", linewidth=2.5,
        markersize=10, color=ACCENT_COLOR)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Rentals")
ax.set_title("Rental Activity Over Time", fontsize=14, fontweight="bold")
ax.fill_between(range(len(df)), df["Rentals"], alpha=0.2, color=ACCENT_COLOR)

# Numeric label next to each point
for i, v in enumerate(df["Rentals"]):
    ax.text(i, v + 150, str(v), ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/05_rental_trends.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 5: Rental trends over time")


# =====================================================
# CHART 6: MONTHLY REVENUE (LINE CHART)
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/revbymonth.csv")
df["Period"] = df["Month_Name"] + " " + df["Year"].astype(str)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["Period"], df["Revenue"], marker="s", linewidth=2.5,
        markersize=10, color=SUCCESS_COLOR)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")
ax.set_title("Revenue Over Time", fontsize=14, fontweight="bold")
ax.fill_between(range(len(df)), df["Revenue"], alpha=0.2, color=SUCCESS_COLOR)

for i, v in enumerate(df["Revenue"]):
    ax.text(i, v + 600, f"${v:,.0f}", ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/06_revenue_trends.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 6: Revenue trends")


# =====================================================
# CHART 7: CATEGORY POPULARITY (DUAL METRIC)
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/famouscat.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Left: rentals per category
ax1.barh(df["Category"], df["Total_Rentals"], color=BAR_COLOR)
ax1.invert_yaxis()
ax1.set_xlabel("Total Rentals")
ax1.set_title("Rentals by Category", fontsize=13, fontweight="bold")

# Right: revenue per category
ax2.barh(df["Category"], df["Total_Revenue"], color=SUCCESS_COLOR)
ax2.invert_yaxis()
ax2.set_xlabel("Total Revenue ($)")
ax2.set_title("Revenue by Category", fontsize=13, fontweight="bold")

plt.suptitle("Film Category Performance", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/07_category_performance.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 7: Category performance")


# =====================================================
# CHART 8: STORE COMPARISON
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/storeperfor.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

# Stores labeled as "City (Store N)"
labels = [f"{row['City']} (Store {row['Store_ID']})" for _, row in df.iterrows()]
colors = [BAR_COLOR, ACCENT_COLOR]

ax1.bar(labels, df["Total_Rentals"], color=colors, width=0.5)
ax1.set_ylabel("Total Rentals")
ax1.set_title("Rentals by Store", fontsize=13, fontweight="bold")
for i, v in enumerate(df["Total_Rentals"]):
    ax1.text(i, v + 80, str(v), ha="center", fontweight="bold")

ax2.bar(labels, df["Total_Revenue"], color=colors, width=0.5)
ax2.set_ylabel("Total Revenue ($)")
ax2.set_title("Revenue by Store", fontsize=13, fontweight="bold")
for i, v in enumerate(df["Total_Revenue"]):
    ax2.text(i, v + 300, f"${v:,.0f}", ha="center", fontweight="bold")

plt.suptitle("Store Performance Comparison", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/08_store_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 8: Store comparison")


# =====================================================
# CHART 9: WEEKEND vs WEEKDAY (PIE CHART)
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/weekendvsweekday.csv")

fig, ax = plt.subplots(figsize=(8, 8))
colors = [BAR_COLOR, ACCENT_COLOR]
explode = (0, 0.08)              # pull the weekend slice out slightly

wedges, texts, autotexts = ax.pie(
    df["Rentals"],
    labels=df["Day_Type"],
    autopct=lambda p: f"{p:.1f}%\n({int(p * df['Rentals'].sum() / 100)} rentals)",
    colors=colors,
    explode=explode,
    startangle=90,
    textprops={"fontsize": 12, "fontweight": "bold"}
)

ax.set_title("Weekend vs Weekday Rentals", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/09_weekend_vs_weekday.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 9: Weekend vs weekday")


# =====================================================
# CHART 10: AVERAGE RENTAL DURATION BY CATEGORY
# =====================================================
df = pd.read_csv(f"{RESULTS_DIR}/avrgrentaldurationbycat.csv")
df = df.sort_values("Avg_Rental_Days", ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
# Highlight the longest-duration category in red
colors = [BAR_COLOR if x < df["Avg_Rental_Days"].max() else ACCENT_COLOR
          for x in df["Avg_Rental_Days"]]

ax.barh(df["Category"], df["Avg_Rental_Days"], color=colors)
ax.set_xlabel("Average Rental Duration (Days)")
ax.set_title("Average Rental Duration by Category", fontsize=14, fontweight="bold")

for i, v in enumerate(df["Avg_Rental_Days"]):
    ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/10_avg_duration_by_category.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Chart 10: Average duration by category")


# =====================================================
# DONE
# =====================================================
print(f"\nAll charts saved to '{CHARTS_DIR}/' folder")
print(f"Total charts generated: 10")
