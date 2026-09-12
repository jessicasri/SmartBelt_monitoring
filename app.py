import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
from datetime import datetime


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Smart Belt Monitoring",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background-color: #07101e;
    color: white;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1550px;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #0c1525;
    border-right: 1px solid #1d2a40;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white;
}


/* HEADER */

.header-box {
    background: #0c1627;
    border: 1px solid #1e2c43;
    border-radius: 10px;
    padding: 18px 25px;
    margin-bottom: 18px;
}

.header-title {
    font-size: 27px;
    font-weight: 700;
    color: white;
}

.header-subtitle {
    color: #91a0b5;
    font-size: 14px;
    margin-top: 4px;
}

.online {
    color: #31dc82;
    font-weight: 600;
    font-size: 14px;
}


/* CARDS */

.card {
    background: #0d1829;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 17px;
    min-height: 100%;
}

.card-title {
    color: #dbe7f7;
    font-size: 18px;
    font-weight: 650;
    margin-bottom: 12px;
}


/* LIVE FEED */

.feed-empty {
    height: 285px;
    border-radius: 8px;
    border: 1px solid #263752;
    background: #091321;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #718096;
    font-size: 16px;
}


/* STATUS */

.normal {
    color: #42e58b;
    font-size: 27px;
    font-weight: 700;
}

.warning {
    color: #ffb83d;
    font-size: 27px;
    font-weight: 700;
}

.critical {
    color: #ff5757;
    font-size: 27px;
    font-weight: 700;
}


/* METRICS */

.metric {
    background: #091321;
    border: 1px solid #273852;
    border-radius: 9px;
    padding: 12px;
    min-height: 72px;
}

.metric-label {
    color: #91a0b5;
    font-size: 12px;
}

.metric-number {
    color: white;
    font-size: 23px;
    font-weight: 700;
    margin-top: 4px;
}


/* ALERT */

.alert {
    background: #251923;
    border: 1px solid #5b3040;
    border-radius: 9px;
    padding: 12px;
    margin-bottom: 9px;
}

.alert-title {
    color: #ff6464;
    font-weight: 650;
}

.alert-time {
    color: #8794a8;
    font-size: 12px;
}


/* PHONE */

.phone {
    background: #091321;
    border: 1px solid #253650;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
    min-height: 170px;
}

.phone-icon {
    font-size: 50px;
}

.phone-message {
    background: #202c40;
    border-radius: 9px;
    padding: 10px;
    text-align: left;
    margin-top: 10px;
}

.phone-title {
    color: #ff5b5b;
    font-weight: 700;
}


/* INFO */

.info {
    color: #8190a5;
    font-size: 13px;
}


/* SECTION */

.section-title {
    color: white;
    font-size: 21px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 10px;
}


/* STREAMLIT BUTTON */

.stButton > button {
    border-radius: 7px;
    font-weight: 650;
}


/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: #0a1423;
    border-radius: 8px;
}


/* NUMBER INPUT */

div[data-testid="stNumberInput"] input {
    background: #091321;
    color: white;
}


/* DATAFRAME */

[data-testid="stDataFrame"] {
    border-radius: 8px;
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
    model_ok = True
except Exception as e:
    model_ok = False
    st.error("Could not load best.pt")
    st.code(str(e))


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "latest" not in st.session_state:
    st.session_state.latest = None


# ============================================================
# SIDEBAR
# ============================================================

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


# ============================================================
# HEADER
# ============================================================

current_time = datetime.now().strftime("%b %d, %Y %I:%M %p")

st.markdown(
    f"""
    <div class="header-box">

        <div style="display:flex;
                    justify-content:space-between;
                    align-items:center;">

            <div>

                <div class="header-title">
                    🏭 SMART BELT MONITORING SYSTEM
                </div>

                <div class="header-subtitle">
                    Intelligent monitoring of conveyor belt damage
                </div>

            </div>

            <div style="text-align:right;">

                <div class="online">
                    🟢 System Online
                </div>

                <div class="info">
                    {current_time}
                </div>

            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# THREE MAIN COLUMNS
# ============================================================

left, middle, right = st.columns(
    [5.2, 3.0, 2.2],
    gap="medium"
)


# ============================================================
# LEFT COLUMN - LIVE FEED
# ============================================================

with left:

    st.markdown(
        """
        <div class="card">

        <div class="card-title">
            📹 Live Feed
            <span style="float:right;color:#35df82;">
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

        st.markdown(
            """
            <div class="feed-empty">
                📷 Upload a conveyor belt image
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        input_image = Image.open(
            uploaded_file
        ).convert("RGB")

        st.image(
            input_image,
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    analyze = st.button(
        "🔍 ANALYZE BELT",
        type="primary",
        use_container_width=True
    )


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if uploaded_file is None:

        st.warning(
            "Please upload a conveyor belt image first."
        )

    elif not model_ok:

        st.error(
            "AI model could not be loaded."
        )

    else:

        input_image = Image.open(
            uploaded_file
        ).convert("RGB")

        image_array = np.array(input_image)

        results = model.predict(
            source=image_array,
            conf=0.25,
            imgsz=640,
            verbose=False
        )

        result = results[0]

        crack_count = 0
        tear_count = 0
        max_confidence = 0

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

        # ====================================================
        # RISK
        # ====================================================

        risk = 0

        if crack_count > 0:
            risk += 35

        if tear_count > 0:
            risk += 35

        if vibration > 7:
            risk += 20

        elif vibration > 5:
            risk += 10

        if temperature > 70:
            risk += 20

        elif temperature > 60:
            risk += 10

        risk = min(risk, 100)

        if risk >= 70:
            status = "CRITICAL"

        elif risk >= 40:
            status = "WARNING"

        else:
            status = "NORMAL"

        damage = []

        if crack_count > 0:
            damage.append("Crack")

        if tear_count > 0:
            damage.append("Tear")

        if damage:
            damage_text = ", ".join(damage)
        else:
            damage_text = "No visible damage"

        # ====================================================
        # SAVE HISTORY
        # ====================================================

        time_now = datetime.now().strftime(
            "%b %d, %I:%M %p"
        )

        history_item = {
            "Time": time_now,
            "Damage": damage_text,
            "Crack": crack_count,
            "Tear": tear_count,
            "Vibration": vibration,
            "Temperature": temperature,
            "Risk": risk,
            "Status": status,
            "Image": input_image
        }

        st.session_state.history.append(
            history_item
        )

        st.session_state.latest = history_item

        if status != "NORMAL":

            st.session_state.alerts.insert(
                0,
                {
                    "Time": time_now,
                    "Damage": damage_text,
                    "Risk": risk
                }
            )

        # ====================================================
        # RESULT IMAGE
        # ====================================================

        annotated = result.plot()

        annotated = annotated[:, :, ::-1]

        st.session_state.latest["Annotated"] = annotated


# ============================================================
# SHOW RESULT / STATUS / ALERTS
# ============================================================

latest = st.session_state.latest


# ============================================================
# MIDDLE - STATUS
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

    if latest is None:

        st.markdown(
            '<div class="normal">🟢 NORMAL</div>',
            unsafe_allow_html=True
        )

        st.write(
            "No inspection performed yet."
        )

        crack = 0
        tear = 0
        risk = 0

    else:

        if latest["Status"] == "CRITICAL":

            st.markdown(
                '<div class="critical">🔴 CRITICAL</div>',
                unsafe_allow_html=True
            )

        elif latest["Status"] == "WARNING":

            st.markdown(
                '<div class="warning">🟠 WARNING</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="normal">🟢 NORMAL</div>',
                unsafe_allow_html=True
            )

        st.write(
            "Major damage detected."
            if latest["Status"] != "NORMAL"
            else
            "No major damage detected."
        )

        crack = latest["Crack"]
        tear = latest["Tear"]
        risk = latest["Risk"]

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-label">
                    🔴 Crack
                </div>

                <div class="metric-number">
                    {crack}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-label">
                    🔵 Tear
                </div>

                <div class="metric-number">
                    {tear}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    with c3:

        st.markdown(
            """
            <div class="metric">

                <div class="metric-label">
                    🟣 Belt Joint
                </div>

                <div class="metric-number">
                    0
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            """
            <div class="metric">

                <div class="metric-label">
                    🟡 Other Damage
                </div>

                <div class="metric-number">
                    0
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="metric">

            <div class="metric-label">
                ⚠️ Risk Score
            </div>

            <div class="metric-number">
                {risk}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <br>

        <div class="info">
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
                        font-size:12px;
                        text-align:right;">
                ● {len(st.session_state.alerts)} new
            </div>
            """,
            unsafe_allow_html=True
        )

        for alert in st.session_state.alerts[:3]:

            st.markdown(
                f"""
                <div class="alert">

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
            <div class="normal">
                🟢
            </div>

            <div style="
                font-size:16px;
                font-weight:600;
                margin-top:5px;">
                No new alerts
            </div>

            <div class="info">
                System is monitoring the conveyor belt.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        """
        <div class="card-title">
            📱 Phone Notification
        </div>

        <div class="info">
            Get instant alerts on your phone
            for detected damage.
        </div>

        <br>

        <div class="phone">

            <div class="phone-icon">
                📱
            </div>

            <div class="phone-message">

                <div class="phone-title">
                    🔴 Belt Damage Alert
                </div>

                <div class="info">
                    Real-time notification
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# INSPECTION LOG + TREND
# ============================================================

log_col, trend_col = st.columns(
    [1.05, 0.95],
    gap="medium"
)


# ============================================================
# INSPECTION LOG
# ============================================================

with log_col:

    st.markdown(
        '<div class="section-title">🕒 Inspection Log</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.info(
            "No inspections recorded yet. "
            "Upload an image and click ANALYZE BELT."
        )

    else:

        for item in reversed(
            st.session_state.history[-5:]
        ):

            c1, c2, c3 = st.columns(
                [1.2, 1.2, 1.3]
            )

            with c1:
                st.write(item["Time"])

            with c2:

                st.image(
                    item["Image"],
                    width=80
                )

            with c3:

                st.write(
                    f"**{item['Damage']}**"
                )

                if item["Status"] == "NORMAL":

                    st.success(
                        "Normal",
                        icon="🟢"
                    )

                else:

                    st.error(
                        "Alert",
                        icon="⚠️"
                    )


# ============================================================
# DAMAGE TREND
# ============================================================

with trend_col:

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

        chart_data = pd.DataFrame(
            [
                {
                    "Inspection": i + 1,
                    "Crack": item["Crack"],
                    "Tear": item["Tear"]
                }
                for i, item
                in enumerate(st.session_state.history)
            ]
        )

        chart_data = chart_data.set_index(
            "Inspection"
        )

        st.line_chart(
            chart_data,
            use_container_width=True
        )


# ============================================================
# SENSOR SNAPSHOT
# ============================================================

st.markdown(
    '<div class="section-title">📊 Current Sensor Snapshot</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3)

with s1:

    st.metric(
        "📳 Vibration",
        f"{vibration:.2f} mm/s"
    )

with s2:

    st.metric(
        "🌡️ Temperature",
        f"{temperature:.1f} °C"
    )

with s3:

    st.metric(
        "⚠️ Risk Score",
        f"{risk}%"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        font-size:12px;
        padding:20px;
        margin-top:20px;
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
