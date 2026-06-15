import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="MU Couriers",
    page_icon="📦",
    layout="wide"
)

# -------------------------
# HARDCODED CREDENTIALS
# -------------------------
GATE_USERNAME = "gate"
GATE_PASSWORD = "gate123"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Student credentials (reg_no: password)
STUDENT_CREDENTIALS = {
    "sm23uefb223": "student123",
    "sm24uefb100": "student123",
}

# -------------------------
# SESSION STATE INIT
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "reg_no" not in st.session_state:
    st.session_state.reg_no = None

# -------------------------
# CREATE CSV IF NOT EXISTS
# -------------------------
if not os.path.exists("parcels.csv"):
    df = pd.DataFrame(columns=[
        "student_name", "reg_no", "email",
        "hostel", "courier_company", "tracking_number", "status"
    ])
    df.to_csv("parcels.csv", index=False)

# -------------------------
# EMAIL FUNCTION
# -------------------------
def send_notification_email(to_email, student_name, tracking_number, status="Collected at Gate"):
    SENDER_EMAIL = "mucouriers@gmail.com"
    SENDER_PASSWORD = "yzdc gwdl txuo yeic"

    msg = EmailMessage()
    msg['Subject'] = f"📦 MU Couriers: Parcel Update - {status}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    content = f"""
Dear {student_name},

Your parcel status has been updated in the MU Couriers system.

Tracking Number: {tracking_number}
Current Status: {status}

Thank you for using MU Couriers.

Regards,
MU Couriers
Mahindra University
    """
    msg.set_content(content)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# -------------------------
# LOGIN PAGE
# -------------------------
def show_login():
    st.markdown("""
        <style>
        .login-box {
            max-width: 420px;
            margin: 80px auto;
            padding: 2.5rem;
            background: #1e1e2e;
            border-radius: 16px;
            border: 1px solid #333;
        }
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .login-sub {
            text-align: center;
            color: #aaaaaa;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">📦 MU Couriers</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Campus Courier Management System</div>', unsafe_allow_html=True)
    st.markdown("---")

    role = st.selectbox("Login As", ["Student", "Gate Staff", "Admin"])

    if role == "Student":
        reg = st.text_input("Registration Number")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if reg in STUDENT_CREDENTIALS and STUDENT_CREDENTIALS[reg] == pwd:
                st.session_state.logged_in = True
                st.session_state.role = "Student"
                st.session_state.reg_no = reg
                st.rerun()
            else:
                st.error("❌ Invalid Registration Number or Password.")

    elif role == "Gate Staff":
        username = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username == GATE_USERNAME and pwd == GATE_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.role = "Gate"
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    elif role == "Admin":
        username = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

# -------------------------
# LOGOUT BUTTON
# -------------------------
def show_logout():
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.role}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.reg_no = None
            st.rerun()

# =====================================================
# GATE PORTAL
# =====================================================
def gate_portal():
    st.header("🚪 Gate Portal")

    student = st.text_input("Student Name")
    reg_no = st.text_input("Registration Number")
    email = st.text_input("Student Email")
    hostel = st.selectbox("Hostel", ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"])
    courier = st.text_input("Courier Company")
    tracking = st.text_input("Tracking Number")

    if st.button("Register Parcel"):
        if student and reg_no and email and courier and tracking:
            parcel = {
                "student_name": student,
                "reg_no": reg_no,
                "email": email,
                "hostel": hostel,
                "courier_company": courier,
                "tracking_number": tracking,
                "status": "Collected at Gate"
            }
            df = pd.read_csv("parcels.csv")
            df = pd.concat([df, pd.DataFrame([parcel])], ignore_index=True)
            df.to_csv("parcels.csv", index=False)

            with st.spinner("Sending email notification..."):
                email_sent = send_notification_email(email, student, tracking)

            if email_sent:
                st.success("✅ Parcel Registered! Email notification sent to student.")
            else:
                st.warning("Parcel Registered, but email failed to send.")
        else:
            st.warning("Please fill all fields.")

# =====================================================
# STUDENT PORTAL
# =====================================================
def student_portal():
    st.header("🎓 Student Portal")

    reg_no = st.session_state.reg_no
    df = pd.read_csv("parcels.csv")
    result = df[df["reg_no"].astype(str).str.strip() == reg_no.strip()]

    if len(result) > 0:
        st.success(f"Found {len(result)} parcel(s) for your account.")

        for index, parcel in result.iterrows():
            with st.expander(f"📦 {parcel['courier_company']} - {parcel['tracking_number']}"):
                st.write(f"**Student:** {parcel['student_name']}")
                st.write(f"**Hostel:** {parcel['hostel']}")
                st.write(f"**Status:** {parcel['status']}")

                progress = {
                    "Collected at Gate": 33,
                    "Arrived at Mail Desk": 66,
                    "Parcel Collected": 100
                }
                st.progress(progress.get(parcel["status"], 0))
                st.divider()
    else:
        st.info("No parcels found for your account.")

# =====================================================
# ADMIN DASHBOARD
# =====================================================
def admin_dashboard():
    st.header("📊 Admin Dashboard")

    df = pd.read_csv("parcels.csv")
    total = len(df)
    gate_count = len(df[df["status"] == "Collected at Gate"])
    maildesk_count = len(df[df["status"] == "Arrived at Mail Desk"])
    collected_count = len(df[df["status"] == "Parcel Collected"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Parcels", total)
    col2.metric("At Gate", gate_count)
    col3.metric("At Mail Desk", maildesk_count)
    col4.metric("Collected", collected_count)

    st.divider()
    st.subheader("Search Parcel")
    keyword = st.text_input("Search by Registration Number")
    filtered_df = df

    if keyword:
        filtered_df = df[
            df["reg_no"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)

    st.divider()
    st.subheader("Update Parcel Status")
    tracking_number = st.text_input("Tracking Number")
    new_status = st.selectbox(
        "Select Status",
        ["Collected at Gate", "Arrived at Mail Desk", "Parcel Collected"]
    )

    if st.button("Update Status"):
        index = df[df["tracking_number"] == tracking_number].index

        if len(index) > 0:
            student_email = df.loc[index[0], "email"]
            student_name = df.loc[index[0], "student_name"]

            df.loc[index, "status"] = new_status
            df.to_csv("parcels.csv", index=False)

            with st.spinner("Sending status update email..."):
                email_sent = send_notification_email(
                    student_email, student_name, tracking_number, new_status
                )

            if email_sent:
                st.success("✅ Status Updated! Student notified via email.")
            else:
                st.success("Status Updated! (Email notification failed)")
        else:
            st.error("Tracking Number Not Found")

    st.divider()
    st.subheader("Download Records")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="parcels.csv",
        mime="text/csv"
    )

# =====================================================
# MAIN APP ROUTER
# =====================================================
if not st.session_state.logged_in:
    show_login()
else:
    show_logout()
    if st.session_state.role == "Gate":
        gate_portal()
    elif st.session_state.role == "Student":
        student_portal()
    elif st.session_state.role == "Admin":
        admin_dashboard()