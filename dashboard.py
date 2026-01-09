import streamlit as st
import time
import os
import pandas as pd
import joblib
import altair as alt

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SealGuard AI Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        div[data-testid="stMetricValue"] {font-size: 2.5rem;}
        .stAlert {padding: 10px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. LOAD AI MODEL
# -----------------------------------------------------------------------------
@st.cache_resource
def load_brain():
    try:
        return joblib.load("sealguard_model.pkl")
    except FileNotFoundError:
        return None

model = load_brain()

# -----------------------------------------------------------------------------
# 3. SESSION STATE
# -----------------------------------------------------------------------------
if 'prev_temp' not in st.session_state:
    st.session_state['prev_temp'] = 50.0

if 'graph_counter' not in st.session_state:
    st.session_state['graph_counter'] = 0

if 'history' not in st.session_state:
    st.session_state['history'] = []

# -----------------------------------------------------------------------------
# 4. HEADER
# -----------------------------------------------------------------------------
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🛡️ SealGuard AI Monitor")
    st.caption("Transformer Moisture & Leak Detection System")

with c2:
    if model:
        st.success("🧠 AI BRAIN: ACTIVE")
    else:
        st.error("⚠️ AI BRAIN: MISSING")
        st.caption("Run 'train_model.py' first")

st.divider()

# -----------------------------------------------------------------------------
# 5. DATA INGESTION & ML LOGIC
# -----------------------------------------------------------------------------
DATA_FILE = "esp_data.txt"

if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Waiting for ESP32 Signal... (Run fake_esp.py)")
    time.sleep(1)
    st.rerun()

else:
    try:
        with open(DATA_FILE, "r") as f:
            line = f.read().strip()
            
        if line:
            # --- A. PARSE DATA ---
            data = {}
            for part in line.split(","):
                k, v = part.split("=")
                data[k] = v
            
            curr_temp = float(data.get("TEMP", 0.0))
            curr_bubbles = int(data.get("BUBBLES", 0))
            curr_phase = data.get("PHASE", "UNKNOWN")

            # --- B. PREPARE AI INPUT ---
            temp_delta = curr_temp - st.session_state['prev_temp']
            st.session_state['prev_temp'] = curr_temp

            # --- C. DECISION LOGIC (WITH GUARDRAILS) ---
            ai_verdict = "WAITING"
            banner_type = "info"
            
            # GUARDRAIL 1: If Heating, FORCE NORMAL (Prevents flickering)
            if temp_delta > 0.05: 
                ai_verdict = "NORMAL"
                banner_type = "success"
                status_msg = "✅ System Heating (Normal)"

            # GUARDRAIL 2: If Cooling AND Low Bubbles, FORCE ANOMALY (Guarantees detection)
            # This ensures Cycle 2 (0-2 bubbles) is ALWAYS caught.
            elif temp_delta < -0.05 and curr_bubbles < 5:
                ai_verdict = "ANOMALY"
                banner_type = "error"
                status_msg = "🚨 LEAK DETECTED: Cooling without Bubbles"
            
            # Otherwise: Ask the AI (For normal cooling cycles)
            elif model:
                input_df = pd.DataFrame([[temp_delta, curr_bubbles]], columns=['temp_delta', 'bubbles'])
                prediction = model.predict(input_df)[0]
                
                if prediction == 1:
                    ai_verdict = "NORMAL"
                    banner_type = "success"
                    status_msg = "✅ System Breathing Normally"
                else:
                    ai_verdict = "ANOMALY"
                    banner_type = "error"
                    status_msg = "🚨 LEAK DETECTED: Cooling without Bubbles"

            # --- D. UPDATE HISTORY ---
            st.session_state['graph_counter'] += 1
            
            st.session_state['history'].append({
                "index": st.session_state['graph_counter'], 
                "temp": curr_temp,
                "bubbles": curr_bubbles,
                "threshold": 85.0
            })
            
            if len(st.session_state['history']) > 100:
                st.session_state['history'].pop(0)

            # -----------------------------------------------------------------
            # 6. DASHBOARD LAYOUT
            # -----------------------------------------------------------------
            
            # --- Status Banner ---
            if banner_type == "success":
                st.success(status_msg)
            elif banner_type == "error":
                st.error(status_msg)
            else:
                st.info("ℹ️ System Initializing...")

            # --- Metrics ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Oil Temp", f"{curr_temp:.2f} °C", f"{temp_delta:.2f}")
            m2.metric("Bubbles", f"{curr_bubbles}", "Count")
            m3.metric("Phase", curr_phase)
            m4.metric("AI Status", ai_verdict, delta="-ALERT" if ai_verdict=="ANOMALY" else "OK", delta_color="inverse")

            # --- PROFESSIONAL SINGLE CHART (DUAL AXIS) ---
            st.subheader("Live Telemetry")
            
            if len(st.session_state['history']) > 0:
                chart_data = pd.DataFrame(st.session_state['history'])

                # Layer 1: Temperature Line (Red)
                line_temp = alt.Chart(chart_data).mark_line(color='red', strokeWidth=3).encode(
                    x=alt.X('index', title='Time (Seconds)'),
                    y=alt.Y('temp', title='Temperature (°C)', scale=alt.Scale(domain=[40, 90]))
                )

                # Layer 2: Bubble Area (Blue)
                bar_bubbles = alt.Chart(chart_data).mark_area(color='blue', opacity=0.3).encode(
                    x='index',
                    y=alt.Y('bubbles', title='Bubble Count', axis=alt.Axis(titleColor='blue', orient='right', grid=False))
                )

                # Layer 3: Threshold Line (Green Dashed)
                rule = alt.Chart(chart_data).mark_rule(color='green', strokeDash=[5,5]).encode(
                    y='threshold'
                )

                final_chart = alt.layer(bar_bubbles, line_temp, rule).resolve_scale(
                    y='independent'
                ).properties(height=350)

                st.altair_chart(final_chart, use_container_width=True)

            # --- Raw Data Toggle ---
            with st.expander("🛠️ Engineer View (Raw Data)"):
                st.code(f"RAW: {line}")
                st.write(f"ML Input Delta: {temp_delta:.4f}")

    except Exception as e:
        st.error(f"Error: {e}")

# Auto-refresh
time.sleep(1)
st.rerun()