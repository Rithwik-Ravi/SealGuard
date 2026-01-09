import pandas as pd
import random

# --- GOLDEN CONFIGURATION ---
STEPS = 50000 
MIN_TEMP = 45.0
MAX_TEMP = 85.0

# SYNC FIX: Dashboard reads 1s, ESP updates 0.5s.
# We double the rates here so the AI expects the larger jump.
HEATING_RATE = 0.6
COOLING_RATE = 0.4

data = []
current_temp = 50.0
direction = 1 

print(f"⚡ Generating SYNCED training data (Constant High Bubbles)...")

for i in range(STEPS):
    prev_temp = current_temp
    # Slightly wider noise to handle dashboard timing jitter
    noise = random.uniform(-0.05, 0.05)
    
    # 1. Simulate Temp Change
    if direction == 1:
        current_temp += HEATING_RATE + noise
        phase = "HEATING"
    else:
        current_temp -= COOLING_RATE + noise
        phase = "COOLING"

    # 2. Switch Direction
    if current_temp >= MAX_TEMP: direction = -1
    elif current_temp <= MIN_TEMP: direction = 1

    # 3. Calculate Delta
    temp_delta = current_temp - prev_temp

    # 4. Bubble Logic (CONSTANT HIGH BASELINE)
    bubbles = 0
    if phase == "COOLING":
        # Consistent high bubbles. No gradual math.
        # This teaches AI: "Cooling MUST have 10-15 bubbles."
        bubbles = random.randint(10, 15)
    
    data.append({"temp_delta": temp_delta, "bubbles": bubbles})

# 5. Save
df = pd.DataFrame(data)
df.to_csv("transformer_healthy_data.csv", index=False)
print(f"✅ Data Generated. Run 'train_model.py' to Sync.")