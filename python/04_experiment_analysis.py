import pandas as pd 
import numpy as np

np.random.seed(42)

df = pd.read_csv("../data/crunchyroll_anime_dataset.csv")

# Simulate A/B test groups for homepage thumbnail / recommendation rail
df["experiment_group"] = np.random.choice(
    ["Control", "Variant"],
    size=len(df),
    p=[0.50, 0.50]
)

# Simulate conversion behavior
df["clicked_title"] = np.where(
    df["experiment_group"] == "Variant",
    np.random.choice([0, 1], size=len(df), p=[0.28, 0.72]),
    np.random.choice([0, 1], size=len(df), p=[0.36, 0.64])
)

df["started_watching"] = np.where(
    df["clicked_title"] == 1,
    np.random.choice([0, 1], size=len(df), p=[0.25, 0.75]),
    0
)

df["completed_episode"] = np.where(
    df["started_watching"] == 1,
    np.random.choice([0, 1], size=len(df), p=[0.30, 0.70]),
    0
)

# KPI results
results = (
    df.groupby("experiment_group")[["clicked_title", "started_watching", "completed_episode"]]
    .mean()
    .mul(100)
    .round(2)
)

print("\n=== A/B TEST RESULTS ===\n")
print(results)

control_click = results.loc["Control", "clicked_title"]
variant_click = results.loc["Variant", "clicked_title"]

lift = ((variant_click - control_click) / control_click) * 100

print("\n=== EXPERIMENT LIFT ===\n")
print(f"Click Conversion Lift: {lift:.2f}%")

df.to_csv("../data/crunchyroll_experiment_dataset.csv", index=False)

print("\nExperiment dataset created successfully.")
