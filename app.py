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
    layout="wide"
)


# =========================================================
# LOAD AI MODEL
# =========================================================

model = YOLO("best.pt")


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: 700;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #777;
    margin-bottom: 20px;
}

.status-monitoring {
    background-color: #dff5e1;
    color: #16802b;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.risk-low {
    background-color: #dff5e1;
    color: #16802b;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.risk-medium {
    background-color: #fff1c7;
    color: #946200;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.risk-high {
    background-color: #ffd9d9;
    color: #b00020;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

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


# =========================================================
# SYSTEM STATUS
# =========================================================

st.markdown(
    '<div class="status-monitoring">'
    '🟢 SYSTEM STATUS: MONITORING'
    '</div>',
    unsafe_allow_html=True
)

st.write("")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Monitoring Controls")

vibration = st.sidebar.number_input(
    "📳 Vibration (mm/s)",
    min_value=0.0,
    value=5.0,
    step=0.1
)

temperature = st.sidebar.number_input(
    "🌡️ Temperature (°C)",
    min_value=0.0,
    value=40.0,
    step=0.1
)

st.sidebar.info(
    "Prototype thresholds:\n\n"
    "Vibration > 7 mm/s\n\n"
    "Temperature > 70 °C"
)


# =========================================================
# IMAGE UPLOAD
# =========================================================

image = st.file_uploader(
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

    if image is None:

        st.warning(
            "Please upload a conveyor belt image."
        )

    else:

        # -------------------------------------------------
        # READ IMAGE
        # -------------------------------------------------

        input_image = Image.open(image).convert("RGB")

        image_array = np.array(input_image)


        # -------------------------------------------------
        # YOLO PREDICTION
        # -------------------------------------------------

        results = model.predict(
            source=image_array,
            conf=0.25,
            imgsz=640,
            verbose=False
        )

        result = results[0]


        # -------------------------------------------------
        # DETECTION INFORMATION
        # -------------------------------------------------

        crack_count = 0
        tear_count = 0

        crack_confidences = []
        tear_confidences = []


        if result.boxes is not None:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # Class 0 = Crack
                if class_id == 0:

                    crack_count += 1
                    crack_confidences.append(confidence)

                # Class 1 = Tear
                elif class_id == 1:

                    tear_count += 1
                    tear_confidences.append(confidence)


        # -------------------------------------------------
        # ANNOTATED IMAGE
        # -------------------------------------------------

        annotated_image = result.plot()

        annotated_image = annotated_image[:, :, ::-1]


        # =================================================
        # SENSOR WARNINGS
        # =================================================

        vibration_warning = vibration > 7

        temperature_warning = temperature > 70


        # =================================================
        # RISK SCORE
        # =================================================

        vibration_score = min(
            (vibration / 10) * 40,
            40
        )

        temperature_score = min(
            (temperature / 80) * 30,
            30
        )

        visual_score = 0

        if crack_count > 0:
            visual_score += 15

        if tear_count > 0:
            visual_score += 15


        risk_score = (
            vibration_score
            + temperature_score
            + visual_score
        )

        risk_score = min(risk_score, 100)


        # =================================================
        # RISK LEVEL
        # =================================================

        if risk_score < 40:

            risk_level = "LOW RISK"
            risk_class = "risk-low"
            risk_icon = "🟢"

        elif risk_score < 70:

            risk_level = "MEDIUM RISK"
            risk_class = "risk-medium"
            risk_icon = "🟠"

        else:

            risk_level = "HIGH RISK"
            risk_class = "risk-high"
            risk_icon = "🔴"


        # =================================================
        # CURRENT SNAPSHOT + STATUS
        # =================================================

        st.divider()

        left, right = st.columns([1, 1.2])


        # =================================================
        # LEFT SIDE
        # =================================================

        with left:

            st.subheader("📷 CURRENT BELT SNAPSHOT")

            st.image(
                annotated_image,
                use_container_width=True
            )


        # =================================================
        # RIGHT SIDE
        # =================================================

        with right:

            st.subheader("📊 CURRENT STATUS")


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "📳 Vibration",
                    f"{vibration:.1f} mm/s"
                )

                st.metric(
                    "🌡️ Temperature",
                    f"{temperature:.1f} °C"
                )


            with col2:

                if crack_count > 0:

                    st.error(
                        f"Crack: DETECTED ({crack_count})"
                    )

                else:

                    st.success(
                        "Crack: NOT DETECTED"
                    )


                if tear_count > 0:

                    st.error(
                        f"Tear: DETECTED ({tear_count})"
                    )

                else:

                    st.success(
                        "Tear: NOT DETECTED"
                    )


            # -------------------------------------------------
            # CONFIDENCE
            # -------------------------------------------------

            if crack_confidences:

                crack_confidence = (
                    max(crack_confidences) * 100
                )

                st.write(
                    f"**Crack Confidence:** "
                    f"{crack_confidence:.1f}%"
                )


            if tear_confidences:

                tear_confidence = (
                    max(tear_confidences) * 100
                )

                st.write(
                    f"**Tear Confidence:** "
                    f"{tear_confidence:.1f}%"
                )


            # -------------------------------------------------
            # RISK
            # -------------------------------------------------

            st.metric(
                "⚠️ Risk Score",
                f"{risk_score:.0f}%"
            )

            st.markdown(
                f'<div class="{risk_class}">'
                f'{risk_icon} {risk_level}'
                f'</div>',
                unsafe_allow_html=True
            )


        # =================================================
        # WARNINGS
        # =================================================

        st.divider()

        st.subheader("⚠️ CONDITION ANALYSIS")


        if crack_count > 0:

            st.warning(
                f"🔴 Crack detected by AI "
                f"({crack_count} detection(s))."
            )


        if tear_count > 0:

            st.warning(
                f"🔴 Tear detected by AI "
                f"({tear_count} detection(s))."
            )


        if vibration_warning:

            st.warning(
                f"📳 High vibration detected: "
                f"{vibration:.1f} mm/s"
            )

        else:

            st.success(
                f"📳 Vibration normal: "
                f"{vibration:.1f} mm/s"
            )


        if temperature_warning:

            st.warning(
                f"🌡️ High temperature detected: "
                f"{temperature:.1f} °C"
            )

        else:

            st.success(
                f"🌡️ Temperature normal: "
                f"{temperature:.1f} °C"
            )


        # =================================================
        # RECOMMENDATION
        # =================================================

        st.divider()

        if risk_score >= 70:

            st.error(
                "🔧 **RECOMMENDATION:** "
                "Immediate inspection recommended. "
                "Possible belt deterioration detected."
            )

        elif risk_score >= 40:

            st.warning(
                "🔧 **RECOMMENDATION:** "
                "Schedule detailed inspection and "
                "continue monitoring."
            )

        else:

            st.success(
                "🔧 **RECOMMENDATION:** "
                "Continue normal monitoring."
            )


        # =================================================
        # INSPECTION HISTORY
        # =================================================

        st.divider()

        st.subheader("📈 INSPECTION HISTORY")


        history = pd.DataFrame({

            "Inspection": [
                1, 2, 3, 4, 5, 6
            ],

            "Vibration": [
                4.2, 4.8, 5.7, 6.8, 8.1, 8.7
            ],

            "Temperature": [
                39, 42, 47, 55, 64, 71
            ],

            "Risk Score": [
                29, 32, 39, 56, 73, 82
            ]
        })


        tab1, tab2, tab3 = st.tabs([
            "📳 Vibration",
            "🌡️ Temperature",
            "⚠️ Risk Score"
        ])


        with tab1:

            st.line_chart(
                history.set_index("Inspection")[
                    "Vibration"
                ]
            )


        with tab2:

            st.line_chart(
                history.set_index("Inspection")[
                    "Temperature"
                ]
            )


        with tab3:

            st.line_chart(
                history.set_index("Inspection")[
                    "Risk Score"
                ]
            )


        # =================================================
        # INSPECTION LOG
        # =================================================

        st.divider()

        st.subheader("📋 INSPECTION LOG")


        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )


        log = pd.DataFrame({

            "Time": [current_time],

            "Vibration": [
                f"{vibration:.1f} mm/s"
            ],

            "Temperature": [
                f"{temperature:.1f} °C"
            ],

            "Crack": [
                "Detected"
                if crack_count > 0
                else "Not detected"
            ],

            "Tear": [
                "Detected"
                if tear_count > 0
                else "Not detected"
            ],

            "Risk": [
                f"{risk_score:.0f}%"
            ],

            "Status": [
                risk_level
            ]
        })


        st.dataframe(
            log,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Smart Belt Monitoring System | "
    "AI visual inspection + vibration + temperature monitoring"
)
