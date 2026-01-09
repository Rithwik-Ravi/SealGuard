import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

print("🧠 Training SealGuard AI Model...")

# 1. Load the Healthy Data
try:
    df = pd.read_csv("transformer_healthy_data.csv")
    print(f"   - Loaded {len(df)} rows of training data.")
except FileNotFoundError:
    print("❌ Error: 'transformer_healthy_data.csv' not found. Run generate_data.py first.")
    exit()

# 2. Select Features
features = ['temp_delta', 'bubbles']
X = df[features]

# 3. Initialize the Brain (Isolation Forest)
# FIX 1: n_estimators=200 (More trees = Smoother decision boundaries)
# FIX 2: contamination=0.001 (0.1%) -> We tell the AI our training data is pure.
#        The old 0.01 (1%) was forcing it to flag healthy heating data as errors.
model = IsolationForest(n_estimators=200, contamination=0.001, random_state=42)

# 4. Train (Fit) the Model
model.fit(X)
print("   - Model has learned the pattern of 'Normal Breathing'.")

# 5. Save the Model
filename = "sealguard_model.pkl"
joblib.dump(model, filename)
print(f"✅ Success! Trained model saved as '{filename}'")