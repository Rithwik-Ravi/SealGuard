import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
try:
    df = pd.read_csv("transformer_healthy_data.csv")
    print(f"Loaded {len(df)} rows.")
except FileNotFoundError:
    print("❌ Error: CSV not found. Run generate_data.py first.")
    exit()

# 2. Slice Data (First 2 Days = 2880 minutes)
# We limit the view so the "Wave" pattern is clearly visible.
subset = df.head(2880)

# 3. Setup Plot
fig, ax1 = plt.subplots(figsize=(12, 6))

plt.title("Transformer Breathing Pattern (Normal Behavior)", fontsize=16)
plt.grid(True, linestyle='--', alpha=0.5)

# --- AXIS 1: TEMPERATURE (RED LINE) ---
color_temp = 'tab:red'
ax1.set_xlabel('Time (Minutes)')
ax1.set_ylabel('Temperature (°C)', color=color_temp, fontsize=12)
ax1.plot(subset.index, subset['temp_abs'], color=color_temp, linewidth=2, label='Temperature')
ax1.tick_params(axis='y', labelcolor=color_temp)

# --- AXIS 2: BUBBLES (BLUE BARS) ---
# We create a twin axis sharing the same x-axis
ax2 = ax1.twinx()
color_bubbles = 'tab:blue'
ax2.set_ylabel('Bubble Count', color=color_bubbles, fontsize=12)
# alpha=0.3 makes the bars transparent so they don't hide the red line
ax2.bar(subset.index, subset['bubbles'], color=color_bubbles, alpha=0.3, width=1.0, label='Bubbles')
ax2.tick_params(axis='y', labelcolor=color_bubbles)

# Set limit for bubbles to make the bars look nice (not taking up whole screen)
ax2.set_ylim(0, 30) 

# Show the plot
fig.tight_layout()
print("✅ Opening visualization window...")
plt.show()