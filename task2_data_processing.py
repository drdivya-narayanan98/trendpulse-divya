import glob
import os

import pandas as pd


# ------------------------------------------------------------------
# Step 1: Load the JSON file from Task 1 into a DataFrame
# ------------------------------------------------------------------

# The Task 1 file name contains the date (trends_YYYYMMDD.json), so instead
# of hard-coding it we look for every matching file in data/ and pick the
# newest one. Because the date is in YYYYMMDD format, sorting the names
# alphabetically also sorts them by date.
json_files = sorted(glob.glob("data/trends_*.json"))

if not json_files:
    print("No JSON file found in data/. Please run task1_data_collection.py first.")
    exit()

json_file = json_files[-1]   # the latest one

df = pd.read_json(json_file)

print("Loaded", len(df), "stories from", json_file)
print()


# ------------------------------------------------------------------
# Step 2: Clean the data
# ------------------------------------------------------------------

# --- 1. Duplicates: the same story should only appear once ---
# Two rows with the same post_id are the same story, so keep the first one.
df = df.drop_duplicates(subset="post_id")
print("After removing duplicates:", len(df))

# --- 2. Missing values: drop rows missing post_id, title or score ---
# Empty or whitespace-only titles are also useless, so turn them into
# missing values first (None) so that dropna() catches them too.
df["title"] = df["title"].replace(r"^\s*$", None, regex=True)
df = df.dropna(subset=["post_id", "title", "score"])
print("After removing nulls:", len(df))

# --- 3. Data types: score and num_comments must be integers ---
# num_comments may be missing in some rows, so we treat a missing value as
# 0 comments. pd.to_numeric turns anything that is not a number into NaN
# and fillna(0) replaces it, after which astype(int) works safely.
df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0).astype(int)

# --- 4. Low quality: remove stories with a score below 5 ---
df = df[df["score"] >= 5]
print("After removing low scores:", len(df))

# --- 5. Whitespace: remove extra spaces at the start and end of titles ---
df["title"] = df["title"].str.strip()

print()
print("Rows remaining after cleaning:", len(df))


# ------------------------------------------------------------------
# Step 3: Save the cleaned data as a CSV file
# ------------------------------------------------------------------

os.makedirs("data", exist_ok=True)   # make sure the data/ folder exists

csv_file = "data/trends_clean.csv"

# index=False stops pandas from writing the row numbers as an extra column
df.to_csv(csv_file, index=False)

print()
print("Saved", len(df), "rows to", csv_file)


# ------------------------------------------------------------------
# Quick summary: how many stories per category
# ------------------------------------------------------------------
print()
print("Stories per category:")

category_counts = df["category"].value_counts()

for category, count in category_counts.items():
    print(" ", category.ljust(15), count)

