import requests
import time
import json
import os
import re
from datetime import datetime


# ------------------------------------------------------------------
# Step 1: Get the list of top story IDs
# ------------------------------------------------------------------

# Hacker News top stories URL
url = "https://hacker-news.firebaseio.com/v0/topstories.json"

# HackerNews asks us to identify our script with a User-Agent header
headers = {"User-Agent": "TrendPulse/1.0"}

# If this first request fails there is nothing to work with,
# so we print a message and stop instead of crashing with an error
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()   # turns 4xx / 5xx responses into errors
    story_ids = response.json()
except requests.exceptions.RequestException as e:
    print("Could not fetch story IDs:", e)
    exit()

print("Status code:", response.status_code)

# We only need the first 500 stories
story_ids = story_ids[:500]

# The top 500 didn't give enough sports/science matches, so also pull in
# the newest stories to widen the pool.
try:
    new_response = requests.get(
        "https://hacker-news.firebaseio.com/v0/newstories.json",
        headers=headers, timeout=10)
    new_response.raise_for_status()

    for new_id in new_response.json()[:500]:
        if new_id not in story_ids:      # avoid fetching the same story twice
            story_ids.append(new_id)
except requests.exceptions.RequestException as e:
    print("Could not fetch new stories:", e)

print("Number of stories:", len(story_ids))


# ------------------------------------------------------------------
# Categories and their keywords
# ------------------------------------------------------------------
keywords = {
    "technology": [
        "AI", "software", "tech", "code", "computer",
        "data", "cloud", "API", "GPU", "LLM"
    ],

    "worldnews": [
        "war", "government", "country", "president",
        "election", "climate", "attack", "global"
    ],

    "sports": [
        "NFL", "NBA", "FIFA", "sport", "game", "team",
        "player", "league", "championship"
    ],

    "science": [
        "research", "study", "space", "physics", "biology",
        "discovery", "NASA", "genome"
    ],

    "entertainment": [
        "movie", "film", "music", "Netflix", "game",
        "book", "show", "award", "streaming"
    ]
}


# ------------------------------------------------------------------
# Step 2: Get the details of each story
# ------------------------------------------------------------------
# We fetch every story ONCE here and sort them into categories later.
# This way the 2 second sleep can happen once per category,
# instead of once per story (which would take far too long).

# This list will contain all the story information
all_stories = []

for story_id in story_ids:

    story_url = "https://hacker-news.firebaseio.com/v0/item/" + str(story_id) + ".json"

    # If one story fails, print a message and move on to the next one
    try:
        story_response = requests.get(story_url, headers=headers, timeout=10)
        story_response.raise_for_status()
        story = story_response.json()
    except requests.exceptions.RequestException as e:
        print("Failed to fetch story", story_id, "-", e)
        continue

    # Make sure the response contains a title
    # (deleted stories come back as None or without a title)
    if story is not None and "title" in story:
        all_stories.append(story)

print("Stories collected:", len(all_stories))


# ------------------------------------------------------------------
# Step 3: Assign categories and keep the fields we need
# ------------------------------------------------------------------

# Store the final stories here
final_stories = []

# Remember which story IDs we already saved, so a story that matches
# two categories (e.g. "game" is in both sports and entertainment)
# is only saved once. A set makes this check fast.
used_ids = set()

# Keep track of how many stories we have in each category
category_count = {
    "technology": 0,
    "worldnews": 0,
    "sports": 0,
    "science": 0,
    "entertainment": 0
}

# Check each category
for category in keywords:

    print("Checking category:", category)

    for story in all_stories:

        # Stop when we have 25 stories in this category
        if category_count[category] >= 25:
            break

        # Skip stories that were already saved under another category
        if story["id"] in used_ids:
            continue

        title = story["title"]

        found = False

        # Check the keywords for this category
        for word in keywords[category]:

            if word == "AI":
                # "AI" is only 2 letters, so match it as a whole word;
                # otherwise it would match inside "said", "against", etc.
                if re.search(r"\bAI\b", title, re.IGNORECASE):
                    found = True
                    break
            else:
                # For every other keyword, a plain "contains" check is enough.
                # This also matches plurals like "sports" and "games".
                if word.lower() in title.lower():
                    found = True
                    break

        # Add the story if a keyword was found
        if found:

            new_story = {
                "post_id": story["id"],
                "title": story["title"],
                "category": category,
                # .get() gives a default value if HackerNews left the field out
                "score": story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author": story.get("by", "unknown"),
                "collected_at": datetime.now().isoformat()
            }

            final_stories.append(new_story)
            used_ids.add(story["id"])

            category_count[category] = category_count[category] + 1

    # Wait 2 seconds before checking the next category
    # (one sleep per category, not per story)
    time.sleep(2)


# ------------------------------------------------------------------
# Step 4: Save everything to a JSON file
# ------------------------------------------------------------------

# Create the data folder if it does not already exist
os.makedirs("data", exist_ok=True)

# Create today's date
today = datetime.now().strftime("%Y%m%d")

# Create the output file name
file_name = "data/trends_" + today + ".json"

# Save the stories as a JSON file
with open(file_name, "w", encoding="utf-8") as file:

    json.dump(final_stories, file, indent=4)


print()
print("Collected", len(final_stories), "stories. Saved to", file_name)

print()
print("Category totals:")

for category in category_count:
    print(category, ":", category_count[category])