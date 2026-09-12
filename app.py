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

st.markdown("""
<style>

.stApp {
    background-color: #07101e;
}

.block-container {
    max-width: 1550px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #0b1424;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e8eef7;
}


/* HEADINGS */

h1, h2, h3 {
    color: #e8eef7 !important;
}

p, label {
    color: #aab7c9;
}


/* BUTTON */

.stButton > button {
    width: 100%;
    min-height: 45px;
    border-radius: 8px;
    font-weight: 700;
}


/* CONTAINERS */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #0d1829;
    border: 1px solid #263650;
    border-radius: 12px;
}


/* METRICS */

div[data-testid="stMetric"] {
    background-color: #091321;
    border: 1px solid #263650;
    border-radius: 9px;
    padding: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #91a0b5 !important;
}

div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
}


/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background-color: #091321;
    border: 1px solid #263650;
    border-radius: 9px;
    padding: 8px;
}


/* ALERT BOXES */

div[data-testid="stAlert"] {
    border-radius: 9px;
}


/* DATAFRAME */

[data-testid="stDataFrame"] {
    border-radius: 9px;
}


/* DIVIDER */

hr {
    border-color: #263650;
}

</style>
""", unsafe_allow_html=True)


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
    st.error("❌ Could not load the AI model.")
    st.code(str(error))


# =========================================================
# SESSION STATE
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

    st.title("🏭 Smart Belt")

    st.markdown("### 🏠 Home")
    st.caption("Monitoring Dashboard")

    st.markdown("### 🔍 Inspection Log")
    st.caption("Previous inspections")

    st.markdown("### 🔔 Alerts")
    st.caption("Damage notifications")

    st.markdown("### ⚙️ Settings")
    st.caption("System configuration")

    st.divider()

    st.subheader("⚙️ Monitoring Controls")

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
    st.caption("Version 2.0")


# =========================================================
# HEADER
# =========================================================

current_time = datetime.now().strftime(
    "%b %d, %Y  •  %I:%M %p"
)

header_left, header_right = st.columns([4, 1])

with header_left:

    st.title("🏭 SMART BELT MONITORING SYSTEM")

    st.caption(
        "AI-powered monitoring of conveyor belt damage"
    )

with header_right:

    st.success("🟢 System Online")

    st.caption(current_time)


st.divider()


# =========================================================
# MAIN COLUMNS
# =========================================================

left_col, middle_col, right_col = st.columns(
    [5, 3, 2.2],
    gap="medium"
)


# =========================================================
# LEFT — LIVE FEED
# =========================================================

with left_col:

    with st.container(border=True):

        st.subheader("📹 Live Feed")

        st.caption(
            "Upload a conveyor belt image for AI inspection."
        )

        uploaded_file = st.file_uploader(
            "Upload conveyor belt image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file is None:

            st.info(
                "📷 Upload an image to begin inspection."
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
# ANALYSIS
# =========================================================

if analyze_button:

    st.session_state.telegram_sent = False

    if uploaded_file is None:

        st.warning(
            "Please upload a conveyor belt image first."
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
        # DAMAGE
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
        # TELEGRAM
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


if latest is None:

    crack_value = 0
    tear_value = 0
    risk_value = 0

else:

    crack_value = latest["Crack"]
    tear_value = latest["Tear"]
    risk_value = latest["Risk"]


# =========================================================
# MIDDLE — BELT STATUS
# =========================================================

with middle_col:

    with st.container(border=True):

        st.subheader("🛡️ Belt Status")

        if latest is None:

            st.success("🟢 NORMAL")

            st.caption(
                "Waiting for first inspection."
            )

        else:

            if latest["Status"] == "CRITICAL":

                st.error("🔴 CRITICAL")

                st.caption(
                    "Major belt damage detected."
                )

            elif latest["Status"] == "WARNING":

                st.warning("🟠 WARNING")

                st.caption(
                    "Potential belt deterioration detected."
                )

            else:

                st.success("🟢 NORMAL")

                st.caption(
                    "No major damage detected."
                )


        st.divider()


        # CRACK / TEAR

        metric1, metric2 = st.columns(2)

        with metric1:

            st.metric(
                "🔴 Crack",
                crack_value
            )

        with metric2:

            st.metric(
                "🔵 Tear",
                tear_value
            )


        # OTHER INFORMATION

        st.metric(
            "⚠️ Risk Score",
            f"{risk_value}%"
        )

        st.divider()

        st.caption(
            "🛡️ Continuous condition monitoring"
        )


# =========================================================
# RIGHT — ALERTS
# =========================================================

with right_col:

    with st.container(border=True):

        st.subheader("🔔 Alerts")

        if st.session_state.alerts:

            for alert in st.session_state.alerts[:3]:

                st.error(
                    f"🔴 {alert['Damage']} Detected\n\n"
                    f"{alert['Time']}  •  "
                    f"Risk: {alert['Risk']}%"
                )

        else:

            st.success(
                "🟢 No new alerts"
            )

            st.caption(
                "System is monitoring the conveyor belt."
            )


        st.divider()

        st.markdown("### 📱 Phone Notification")

        st.caption(
            "Instant Telegram alerts for WARNING "
            "and CRITICAL conditions."
        )

        if st.session_state.telegram_sent:

            st.success(
                "📲 Telegram alert sent successfully."
            )

        else:

            st.info(
                "📲 Telegram monitoring active."
            )


# =========================================================
# INSPECTION LOG
# =========================================================

st.divider()

st.subheader("🕒 Inspection Log")

if not st.session_state.history:

    st.info(
        "No inspections recorded yet. "
        "Upload an image and click ANALYZE BELT."
    )

else:

    table_rows = []

    for item in reversed(
        st.session_state.history[-10:]
    ):

        table_rows.append(
            {
                "Time": item["Time"],
                "Damage": item["Damage"],
                "Crack": item["Crack"],
                "Tear": item["Tear"],
                "Vibration": f"{item['Vibration']:.1f}",
                "Temperature": f"{item['Temperature']:.1f} °C",
                "Risk": f"{item['Risk']}%",
                "Status": item["Status"],
                "Confidence": f"{item['Confidence'] * 100:.1f}%"
            }
        )

    log_df = pd.DataFrame(
        table_rows
    )

    st.dataframe(
        log_df,
        width="stretch",
        hide_index=True
    )


# =========================================================
# DAMAGE TREND
# =========================================================

st.divider()

trend_left, trend_right = st.columns(
    [1.5, 1],
    gap="medium"
)


with trend_left:

    st.subheader("📈 Damage Trend")

    if len(st.session_state.history) < 2:

        st.info(
            "Run at least two inspections "
            "to display the damage trend."
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
            chart_df
        )


# =========================================================
# SENSOR SNAPSHOT
# =========================================================

with trend_right:

    st.subheader("📊 Current Sensor Snapshot")

    sensor1, sensor2 = st.columns(2)

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

    st.metric(
        "⚠️ Current Risk",
        f"{risk_value}%"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🏭 Smart Belt Monitoring System  •  "
    "AI-powered conveyor belt inspection  •  "
    "Crack + Tear Detection"
)
