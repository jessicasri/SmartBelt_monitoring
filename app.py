import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import requests
from datetime import datetime


# =========================================================
# PAGE SETTINGS
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

st.markdown(
    """
    <style>

    /* ---------- MAIN PAGE ---------- */

    .stApp {
        background: #07101e;
        color: white;
    }

    .block-container {
        max-width: 1600px;
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #0b1424;
        border-right: 1px solid #1d2b40;
    }


    /* ---------- HEADER ---------- */

    .top-header {
        background: #0c1627;
        border: 1px solid #1d2c43;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 18px;
    }

    .main-title {
        color: white;
        font-size: 27px;
        font-weight: 700;
    }

    .sub-title {
        color: #91a0b5;
        font-size: 14px;
        margin-top: 4px;
    }

    .online-text {
        color: #36df82;
        font-size: 14px;
        font-weight: 700;
    }

    .date-text {
        color: #8b99ad;
        font-size: 12px;
        margin-top: 5px;
    }


    /* ---------- SECTION TITLES ---------- */

    .section-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 10px;
    }


    /* ---------- STATUS ---------- */

    .status-normal {
        color: #42e58b;
        font-size: 26px;
        font-weight: 700;
    }

    .status-warning {
        color: #ffb83d;
        font-size: 26px;
        font-weight: 700;
    }

    .status-critical {
        color: #ff5757;
        font-size: 26px;
        font-weight: 700;
    }


    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: #091321;
        border: 1px solid #263650;
        border-radius: 9px;
        padding: 12px;
        min-height: 72px;
    }

    .metric-label {
        color: #8e9db1;
        font-size: 12px;
    }

    .metric-value {
        color: white;
        font-size: 23px;
        font-weight: 700;
        margin-top: 5px;
    }


    /* ---------- ALERT CARD ---------- */

    .alert-card {
        background: #251923;
        border: 1px solid #603140;
        border-radius: 9px;
        padding: 11px;
        margin-bottom: 8px;
    }

    .alert-title {
        color: #ff6262;
        font-size: 14px;
        font-weight: 700;
    }

    .alert-time {
        color: #8491a5;
        font-size: 11px;
        margin-top: 4px;
    }


    /* ---------- PHONE CARD ---------- */

    .phone-card {
        background: #091321;
        border: 1px solid #263650;
        border-radius: 9px;
        padding: 14px;
        text-align: center;
    }

    .phone-icon {
        font-size: 42px;
    }

    .phone-alert {
        background: #202b40;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
        text-align: left;
    }

    .phone-alert-title {
        color: #ff5c5c;
        font-size: 13px;
        font-weight: 700;
    }


    /* ---------- SMALL TEXT ---------- */

    .small-text {
        color: #8391a5;
        font-size: 12px;
    }


    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 8px;
        font-weight: 700;
        min-height: 42px;
    }


    /* ---------- FILE UPLOADER ---------- */

    [data-testid="stFileUploader"] {
        background: #091321;
        border: 1px solid #263650;
        border-radius: 8px;
        padding: 8px;
    }


    /* ---------- NATIVE STREAMLIT CONTAINERS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0d1829;
        border-color: #1f3048;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TELEGRAM ALERT
# =========================================================

def send_telegram_alert(
    damage,
    confidence,
    vibration,
    temperature,
    risk_score,
    status
):

    try:

        bot_token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

        message = f"""
🚨 SMART BELT ALERT

Conveyor belt damage detected.

Status: {status}
Damage: {damage}
AI Confidence: {confidence:.1f}%

📳 Vibration: {vibration:.1f} mm/s
🌡️ Temperature: {temperature:.1f} °C
⚠️ Risk Score: {risk_score}%

Immediate inspection recommended.
"""

        url = (
            f"https://api.telegram.org/"
            f"bot{bot_token}/sendMessage"
        )

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


# =========================================================
# LOAD YOLO MODEL
# =========================================================

@st.cache_resource
def load_model():

    return YOLO("best.pt")


try:

    model = load_model()
    model_loaded = True

except Exception as error:

    model_loaded = False

    st.error("Could not load best.pt")
    st.code(str(error))


# =========================================================
# SESSION VARIABLES
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "latest" not in st.session_state:
    st.session_state.latest = None

if "telegram_sent" not in st.session_state:
    st.session_state.telegram_sent = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🏭 Smart Belt")

    st.markdown("### 🏠 Home")
    st.caption("Dashboard")

    st.markdown("### 🔍 Inspection Log")
    st.caption("Previous inspections")

    st.markdown("### 🔔 Alerts")
    st.caption("Damage notifications")

    st.markdown("### ⚙️ Settings")
    st.caption("System configuration")

    st.divider()

    st.markdown("## ⚙️ Monitoring Controls")

    vibration = st.number_input(
        "📳 Vibration (mm/s)",
        min_value=0.0,
        max_value=20.0,
        value=5.20,
        step=0.10
    )

    temperature = st.number_input(
        "🌡️ Temperature (°C)",
        min_value=0.0,
        max_value=150.0,
        value=40.0,
        step=0.5
    )

    st.divider()

    st.caption("Smart Belt Monitoring System")
    st.caption("v2.0")


# =========================================================
# HEADER
# =========================================================

current_time = datetime.now().strftime(
    "%b %d, %Y  %I:%M %p"
)

st.markdown(
    f"""
    <div class="top-header">
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>
                <div class="main-title">
                    🏭 SMART BELT MONITORING SYSTEM
                </div>

                <div class="sub-title">
                    Intelligent monitoring of conveyor belt damage
                </div>
            </div>

            <div style="text-align:right;">
                <div class="online-text">
                    🟢 System Online
                </div>

                <div class="date-text">
                    {current_time}
                </div>
            </div>

        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MAIN COLUMNS
# =========================================================

left_col, middle_col, right_col = st.columns(
    [5, 3, 2.2],
    gap="medium"
)


# =========================================================
# LEFT COLUMN - LIVE FEED
# =========================================================

with left_col:

    with st.container(border=True):

        st.markdown(
            """
            <div class="card-heading"
                 style="color:#dce7f6;
                        font-size:18px;
                        font-weight:700;
                        margin-bottom:12px;">
                📹 Live Feed
                <span style="
                    float:right;
                    color:#36df82;
                    font-size:13px;">
                    ● Live
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Upload conveyor belt image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file is None:

            st.info(
                "📷 Upload a conveyor belt image to begin inspection."
            )

        else:

            original_image = Image.open(
                uploaded_file
            ).convert("RGB")

            st.image(
                original_image,
                width="stretch"
            )


    st.write("")

    analyze_button = st.button(
        "🔍 ANALYZE BELT",
        type="primary",
        width="stretch"
    )


# =========================================================
# RUN AI ANALYSIS
# =========================================================

if analyze_button:

    st.session_state.telegram_sent = False

    if uploaded_file is None:

        st.warning(
            "Please upload a conveyor belt image."
        )

    elif not model_loaded:

        st.error(
            "The AI model could not be loaded."
        )

    else:

        original_image = Image.open(
            uploaded_file
        ).convert("RGB")

        image_array = np.array(
            original_image
        )

        predictions = model.predict(
            source=image_array,
            conf=0.25,
            imgsz=640,
            verbose=False
        )

        result = predictions[0]

        crack_count = 0
        tear_count = 0
        confidence = 0.0

        if result.boxes is not None:

            for class_value in result.boxes.cls:

                class_id = int(class_value)

                if class_id == 0:
                    crack_count += 1

                elif class_id == 1:
                    tear_count += 1

            if len(result.boxes) > 0:

                confidence = float(
                    result.boxes.conf.max()
                )


        # =================================================
        # RISK SCORE
        # =================================================

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

        risk_score = min(
            risk_score,
            100
        )


        # =================================================
        # STATUS
        # =================================================

        if risk_score >= 70:

            belt_status = "CRITICAL"

        elif risk_score >= 40:

            belt_status = "WARNING"

        else:

            belt_status = "NORMAL"


        # =================================================
        # DAMAGE NAME
        # =================================================

        detected_damage = []

        if crack_count > 0:
            detected_damage.append("Crack")

        if tear_count > 0:
            detected_damage.append("Tear")

        if detected_damage:

            damage_text = ", ".join(
                detected_damage
            )

        else:

            damage_text = "No visible damage"


        # =================================================
        # SAVE INSPECTION
        # =================================================

        inspection_time = datetime.now().strftime(
            "%b %d, %I:%M %p"
        )

        inspection = {

            "Time": inspection_time,

            "Damage": damage_text,

            "Crack": crack_count,

            "Tear": tear_count,

            "Vibration": vibration,

            "Temperature": temperature,

            "Risk": risk_score,

            "Status": belt_status,

            "Confidence": confidence,

            "Image": original_image
        }

        st.session_state.history.append(
            inspection
        )

        st.session_state.latest = inspection


        # =================================================
        # SAVE ALERT
        # =================================================

        if belt_status != "NORMAL":

            alert = {

                "Time": inspection_time,

                "Damage": damage_text,

                "Risk": risk_score
            }

            st.session_state.alerts.insert(
                0,
                alert
            )


        # =================================================
        # TELEGRAM ALERT
        # =================================================

        if belt_status != "NORMAL":

            telegram_success = send_telegram_alert(
                damage_text,
                confidence * 100,
                vibration,
                temperature,
                risk_score,
                belt_status
            )

            if telegram_success:

                st.session_state.telegram_sent = True

            else:

                st.warning(
                    "Telegram notification could not be sent."
                )


# =========================================================
# LATEST RESULT
# =========================================================

latest = st.session_state.latest


# =========================================================
# MIDDLE COLUMN - BELT STATUS
# =========================================================

with middle_col:

    with st.container(border=True):

        st.markdown(
            """
            <div style="
                color:#dce7f6;
                font-size:18px;
                font-weight:700;
                margin-bottom:12px;">
                🛡️ Belt Status
            </div>
            """,
            unsafe_allow_html=True
        )

        if latest is None:

            st.markdown(
                '<div class="status-normal">🟢 NORMAL</div>',
                unsafe_allow_html=True
            )

            st.write(
                "No inspection performed yet."
            )

            crack_value = 0
            tear_value = 0
            risk_value = 0

        else:

            if latest["Status"] == "CRITICAL":

                st.markdown(
                    '<div class="status-critical">🔴 CRITICAL</div>',
                    unsafe_allow_html=True
                )

                st.write(
                    "Major belt damage detected."
                )

            elif latest["Status"] == "WARNING":

                st.markdown(
                    '<div class="status-warning">🟠 WARNING</div>',
                    unsafe_allow_html=True
                )

                st.write(
                    "Potential belt deterioration detected."
                )

            else:

                st.markdown(
                    '<div class="status-normal">🟢 NORMAL</div>',
                    unsafe_allow_html=True
                )

                st.write(
                    "No major damage detected."
                )

            crack_value = latest["Crack"]
            tear_value = latest["Tear"]
            risk_value = latest["Risk"]


        st.divider()


        # CRACK / TEAR

        metric1, metric2 = st.columns(2)

        with metric1:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        🔴 Crack
                    </div>
                    <div class="metric-value">
                        {crack_value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with metric2:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        🔵 Tear
                    </div>
                    <div class="metric-value">
                        {tear_value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.write("")


        # PLACEHOLDER CATEGORIES

        metric3, metric4 = st.columns(2)

        with metric3:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">
                        🟣 Belt Joint
                    </div>
                    <div class="metric-value">
                        0
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with metric4:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">
                        🟡 Other Damage
                    </div>
                    <div class="metric-value">
                        0
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.write("")


        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    ⚠️ Risk Score
                </div>
                <div class="metric-value">
                    {risk_value}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.caption(
            "🛡️ Monitoring system running 24/7"
        )


# =========================================================
# RIGHT COLUMN - ALERTS
# =========================================================

with right_col:

    with st.container(border=True):

        st.markdown(
            """
            <div style="
                color:#dce7f6;
                font-size:18px;
                font-weight:700;
                margin-bottom:12px;">
                🔔 Alerts & Notifications
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.alerts:

            for alert in st.session_state.alerts[:3]:

                st.markdown(
                    f"""
                    <div class="alert-card">

                        <div class="alert-title">
                            🔴 {alert["Damage"]} Detected
                        </div>

                        <div class="alert-time">
                            {alert["Time"]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.markdown(
                """
                <div class="status-normal">
                    🟢
                </div>

                <div style="
                    font-size:15px;
                    font-weight:600;
                    margin-top:5px;">
                    No new alerts
                </div>

                <div class="small-text">
                    System is monitoring the conveyor belt.
                </div>
                """,
                unsafe_allow_html=True
            )


        st.divider()


        st.markdown(
            """
            <div style="
                color:#dce7f6;
                font-size:17px;
                font-weight:700;
                margin-bottom:5px;">
                📱 Phone Notification
            </div>

            <div class="small-text">
                Get instant alerts on your phone
                for detected damage.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.write("")


        st.markdown(
            """
            <div class="phone-card">

                <div class="phone-icon">
                    📱
                </div>

                <div class="phone-alert">

                    <div class="phone-alert-title">
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


        if st.session_state.telegram_sent:

            st.success(
                "Telegram alert sent to phone."
            )


# =========================================================
# LOWER SECTION
# =========================================================

st.markdown(
    '<div class="section-title">🕒 Inspection Log</div>',
    unsafe_allow_html=True
)


log_column, trend_column = st.columns(
    [1.1, 0.9],
    gap="medium"
)


# =========================================================
# INSPECTION LOG
# =========================================================

with log_column:

    if not st.session_state.history:

        st.info(
            "No inspections recorded yet. "
            "Upload an image and click ANALYZE BELT."
        )

    else:

        for item in reversed(
            st.session_state.history[-5:]
        ):

            with st.container(border=True):

                log1, log2, log3 = st.columns(
                    [1.2, 1.0, 1.5]
                )

                with log1:

                    st.write(
                        item["Time"]
                    )

                with log2:

                    st.image(
                        item["Image"],
                        width=80
                    )

                with log3:

                    st.write(
                        f"**{item['Damage']}**"
                    )

                    if item["Status"] == "NORMAL":

                        st.success(
                            "Normal"
                        )

                    else:

                        st.error(
                            "⚠ Alert"
                        )


# =========================================================
# DAMAGE TREND
# =========================================================

with trend_column:

    st.markdown(
        '<div class="section-title">📈 Damage Trend</div>',
        unsafe_allow_html=True
    )

    if len(st.session_state.history) < 2:

        st.info(
            "Run at least two inspections "
            "to display the trend."
        )

    else:

        chart_rows = []

        for number, item in enumerate(
            st.session_state.history,
            start=1
        ):

            chart_rows.append(
                {
                    "Inspection": number,
                    "Crack": item["Crack"],
                    "Tear": item["Tear"]
                }
            )

        chart_df = pd.DataFrame(
            chart_rows
        )

        chart_df = chart_df.set_index(
            "Inspection"
        )

        st.line_chart(
            chart_df,
            width="stretch"
        )


# =========================================================
# CURRENT SENSOR SNAPSHOT
# =========================================================

st.markdown(
    '<div class="section-title">📊 Current Sensor Snapshot</div>',
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

    st.metric(
        "⚠️ Risk Score",
        f"{risk_value}%"
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        font-size:12px;
        padding:18px;
        margin-top:18px;
        border-top:1px solid #1c293d;">

        🏭 Smart Belt Monitoring System
        &nbsp; | &nbsp;
        AI-powered conveyor belt inspection
        &nbsp; | &nbsp;
        Crack + Tear Detection

    </div>
    """,
    unsafe_allow_html=True
)
