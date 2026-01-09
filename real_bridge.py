import serial
import time

# CONFIGURATION
SERIAL_PORT = "COM3"  # Change to your ESP32 port (e.g., /dev/ttyUSB0 on Linux/Mac)
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"--- LISTENING TO {SERIAL_PORT} ---")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

# Logic Variables
previous_temp = 0
phase = "STABLE"

while True:
    if ser.in_waiting > 0:
        try:
            # 1. Read raw line from ESP32 (e.g., "RAW_TEMP=30.5,RAW_BUBBLES=2")
            raw_line = ser.readline().decode('utf-8').strip()
            
            if "RAW_TEMP" in raw_line:
                # Parse the raw data
                parts = raw_line.split(",")
                data = {}
                for p in parts:
                    k, v = p.split("=")
                    data[k] = float(v)
                
                temp = data["RAW_TEMP"]
                bubbles = int(data["RAW_BUBBLES"])

                # 2. Apply SealGuard Logic (The "Brain")
                
                # Determine Phase
                if temp > previous_temp + 0.1:
                    phase = "HEATING"
                elif temp < previous_temp - 0.1:
                    phase = "COOLING"
                
                # Determine Status (The "Leak Logic")
                # Rule: If Cooling AND No Bubbles -> LEAK
                if phase == "COOLING" and bubbles == 0:
                    status = "LEAK DETECTED"
                elif phase == "COOLING" and bubbles > 0:
                    status = "HEALTHY BREATHING"
                else:
                    status = "MONITORING"

                previous_temp = temp

                # 3. Format for Streamlit
                output_line = f"TEMP={temp:.2f},PHASE={phase},BUBBLES={bubbles},STATUS={status}"
                print(output_line) # Show in terminal

                # 4. Save to shared file
                with open("esp_data.txt", "w") as f:
                    f.write(output_line)
                    
        except Exception as e:
            print(f"Error parsing line: {e}")
            
    time.sleep(0.1)