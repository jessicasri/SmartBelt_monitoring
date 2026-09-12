import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
from datetime import datetime
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Belt Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #08101f;
        color: white;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid #1f2b3d;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    /* Header */
    .top-header {
        background: linear-gradient(90deg, #0c1527, #111d32);
        padding: 18px 28px;
        border-radius: 10px;
        border: 1px solid #1d2a3d;
        margin-bottom: 20px;
    }

    .title {
        font-size: 28px;
        font-weight: 700;
        color: white;
    }

    .subtitle {
        color: #9ba9bd;
        font-size: 15px;
        margin-top: 3px;
    }

    .online {
        color: #27d17f;
        font-weight: 600;
    }

    /* Cards */
    .card {
        background: #101a2b;
        border: 1px solid #20304a;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .card-title {
        font-size: 18px;
        font-weight: 650;
        color: #dbe7f7;
        margin-bottom: 14px;
    }

    /* Status */
    .status-normal {
        color: #48e58c;
        font-size: 27px;
        font-weight: 700;
    }

    .status-alert {
        color: #ff5555;
        font-size: 27px;
        font-weight: 700;
    }

    /* Metric boxes */
    .metric-box {
        background: #0c1627;
        border: 1px solid #273752;
        border-radius: 10px;
        padding: 14px;
        min-height: 85px;
    }

    .metric-title {
        color: #9ba9bd;
        font-size: 13px;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Alert */
    .alert-box {
        background: #281923;
        border: 1px solid #663142;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }

    .alert-title {
        color: #ff6464;
        font-weight: 700;
    }

    .alert-time {
        color: #8f9aac;
        font-size: 12px;
        margin-top: 4px;
    }

    /* Normal box */
    .normal-box {
        background: #10251d;
        border: 1px solid #1c6945;
        border-radius: 10px;
        padding: 15px;
    }

    /* Phone */
    .phone-box {
        background: #091323;
        border: 1px solid #243550;
        border-radius: 12px;
        padding: 18px;
        min-height: 260px;
    }

    .phone-alert {
        background: #202b40;
        border-radius: 10px;
        padding: 14px;
        margin-top: 20px;
    }

    /* Section headings */
    .section-heading {
        font-size: 22px;
        font-weight: 700;
        color: white;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    /* Inspection table */
    .inspection-row {
        background: #101a2b;
        border-bottom: 1px solid #25334a;
        padding: 10px;
    }

    /* Small text */
    .small-text {
        color: #91a0b5;
        font-size: 13px;
    }

    /* Hide Streamlit footer */
    footer {
        visibility: hidden;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 7px;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():
    return YOLO("best.pt")


try:
    model = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.error("Unable to load best.pt")
    st.code(str(e))


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None


# ============================================================
# TELEGRAM ALERT FUNCTION
# ============================================================

def send_telegram_alert(
    damage,
    confidence,
    vibration,
    temperature,
    risk_score
):

    try:

        bot_token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

        message = f"""
🚨 SMART BELT ALERT

Conveyor belt damage detected.

Damage: {damage}
AI Confidence: {confidence:.1f}%
Vibration: {vibration:.1f} mm/s
Temperature: {temperature:.1f} °C
Risk Score: {risk_score}%

⚠️ Immediate inspection recommended.
"""

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message
            },
            timeout=10
        )

        return response.ok

    except Exception:
        return False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Monitoring Controls")

    st.markdown("### 📳 Vibration (mm/s)")

    vibration = st.number_input(
        "Vibration",
        min_value=0.0,
        max_value=20.0,
        value=5.20,
        step=0.10,
        label_visibility="collapsed"
    )

    st.markdown("### 🌡️ Temperature (°C)")

    temperature = st.number_input(
        "Temperature",
        min_value=0.0,
        max_value=150.0,
        value=40.0,
        step=0.5,
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        """
        <div class="small-text">
        Monitoring thresholds are used internally for
        prototype risk assessment.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🏭 Smart Belt Monitoring System")
    st.caption("v2.0")


# ============================================================
# TOP HEADER
# ============================================================

current_time = datetime.now().strftime("%b %d, %Y %I:%M %p")

st.markdown(
    f"""
    <div class="top-header">

        <div style="display:flex; justify-content:space-between; align-items:center;">

            <div>
                <div class="title">
                    🏭 SMART BELT MONITORING SYSTEM
                </div>

                <div class="subtitle">
                    Intelligent monitoring of conveyor belt damage
                </div>
            </div>

            <div style="text-align:right;">
                <div class="online">
                    🟢 System Online
                </div>

                <div class="small-text">
                    {current_time}
                </div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN LAYOUT
# ============================================================

left, middle, right = st.columns([5.2, 3.0, 2.2], gap="medium")


# ============================================================
# LEFT - LIVE FEED
# ============================================================

with left:

    st.markdown(
        """
        <div class="card">
            <div class="card-title">
                📹 Live Feed
                <span style="float:right; color:#39e58a;">
                ● Live
                </span>
            </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_image = st.file_uploader(
        "Upload conveyor belt image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    analyze = st.button(
        "🔍 ANALYZE BELT",
        type="primary",
        use_container_width=True
    )

    result = None
    crack_count = 0
    tear_count = 0
    max_confidence = 0
    risk_score = 0
    status = "NORMAL"

    if analyze:

        if uploaded_image is None:

            st.warning("Please upload a conveyor belt image.")

        elif not model_loaded:

            st.error("AI model could not be loaded.")

        else:

            input_image = Image.open(uploaded_image).convert("RGB")

            image_array = np.array(input_image)

            results = model.predict(
                source=image_array,
                conf=0.25,
                imgsz=640,
                verbose=False
            )

            result = results[0]

            # --------------------------------------------
            # Count classes
            # --------------------------------------------

            if result.boxes is not None:

                for cls in result.boxes.cls:

                    class_id = int(cls)

                    if class_id == 0:
                        crack_count += 1

                    elif class_id == 1:
                        tear_count += 1

                if len(result.boxes) > 0:
                    max_confidence = float(
                        result.boxes.conf.max()
                    )

            # --------------------------------------------
            # Risk calculation
            # --------------------------------------------

            risk_score = 0

            if crack_count > 0:
                risk_score += 35

            if tear_count > 0:
                risk_score += 35

            if vibration > 7:
                risk_score += 20

            elif vibration > 5:
                risk_score += 10

            if temperature > 70:
                risk_score += 20

            elif temperature > 60:
                risk_score += 10

            risk_score = min(risk_score, 100)

            # --------------------------------------------
            # Status
            # --------------------------------------------

            if risk_score >= 70:
                status = "CRITICAL"

            elif risk_score >= 40:
                status = "WARNING"

            else:
                status = "NORMAL"

            # --------------------------------------------
            # Annotated image
            # --------------------------------------------

            annotated = result.plot()

            annotated = annotated[:, :, ::-1]

            st.image(
                annotated,
                use_container_width=True
            )

            # --------------------------------------------
            # Damage text
            # --------------------------------------------

            detected_damage = []

            if crack_count > 0:
                detected_damage.append("Crack")

            if tear_count > 0:
                detected_damage.append("Tear")

            if detected_damage:
                damage_text = ", ".join(detected_damage)
            else:
                damage_text = "No visible damage"

            # --------------------------------------------
            # History
            # --------------------------------------------

            inspection_time = datetime.now().strftime(
                "%b %d, %I:%M %p"
            )

            history_item = {
                "Time": inspection_time,
                "Damage": damage_text,
                "Crack": crack_count,
                "Tear": tear_count,
                "Vibration": vibration,
                "Temperature": temperature,
                "Risk": risk_score,
                "Status": status,
                "Image": input_image
            }

            st.session_state.history.append(history_item)

            # --------------------------------------------
            # Alert
            # --------------------------------------------

            if status in ["CRITICAL", "WARNING"]:

                alert_item = {
                    "time": inspection_time,
                    "damage": damage_text,
                    "risk": risk_score
                }

                st.session_state.alerts.insert(
                    0,
                    alert_item
                )

                # Send real Telegram alert only for
                # high-risk inspections
                if risk_score >= 70:

                    send_telegram_alert(
                        damage=damage_text,
                        confidence=max_confidence * 100,
                        vibration=vibration,
                        temperature=temperature,
                        risk_score=risk_score
                    )

            st.session_state.last_analysis = history_item

    else:

        # Default empty live-feed area
        st.markdown(
            """
            <div style="
                height:330px;
                background:#0a1423;
                border:1px solid #243550;
                border-radius:8px;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#738197;
                font-size:18px;
            ">
                📷 Upload a conveyor belt image
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MIDDLE - BELT STATUS
# ============================================================

with middle:

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">🛡️ Belt Status</div>',
        unsafe_allow_html=True
    )

    if st.session_state.last_analysis:

        latest = st.session_state.last_analysis

        if latest["Status"] == "CRITICAL":

            st.markdown(
                """
                <div class="status-alert">
                🔴 CRITICAL
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("Major belt damage risk detected.")

        elif latest["Status"] == "WARNING":

            st.markdown(
                """
                <div style="color:#ffb83d;
                font-size:27px;font-weight:700;">
                🟠 WARNING
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("Potential belt deterioration detected.")

        else:

            st.markdown(
                """
                <div class="status-normal">
                🟢 NORMAL
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("No major damage detected.")

        st.divider()

        # Metrics

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">
                    🔴 Crack
                    </div>

                    <div class="metric-value">
                    {latest["Crack"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">
                    🔵 Tear
                    </div>

                    <div class="metric-value">
                    {latest["Tear"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        c3, c4 = st.columns(2)

        with c3:

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">
                    🟣 Belt Joint
                    </div>

                    <div class="metric-value">
                    0
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">
                    🟡 Other Damage
                    </div>

                    <div class="metric-value">
                    0
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">
                📊 Risk Score
                </div>

                <div class="metric-value">
                {latest["Risk"]}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="status-normal">
            🟢 NORMAL
            </div>

            <p style="color:#9ba9bd;">
            No inspection performed yet.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                """
                <div class="metric-box">
                    <div class="metric-title">🔴 Crack</div>
                    <div class="metric-value">0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                """
                <div class="metric-box">
                    <div class="metric-title">🔵 Tear</div>
                    <div class="metric-value">0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        c3, c4 = st.columns(2)

        with c3:

            st.markdown(
                """
                <div class="metric-box">
                    <div class="metric-title">🟣 Belt Joint</div>
                    <div class="metric-value">0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:

            st.markdown(
                """
                <div class="metric-box">
                    <div class="metric-title">🟡 Other Damage</div>
                    <div class="metric-value">0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <br>
        <div class="small-text">
        🛡️ Monitoring system running 24/7
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RIGHT - ALERTS
# ============================================================

with right:

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">🔔 Alerts & Notifications</div>',
        unsafe_allow_html=True
    )

    if st.session_state.alerts:

        st.markdown(
            f"""
            <div style="color:#ff6565;
            font-size:12px;text-align:right;">
            ● {len(st.session_state.alerts)} new
            </div>
            """,
            unsafe_allow_html=True
        )

        for alert in st.session_state.alerts[:3]:

            st.markdown(
                f"""
                <div class="alert-box">

                    <div class="alert-title">
                    🔴 {alert["damage"]} Detected
                    </div>

                    <div class="alert-time">
                    {alert["time"]}
                    </div>

                    <div class="small-text">
                    Risk Score: {alert["risk"]}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            """
            <div class="normal-box">

            🟢 No new alerts

            <br><br>

            <span class="small-text">
            System is monitoring the conveyor belt.
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Phone notification

    st.markdown(
        """
        <div style="font-size:17px;font-weight:650;">
        📱 Phone Notification
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="small-text">
        Get instant alerts on your phone
        for detected damage.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <br>

        <div class="phone-box">

            <div style="
            text-align:center;
            font-size:50px;">
            📱
            </div>

            <div class="phone-alert">

                <div style="
                color:#ff5b5b;
                font-weight:700;">
                🔴 Belt Damage Alert
                </div>

                <div class="small-text">
                Real-time notification
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# INSPECTION LOG
# ============================================================

st.markdown(
    '<div class="section-heading">🕒 Inspection Log</div>',
    unsafe_allow_html=True
)

if st.session_state.history:

    # Show newest inspections first
    history = list(reversed(st.session_state.history))

    for item in history[:6]:

        c1, c2, c3, c4 = st.columns(
            [1.4, 1.5, 2.0, 1.2]
        )

        with c1:

            st.write(item["Time"])

        with c2:

            st.image(
                item["Image"],
                width=90
            )

        with c3:

            if item["Damage"] == "No visible damage":

                st.success("No Damage")

            else:

                st.warning(item["Damage"])

        with c4:

            if item["Status"] == "NORMAL":

                st.success("Normal")

            else:

                st.error("⚠ Alert")

else:

    st.info(
        "No inspections recorded yet. "
        "Upload an image and click ANALYZE BELT."
    )


# ============================================================
# DAMAGE TREND
# ============================================================

st.markdown(
    '<div class="section-heading">📈 Damage Trend (Last 24 Hours)</div>',
    unsafe_allow_html=True
)

if len(st.session_state.history) >= 2:

    trend_data = []

    for item in st.session_state.history:

        trend_data.append(
            {
                "Inspection": item["Time"],
                "Crack": item["Crack"],
                "Tear": item["Tear"],
                "Risk": item["Risk"]
            }
        )

    trend_df = pd.DataFrame(trend_data)

    chart_df = trend_df[
        ["Crack", "Tear"]
    ]

    st.line_chart(
        chart_df,
        use_container_width=True
    )

else:

    st.info(
        "Run at least two inspections to display the trend."
    )


# ============================================================
# CURRENT SENSOR SNAPSHOT
# ============================================================

st.markdown(
    '<div class="section-heading">📊 Current Sensor Snapshot</div>',
    unsafe_allow_html=True
)

sensor1, sensor2, sensor3 = st.columns(3)

with sensor1:

    st.metric(
        "📳 Vibration",
        f"{vibration:.2f} mm/s"
    )

with sensor2:

    st.metric(
        "🌡️ Temperature",
        f"{temperature:.1f} °C"
    )

with sensor3:

    if st.session_state.last_analysis:

        st.metric(
            "⚠️ Risk Score",
            f'{st.session_state.last_analysis["Risk"]}%'
        )

    else:

        st.metric(
            "⚠️ Risk Score",
            "0%"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br><br>

    <div style="
        text-align:center;
        color:#65748a;
        font-size:12px;
        padding:20px;
        border-top:1px solid #1c293d;
    ">

    🏭 Smart Belt Monitoring System |
    AI-powered conveyor belt inspection |
    Crack + Tear Detection

    </div>
    """,
    unsafe_allow_html=True
)
