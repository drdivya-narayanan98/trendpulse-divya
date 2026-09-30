import numpy as np
import pandas as pd

# Step 1: Load and explore the data
df = pd.read_csv("data/trends_clean.csv")

print("Loaded data:", df.shape)
print()
print("First 5 rows:")
print(df.head())

avg_score = df["score"].mean()
avg_comments = df["num_comments"].mean()

print()
print("Average score   :", round(avg_score))
print("Average comments:", round(avg_comments))

# Step 2: Basic analysis with NumPy
scores = df["score"].to_numpy()
comments = df["num_comments"].to_numpy()

print()
print("--- NumPy Stats ---")
print("Mean score   :", round(np.mean(scores)))
print("Median score :", round(np.median(scores)))
print("Std deviation:", round(np.std(scores)))
print("Max score    :", np.max(scores))
print("Min score    :", np.min(scores))

# Category with the most stories (value_counts sorts biggest first)
category_counts = df["category"].value_counts()
top_category = category_counts.index[0]
top_count = category_counts.iloc[0]

print()
print("Most stories in:", top_category, "(" + str(top_count), "stories)")

# np.argmax gives the row position of the biggest comment count
most_commented = df.iloc[np.argmax(comments)]

print()
print('Most commented story: "' + most_commented["title"] + '" -',
      most_commented["num_comments"], "comments")

# Step 3: Add new columns
# comments per upvote (+1 avoids dividing by zero)
df["engagement"] = df["num_comments"] / (df["score"] + 1)

# True if the story's score is above the overall average
df["is_popular"] = df["score"] > avg_score

# Step 4: Save the result
output_file = "data/trends_analysed.csv"
df.to_csv(output_file, index=False)

print()
print("Saved to", output_file)
