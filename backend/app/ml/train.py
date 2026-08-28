import os
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

from app.ml.training_data import TRAINING_DATA

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "hs_classifier.joblib"


def train():
    print("🚀 Starting HS Code Classifier training...")
    print(f"   Training samples: {len(TRAINING_DATA)}")

    # Separate descriptions and labels
    descriptions = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    unique_codes = list(set(labels))
    print(f"   HS codes to classify: {len(unique_codes)}")
    print(f"   Codes: {sorted(unique_codes)}")

    # Build pipeline: TF-IDF vectoriser + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),     # unigrams and bigrams
            max_features=5000,
            sublinear_tf=True,      # apply log normalization
            min_df=1,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            multi_class="multinomial",
        )),
    ])

    # Cross-validation to measure real accuracy
    print("\n📊 Running 5-fold cross-validation...")
    scores = cross_val_score(pipeline, descriptions, labels, cv=5, scoring="accuracy")
    print(f"   Accuracy scores: {[f'{s:.2%}' for s in scores]}")
    print(f"   Mean accuracy:   {scores.mean():.2%} (+/- {scores.std():.2%})")

    # Train on full dataset
    print("\n🏋️  Training on full dataset...")
    pipeline.fit(descriptions, labels)

    # Save model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_data = {
        "pipeline": pipeline,
        "hs_codes": sorted(unique_codes),
        "version": "1.0.0",
        "training_samples": len(TRAINING_DATA),
    }
    joblib.dump(model_data, MODEL_PATH)
    print(f"\n✅ Model saved to {MODEL_PATH}")
    print(f"   File size: {MODEL_PATH.stat().st_size / 1024:.1f} KB")

    # Quick sanity test
    print("\n🧪 Sanity check predictions:")
    test_cases = [
        "cotton t-shirt for men",
        "laptop computer portable",
        "android smartphone 5g",
        "vitamin tablet medicine",
        "gold necklace jewellery",
    ]
    for desc in test_cases:
        proba = pipeline.predict_proba([desc])[0]
        classes = pipeline.classes_
        top_idx = np.argmax(proba)
        print(f"   '{desc}' → {classes[top_idx]} ({proba[top_idx]:.1%})")


if __name__ == "__main__":
    train()