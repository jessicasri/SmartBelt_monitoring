import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
from datetime import datetime
import os


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Belt Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #0b1220;
        color: white;
    }

    /* Remove some default spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Main title */
    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 20px;
    }

    /* Cards */
    .card {
        background-color: #111827;
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Status */
    .system-status {
        background-color: #12351f;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: #4ade80;
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 20px;
    }

    /* Metric boxes */
    .metric-box {
        background-color: #111827;
        border: 1px solid #263244;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    .metric-title {
        color: #9ca3af;
        font-size: 14px;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Risk */
    .risk-low {
        background-color: #12351f;
        color: #4ade80;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
    }

    .risk-medium {
        background-color: #3b2f0b;
        color: #facc15;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
    }

    .risk-high {
        background-color: #3b1515;
        color: #f87171;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
    }

    /* Alert */
    .alert-box {
        background-color: #321619;
        border: 1px solid #7f1d1d;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }

    .normal-box {
        background-color: #12351f;
        border-radius: 10px;
        padding: 14px;
        color: #4ade80;
    }

    /* Small text */
    .small-text {
        color: #9ca3af;
        font-size: 13px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD MODEL
# =========================================================

MODEL_PATH = "best.pt"

if not os.path.exists(MODEL_PATH):
    st.error("❌ best.pt model file not found.")
    st.stop()

model = YOLO(MODEL_PATH)


# =========================================================
# SESSION HISTORY
# =========================================================

if "inspection_history" not in st.session_state:
    st.session_state.inspection_history = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Monitoring Controls")

    vibration = st.number_input(
        "📳 Vibration (mm/s)",
        min_value=0.0,
        max_value=20.0,
        value=5.2,
        step=0.1
    )

    temperature = st.number_input(
        "🌡️ Temperature (°C)",
        min_value=0.0,
        max_value=150.0,
        value=40.0,
        step=0.5
    )

    st.markdown("---")

    st.markdown(
        '<div class="small-text">'
        'Monitoring thresholds are used internally for prototype risk assessment.'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

header_col1, header_col2 = st.columns([5, 1])

with header_col1:

    st.markdown(
        '<div class="main-title">🏭 SMART BELT MONITORING SYSTEM</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Intelligent monitoring of conveyor belt damage'
        '</div>',
        unsafe_allow_html=True
    )

with header_col2:

    st.markdown(
        '<div style="text-align:right; color:#4ade80; '
        'font-weight:600; margin-top:15px;">'
        '🟢 SYSTEM ONLINE'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# SYSTEM STATUS
# =========================================================

st.markdown(
    '<div class="system-status">'
    '🟢 SYSTEM STATUS: MONITORING'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# IMAGE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📷 Upload Conveyor Belt Image",
    type=["jpg", "jpeg", "png"]
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

analyze = st.button(
    "🔍 ANALYZE BELT",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze:

    if uploaded_file is None:

        st.warning("Please upload a conveyor belt image first.")

    else:

        # -----------------------------------------------
        # Read image
        # -----------------------------------------------

        image = Image.open(uploaded_file).convert("RGB")
        image_array = np.array(image)

        # -----------------------------------------------
        # YOLO prediction
        # -----------------------------------------------

        results = model.predict(
            source=image_array,
            conf=0.25,
            imgsz=640,
            verbose=False
        )

        result = results[0]

        # -----------------------------------------------
        # Count classes
        # -----------------------------------------------

        crack_count = 0
        tear_count = 0

        max_confidence = 0.0

        if result.boxes is not None and len(result.boxes) > 0:

            classes = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()

            for cls, conf in zip(classes, confidences):

                max_confidence = max(
                    max_confidence,
                    float(conf)
                )

                if int(cls) == 0:
                    crack_count += 1

                elif int(cls) == 1:
                    tear_count += 1

        # -----------------------------------------------
        # Risk score
        # -----------------------------------------------

        risk_score = 0

        # Visual damage
        if crack_count > 0:
            risk_score += 35

        if tear_count > 0:
            risk_score += 35

        # Vibration
        if vibration > 7:
            risk_score += 20

        elif vibration > 5:
            risk_score += 10

        # Temperature
        if temperature > 70:
            risk_score += 20

        elif temperature > 60:
            risk_score += 10

        risk_score = min(risk_score, 100)

        # -----------------------------------------------
        # Risk level
        # -----------------------------------------------

        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # -----------------------------------------------
        # Recommendation
        # -----------------------------------------------

        if risk_level == "HIGH":

            recommendation = (
                "Stop or isolate the affected belt section "
                "and perform immediate inspection."
            )

        elif risk_level == "MEDIUM":

            recommendation = (
                "Schedule inspection and continue close monitoring."
            )

        else:

            recommendation = (
                "Continue normal monitoring."
            )

        # -----------------------------------------------
        # Save inspection
        # -----------------------------------------------

        timestamp = datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )

        inspection = {
            "Time": timestamp,
            "Crack": crack_count,
            "Tear": tear_count,
            "Vibration": vibration,
            "Temperature": temperature,
            "Risk Score": risk_score,
            "Status": risk_level
        }

        st.session_state.inspection_history.append(
            inspection
        )

        # =================================================
        # MAIN DASHBOARD
        # =================================================

        st.divider()

        # -----------------------------------------------
        # SNAPSHOT + STATUS
        # -----------------------------------------------

        col1, col2 = st.columns([1.5, 1])

        # ===============================================
        # CURRENT SNAPSHOT
        # ===============================================

        with col1:

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            st.subheader("📷 CURRENT BELT SNAPSHOT")

            annotated_image = result.plot()

            # YOLO plot returns BGR
            annotated_image = annotated_image[:, :, ::-1]

            st.image(
                annotated_image,
                use_container_width=True
            )

            st.markdown(
                f'<div class="small-text">'
                f'Inspection captured: {timestamp}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # ===============================================
        # CURRENT STATUS
        # ===============================================

        with col2:

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            st.subheader("📊 CURRENT STATUS")

            # Vibration
            st.metric(
                "📳 Vibration",
                f"{vibration:.1f} mm/s"
            )

            # Temperature
            st.metric(
                "🌡️ Temperature",
                f"{temperature:.1f} °C"
            )

            # Crack
            if crack_count > 0:

                st.error(
                    f"🔴 Crack: DETECTED ({crack_count})"
                )

            else:

                st.success(
                    "🟢 Crack: NOT DETECTED"
                )

            # Tear
            if tear_count > 0:

                st.error(
                    f"🔴 Tear: DETECTED ({tear_count})"
                )

            else:

                st.success(
                    "🟢 Tear: NOT DETECTED"
                )

            # Confidence
            if max_confidence > 0:

                st.write(
                    f"**AI Confidence:** "
                    f"{max_confidence * 100:.1f}%"
                )

            # Risk score
            st.metric(
                "⚠️ Risk Score",
                f"{risk_score}%"
            )

            if risk_level == "LOW":

                st.markdown(
                    '<div class="risk-low">'
                    '🟢 LOW RISK'
                    '</div>',
                    unsafe_allow_html=True
                )

            elif risk_level == "MEDIUM":

                st.markdown(
                    '<div class="risk-medium">'
                    '🟡 MEDIUM RISK'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<div class="risk-high">'
                    '🔴 HIGH RISK'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)


        # =================================================
        # RECOMMENDATION
        # =================================================

        st.markdown("### 🔧 RECOMMENDATION")

        if risk_level == "HIGH":

            st.error(recommendation)

        elif risk_level == "MEDIUM":

            st.warning(recommendation)

        else:

            st.success(recommendation)


        # =================================================
        # ALERTS
        # =================================================

        st.divider()

        alert_col1, alert_col2 = st.columns([1, 1])

        with alert_col1:

            st.subheader("🔔 ALERTS & NOTIFICATIONS")

            if risk_level == "HIGH":

                st.markdown(
                    '<div class="alert-box">'
                    '<b>🚨 BELT DAMAGE ALERT</b><br>'
                    f'High-risk condition detected at {timestamp}.'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.warning(
                    "📱 Phone notification triggered "
                    "(prototype simulation)."
                )

            elif risk_level == "MEDIUM":

                st.markdown(
                    '<div class="alert-box">'
                    '<b>⚠️ MONITORING ALERT</b><br>'
                    'Moderate belt risk detected.'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<div class="normal-box">'
                    '✅ No active belt damage alert.'
                    '</div>',
                    unsafe_allow_html=True
                )

        # ===============================================
        # PHONE NOTIFICATION
        # ===============================================

        with alert_col2:

            st.subheader("📱 PHONE NOTIFICATION")

            if risk_level == "HIGH":

                st.markdown(
                    '<div class="card">'
                    '<h4>🚨 Belt Damage Alert</h4>'
                    '<p>High-risk belt condition detected.</p>'
                    f'<p class="small-text">{timestamp}</p>'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<div class="card">'
                    '<h4>📱 Monitoring Active</h4>'
                    '<p>No critical alert currently active.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )


# =========================================================
# INSPECTION HISTORY
# =========================================================

st.divider()

st.subheader("📋 INSPECTION LOG")

if len(st.session_state.inspection_history) == 0:

    st.info(
        "No inspections recorded yet. "
        "Upload an image and click ANALYZE BELT."
    )

else:

    history_df = pd.DataFrame(
        st.session_state.inspection_history
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# DAMAGE TREND
# =========================================================

st.subheader("📈 DAMAGE & RISK TREND")

if len(st.session_state.inspection_history) >= 2:

    chart_df = pd.DataFrame(
        st.session_state.inspection_history
    )

    chart_df = chart_df[
        [
            "Time",
            "Crack",
            "Tear",
            "Risk Score"
        ]
    ]

    chart_df = chart_df.set_index("Time")

    st.line_chart(
        chart_df,
        use_container_width=True
    )

else:

    st.info(
        "Run at least two inspections to display the trend."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    '<div style="text-align:center; color:#6b7280;">'
    'Smart Belt Monitoring System | '
    'AI visual inspection + vibration + temperature monitoring'
    '</div>',
    unsafe_allow_html=True
)
