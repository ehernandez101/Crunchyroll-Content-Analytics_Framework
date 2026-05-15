import pandas as pd 
import numpy as np

np.random.seed(42)

titles = [
    "Attack on Titan",
    "Jujutsu Kaisen",
    "Solo Leveling",
    "Demon Slayer",
    "One Piece",
    "Chainsaw Man",
    "Spy x Family"
]

genres = [
    "Action",
    "Fantasy",
    "Adventure",
    "Comedy"
]

regions = [
    "North America",
    "Europe",
    "Latin America",
    "Asia"
]

rows = 5000

df = pd.DataFrame({
    "user_id": range(1, rows + 1),
    "anime_title": np.random.choice(titles, rows),
    "genre": np.random.choice(genres, rows),
    "region": np.random.choice(regions, rows),
    "watch_minutes": np.random.normal(140, 40, rows).astype(int),
    "episodes_completed": np.random.randint(1, 24, rows),
    "days_inactive": np.random.randint(0, 60, rows),
    "subscription_months": np.random.randint(1, 48, rows),
    "ad_clicks": np.random.randint(0, 20, rows),
    "retained": np.random.choice([0,1], rows, p=[0.35,0.65])
})

df["churn_risk"] = np.where(
    (df["days_inactive"] > 30) &
    (df["watch_minutes"] < 100),
    "High",
    "Low"
)

df.to_csv("../data/crunchyroll_anime_dataset.csv", index=False)

print("Anime dataset created successfully.")
print(df.head())
