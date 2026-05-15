import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

df = pd.read_csv("../data/crunchyroll_anime_dataset.csv")

# Convert churn risk into a binary target
df["high_churn_risk"] = df["churn_risk"].map({
    "Low": 0,
    "High": 1
})

features = [
    "watch_minutes",
    "episodes_completed",
    "days_inactive",
    "subscription_months",
    "ad_clicks"
]

X = df[features]
y = df["high_churn_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n=== CHURN PREDICTION MODEL ===\n")
print(f"Model Accuracy: {accuracy:.2%}")

print("\n=== CLASSIFICATION REPORT ===\n")
print(classification_report(y_test, predictions))

feature_importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\n=== FEATURE IMPORTANCE ===\n")
print(feature_importance)
