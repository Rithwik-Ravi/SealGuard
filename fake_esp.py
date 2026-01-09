import time
import random
import sys

# CONFIGURATION
MIN_TEMP = 45.0
MAX_TEMP = 85.0

# HARDWARE SPEED
HEATING_RATE = 0.3
COOLING_RATE = 0.2

# STATE VARIABLES
current_temp = 50.0
direction = 1       # 1 = Heating, -1 = Cooling
cycle_count = 1     # We start at cycle 1

print("--- FAKE ESP32 STARTED ---")
print("Cycle 1: Healthy (High Bubbles 10-15)")
print("Cycle 2+: LEAK (Low Bubbles 0-2)")
print("----------------------------------------------------")

while True:
    noise = random.uniform(-0.02, 0.02)
    
    if direction == 1:
        current_temp += HEATING_RATE + noise
        phase = "HEATING"
    else:
        current_temp -= COOLING_RATE + noise
        phase = "COOLING"

    if current_temp >= MAX_TEMP:
        direction = -1
    elif current_temp <= MIN_TEMP:
        direction = 1
        cycle_count += 1 

    bubbles = 0
    status = "HEALTHY"

    if phase == "HEATING":
        bubbles = 0
        status = "HEALTHY"
        
    elif phase == "COOLING":
        # FIX: Changed <= 2 to < 2.
        # Cycle 1 is Healthy.
        # Cycle 2 is now the LEAK.
        if cycle_count < 2:
            bubbles = random.randint(10, 15)
            status = "HEALTHY"
        else:
            bubbles = random.randint(0, 2)
            status = "LEAK"

    line = f"TEMP={current_temp:.2f},PHASE={phase},BUBBLES={bubbles},STATUS={status}"
    print(line)
    
    with open("esp_data.txt", "w") as f:
        f.write(line)

    time.sleep(0.5)