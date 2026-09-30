import os

import matplotlib.pyplot as plt
import pandas as pd


# ------------------------------------------------------------------
# Step 1: Setup
# ------------------------------------------------------------------

# Load the analysed CSV that Task 3 created
df = pd.read_csv("data/trends_analysed.csv")
print("Loaded", len(df), "rows from data/trends_analysed.csv")

# Create the outputs/ folder if it does not exist yet
os.makedirs("outputs", exist_ok=True)


# ------------------------------------------------------------------
# Chart drawing functions
# ------------------------------------------------------------------
# Each function draws one chart on the axes (ax) it is given.
# This way the same code is used for the single charts AND for the
# dashboard, so we don't have to write everything twice.

def draw_top_stories(ax):
    """Chart 1: horizontal bar chart of the top 10 stories by score."""
    # nlargest picks the 10 rows with the highest score
    top10 = df.nlargest(10, "score").copy()

    # Shorten titles longer than 50 characters so they fit on the axis
    top10["short_title"] = top10["title"].apply(
        lambda t: t if len(t) <= 50 else t[:47] + "...")

    ax.barh(top10["short_title"], top10["score"], color="steelblue")

    # barh draws the first row at the bottom, so flip the axis to put
    # the highest-scoring story at the top
    ax.invert_yaxis()

    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story title")


def draw_categories(ax):
    """Chart 2: bar chart of how many stories each category has."""
    counts = df["category"].value_counts()

    # One colour per bar (5 categories -> 5 different colours)
    colours = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3"]

    ax.bar(counts.index, counts.values, color=colours[:len(counts)])

    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of stories")
    ax.tick_params(axis="x", rotation=30)


def draw_scatter(ax):
    """Chart 3: scatter plot of score vs number of comments."""
    # Split the data using the is_popular column (True / False)
    popular = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]

    # Two scatter calls with different colours; label= feeds the legend
    ax.scatter(not_popular["score"], not_popular["num_comments"],
               color="grey", alpha=0.7, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"],
               color="crimson", alpha=0.7, label="Popular")

    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Number of comments")
    ax.legend()


# ------------------------------------------------------------------
# Step 2: Chart 1 - Top 10 stories
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
draw_top_stories(ax)
fig.tight_layout()                                   # stops labels being cut off
fig.savefig("outputs/chart1_top_stories.png", dpi=150)   # save BEFORE any show()
plt.close(fig)
print("Saved outputs/chart1_top_stories.png")


# ------------------------------------------------------------------
# Step 3: Chart 2 - Stories per category
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
draw_categories(ax)
fig.tight_layout()
fig.savefig("outputs/chart2_categories.png", dpi=150)
plt.close(fig)
print("Saved outputs/chart2_categories.png")


# ------------------------------------------------------------------
# Step 4: Chart 3 - Score vs comments
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
draw_scatter(ax)
fig.tight_layout()
fig.savefig("outputs/chart3_scatter.png", dpi=150)
plt.close(fig)
print("Saved outputs/chart3_scatter.png")


# ------------------------------------------------------------------
# Bonus: Dashboard with all 3 charts in one figure
# ------------------------------------------------------------------
# 1 row x 3 columns; wide figure because chart 1 has long titles
fig, axes = plt.subplots(1, 3, figsize=(24, 7))

draw_top_stories(axes[0])
draw_categories(axes[1])
draw_scatter(axes[2])

fig.suptitle("TrendPulse Dashboard", fontsize=20, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])   # leave room for the overall title
fig.savefig("outputs/dashboard.png", dpi=150)
print("Saved outputs/dashboard.png")

# Show the dashboard on screen last (only after everything is saved).
# On a machine with no display this just does nothing harmful.
plt.show()
