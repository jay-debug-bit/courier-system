import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="UniDrop",
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

# -------------------------
# SESSION STATE INIT
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "reg_no" not in st.session_state:
    st.session_state.reg_no = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------------------
# CREATE CSV FILES IF NOT EXISTS
# -------------------------
if not os.path.exists("parcels.csv"):
    pd.DataFrame(columns=[
        "student_name", "reg_no", "email",
        "hostel", "courier_company", "tracking_number", "status"
    ]).to_csv("parcels.csv", index=False)

if not os.path.exists("students.csv"):
    pd.DataFrame(columns=[
        "student_name", "reg_no", "email", "hostel", "password"
    ]).to_csv("students.csv", index=False)

# -------------------------
# EMAIL FUNCTION
# -------------------------
def send_notification_email(to_email, student_name, tracking_number, status="Not Arrived Yet"):
    SENDER_EMAIL = "mucouriers@gmail.com"
    SENDER_PASSWORD = "yzdc gwdl txuo yeic"

    msg = EmailMessage()
    msg['Subject'] = f"📦 UniDrop: Parcel Update - {status}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    content = f"""
Dear {student_name},

Your parcel status has been updated in UniDrop.

Tracking Number: {tracking_number}
Current Status: {status}

Thank you for using UniDrop.

Regards,
UniDrop
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
# LOGOUT BUTTON
# -------------------------
def show_logout():
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.role}")
        if st.session_state.reg_no:
            st.markdown(f"**Reg No:** {st.session_state.reg_no}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.reg_no = None
            st.session_state.page = "login"
            st.rerun()

# -------------------------
# REGISTER PAGE
# -------------------------
def show_register():
    st.markdown("<h2 style='text-align:center'>📦 UniDrop</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray'>Create a Student Account</p>", unsafe_allow_html=True)
    st.markdown("---")

    name = st.text_input("Full Name", key="reg_name")
    reg_no = st.text_input("Registration Number", key="reg_reg_no")
    email = st.text_input("Personal Email", key="reg_email")
    hostel = st.selectbox("Hostel", ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"], key="reg_hostel")
    pwd = st.text_input("Create Password", type="password", key="reg_pwd")
    confirm_pwd = st.text_input("Confirm Password", type="password", key="reg_confirm_pwd")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Register", use_container_width=True, key="reg_btn"):
            if not all([name, reg_no, email, pwd, confirm_pwd]):
                st.warning("Please fill all fields.")
            elif pwd != confirm_pwd:
                st.error("❌ Passwords do not match.")
            else:
                students_df = pd.read_csv("students.csv")
                if reg_no in students_df["reg_no"].astype(str).values:
                    st.error("❌ This Registration Number is already registered.")
                else:
                    new_student = {
                        "student_name": name,
                        "reg_no": reg_no,
                        "email": email,
                        "hostel": hostel,
                        "password": pwd
                    }
                    students_df = pd.concat(
                        [students_df, pd.DataFrame([new_student])],
                        ignore_index=True
                    )
                    students_df.to_csv("students.csv", index=False)
                    st.success("✅ Account created! You can now log in.")
                    st.session_state.page = "login"
                    st.rerun()

    with col2:
        if st.button("← Back to Login", use_container_width=True, key="back_login"):
            st.session_state.page = "login"
            st.rerun()

# -------------------------
# LOGIN PAGE
# -------------------------
def show_login():
    st.markdown("<h2 style='text-align:center'>📦 UniDrop</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray'>Campus Parcel Management</p>", unsafe_allow_html=True)
    st.markdown("---")

    role = st.selectbox("Login As", ["Student", "Gate Staff", "Admin"], key="login_role")

    if role == "Student":
        reg = st.text_input("Registration Number", key="login_student_reg")
        pwd = st.text_input("Password", type="password", key="login_student_pwd")

        if st.button("Login", use_container_width=True, key="login_student_btn"):
            students_df = pd.read_csv("students.csv")
            match = students_df[
                (students_df["reg_no"].astype(str) == reg) &
                (students_df["password"].astype(str) == pwd)
            ]
            if len(match) > 0:
                st.session_state.logged_in = True
                st.session_state.role = "Student"
                st.session_state.reg_no = reg
                st.rerun()
            else:
                st.error("❌ Invalid Registration Number or Password.")

        st.markdown("---")
        st.markdown("<p style='text-align:center'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("📝 Register as Student", use_container_width=True, key="reg_page_btn"):
            st.session_state.page = "register"
            st.rerun()

    elif role == "Gate Staff":
        username = st.text_input("Username", key="login_gate_user")
        pwd = st.text_input("Password", type="password", key="login_gate_pwd")

        if st.button("Login", use_container_width=True, key="login_gate_btn"):
            if username == GATE_USERNAME and pwd == GATE_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.role = "Gate"
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    elif role == "Admin":
        username = st.text_input("Username", key="login_admin_user")
        pwd = st.text_input("Password", type="password", key="login_admin_pwd")

        if st.button("Login", use_container_width=True, key="login_admin_btn"):
            if username == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

# =====================================================
# GATE PORTAL
# =====================================================
def gate_portal():
    st.header("🚪 Gate Portal")

    student = st.text_input("Student Name", key="gate_name")
    reg_no = st.text_input("Registration Number", key="gate_reg")
    email = st.text_input("Personal Email", key="gate_email")
    hostel = st.selectbox("Hostel", ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"], key="gate_hostel")
    courier = st.text_input("Courier Company", key="gate_courier")
    tracking = st.text_input("Tracking Number", key="gate_tracking")

    if st.button("Register Parcel", key="gate_register_btn"):
        if student and reg_no and email and courier and tracking:
            parcel = {
                "student_name": student,
                "reg_no": reg_no,
                "email": email,
                "hostel": hostel,
                "courier_company": courier,
                "tracking_number": tracking,
                "status": "Not Arrived Yet"
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
    st.header("🎓 My Parcels")

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
                    "Not Arrived Yet": 0,
                    "Collected at Gate": 25,
                    "Arrived at Mail Desk": 65,
                    "Parcel Collected": 100
                }
                st.progress(progress.get(parcel["status"], 0))
                st.divider()
    else:
        st.info("📭 No parcels found for your account yet.")

# =====================================================
# ADMIN DASHBOARD
# =====================================================
def admin_dashboard():
    st.header("📊 Admin Dashboard")

    df = pd.read_csv("parcels.csv")
    total = len(df)
    not_arrived = len(df[df["status"] == "Not Arrived Yet"])
    gate_count = len(df[df["status"] == "Collected at Gate"])
    maildesk_count = len(df[df["status"] == "Arrived at Mail Desk"])
    collected_count = len(df[df["status"] == "Parcel Collected"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Parcels", total)
    col2.metric("Not Arrived", not_arrived)
    col3.metric("At Gate", gate_count)
    col4.metric("At Mail Desk", maildesk_count)
    col5.metric("Collected", collected_count)

    st.divider()
    st.subheader("All Parcels")
    keyword = st.text_input("Search by Registration Number", key="admin_search")
    filtered_df = df

    if keyword:
        filtered_df = df[
            df["reg_no"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)

    st.divider()
    st.subheader("Update Parcel Status")
    tracking_number = st.text_input("Tracking Number", key="admin_tracking")
    new_status = st.selectbox(
        "Select Status",
        ["Not Arrived Yet", "Collected at Gate", "Arrived at Mail Desk", "Parcel Collected"],
        key="admin_status"
    )

    if st.button("Update Status", key="admin_update_btn"):
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
    st.subheader("Registered Students")
    students_df = pd.read_csv("students.csv")
    st.dataframe(students_df[["student_name", "reg_no", "email", "hostel"]], use_container_width=True)

    st.divider()
    st.subheader("Download Records")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Parcels CSV",
        data=csv,
        file_name="parcels.csv",
        mime="text/csv"
    )

# =====================================================
# MAIN APP ROUTER
# =====================================================
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        show_register()
    else:
        show_login()
else:
    show_logout()
    if st.session_state.role == "Gate":
        gate_portal()
    elif st.session_state.role == "Student":
        student_portal()
    elif st.session_state.role == "Admin":
        admin_dashboard()