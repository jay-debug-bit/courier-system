import streamlit as st
import pandas as pd
import os
import smtplib
import random
import plotly.express as px
from email.message import EmailMessage
from datetime import datetime, time

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="UniDrop",
    page_icon="assets/logo.png",
    layout="wide"
)

# -------------------------
# CUSTOM CSS - UniDrop Brand Colors (Brown #5C3D2E)
# -------------------------
st.markdown("""
<style>
    /* Brand color: brown #5C3D2E */
    .stButton > button {
        background-color: #5C3D2E;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #7a5240;
        color: white;
    }
    .stSelectbox label, .stTextInput label {
        font-weight: 500;
    }
    .brand-header {
        text-align: center;
        color: #5C3D2E;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .brand-sub {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-top: 0;
    }
    .sidebar-brand {
        color: #5C3D2E;
        font-weight: 700;
        font-size: 1.1rem;
    }
    /* Remove white box from sidebar logo */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        background-color: transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        mix-blend-mode: lighten;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
if "otp_store" not in st.session_state:
    st.session_state.otp_store = {}   # tracking_number -> otp

# -------------------------
# CREATE CSV FILES IF NOT EXISTS
# -------------------------
if not os.path.exists("parcels.csv"):
    pd.DataFrame(columns=[
        "student_name", "reg_no", "email",
        "hostel", "courier_company", "tracking_number",
        "status", "pickup_slot", "registered_on"
    ]).to_csv("parcels.csv", index=False)

if not os.path.exists("students.csv"):
    pd.DataFrame(columns=[
        "student_name", "reg_no", "email", "hostel", "password"
    ]).to_csv("students.csv", index=False)

# -------------------------
# LOGO HELPER
# -------------------------
def show_logo(width=180):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width="stretch")
        else:
            st.markdown("<p class='brand-header'>UniDrop</p>", unsafe_allow_html=True)

# -------------------------
# EMAIL FUNCTION
# -------------------------
def send_notification_email(to_email, student_name, tracking_number, status="Not Arrived Yet", otp=None):
    SENDER_EMAIL = "mucouriers@gmail.com"
    SENDER_PASSWORD = "yzdc gwdl txuo yeic"

    msg = EmailMessage()
    msg['Subject'] = f"📦 UniDrop: Parcel Update - {status}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    otp_section = f"\n🔐 Your Collection OTP: {otp}\nPlease show this OTP at the mail desk to collect your parcel.\n" if otp else ""

    content = f"""
Dear {student_name},

Your parcel status has been updated in the UniDrop system.

Tracking Number: {tracking_number}
Current Status:  {status}
{otp_section}
Thank you for using UniDrop.

Regards,
UniDrop Team
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
# GENERATE OTP
# -------------------------
def generate_otp():
    return str(random.randint(100000, 999999))

# -------------------------
# LOGOUT BUTTON
# -------------------------
def show_logout():
    with st.sidebar:
        if os.path.exists("assets/logo.png"):
            import base64
            with open("assets/logo.png", "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div style="display:flex; justify-content:center; padding: 8px 0 4px 0;">
                    <img src="data:image/png;base64,{logo_b64}"
                         style="width:130px; background:transparent; mix-blend-mode:lighten;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown("<span class='sidebar-brand'>UniDrop</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**Role:** {st.session_state.role}")
        if st.session_state.reg_no:
            st.markdown(f"**Reg No:** {st.session_state.reg_no}")
        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.reg_no = None
            st.session_state.page = "login"
            st.session_state.otp_store = {}
            st.rerun()

# -------------------------
# REGISTER PAGE
# -------------------------
def show_register():
    _, center, _ = st.columns([1, 2, 1])
    with center:
        show_logo()
        st.markdown("<p class='brand-sub'>Create a Student Account</p>", unsafe_allow_html=True)
        st.markdown("---")

        name = st.text_input("Full Name")
        reg_no = st.text_input("Registration Number")
        email = st.text_input("Personal Email")
        hostel = st.selectbox("Hostel", ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"])
        pwd = st.text_input("Create Password", type="password")
        confirm_pwd = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Register", width="stretch"):
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
            if st.button("← Back to Login", width="stretch"):
                st.session_state.page = "login"
                st.rerun()

# -------------------------
# LOGIN PAGE
# -------------------------
def show_login():
    _, center, _ = st.columns([1, 2, 1])
    with center:
        show_logo()
        st.markdown("<p class='brand-sub'>Campus Courier Management System</p>", unsafe_allow_html=True)
        st.markdown("---")

        role = st.selectbox("Login As", ["Student", "Gate Staff", "Admin"])

        if role == "Student":
            reg = st.text_input("Registration Number")
            pwd = st.text_input("Password", type="password")

            if st.button("Login", width="stretch"):
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
            if st.button("📝 Register as Student", width="stretch"):
                st.session_state.page = "register"
                st.rerun()

        elif role == "Gate Staff":
            username = st.text_input("Username")
            pwd = st.text_input("Password", type="password")

            if st.button("Login", width="stretch"):
                if username == GATE_USERNAME and pwd == GATE_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "Gate"
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")

        elif role == "Admin":
            username = st.text_input("Username")
            pwd = st.text_input("Password", type="password")

            if st.button("Login", width="stretch"):
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
    st.markdown("## 🚪 Gate Portal")
    st.markdown("Register incoming parcels and notify students.")
    st.markdown("---")

    with st.form("gate_form"):
        st.subheader("New Parcel Entry")
        col1, col2 = st.columns(2)

        with col1:
            student = st.text_input("Student Name")
            reg_no = st.text_input("Registration Number")
            email = st.text_input("Student Email")

        with col2:
            hostel = st.selectbox("Hostel", ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"])
            courier = st.text_input("Courier Company")
            tracking = st.text_input("Tracking Number")

        submitted = st.form_submit_button("📦 Register Parcel", width="stretch")

    if submitted:
        if student and reg_no and email and courier and tracking:
            parcel = {
                "student_name": student,
                "reg_no": reg_no,
                "email": email,
                "hostel": hostel,
                "courier_company": courier,
                "tracking_number": tracking,
                "status": "Not Arrived Yet",
                "pickup_slot": "",
                "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            df = pd.read_csv("parcels.csv")
            df = pd.concat([df, pd.DataFrame([parcel])], ignore_index=True)
            df.to_csv("parcels.csv", index=False)

            with st.spinner("Sending email notification..."):
                email_sent = send_notification_email(email, student, tracking)

            if email_sent:
                st.success("✅ Parcel registered! Email notification sent to student.")
            else:
                st.warning("Parcel registered, but email failed to send.")
        else:
            st.warning("Please fill all fields.")

    st.markdown("---")
    st.subheader("📋 Today's Registered Parcels")
    df = pd.read_csv("parcels.csv")
    today = datetime.now().strftime("%Y-%m-%d")
    if "registered_on" in df.columns:
        today_df = df[df["registered_on"].astype(str).str.startswith(today)]
        st.dataframe(today_df[["student_name", "reg_no", "courier_company", "tracking_number", "hostel", "status"]], width="stretch")
    else:
        st.dataframe(df[["student_name", "reg_no", "courier_company", "tracking_number", "hostel", "status"]], width="stretch")

# =====================================================
# STUDENT PORTAL
# =====================================================
def student_portal():
    st.markdown("## 🎓 My Parcels")

    reg_no = st.session_state.reg_no
    df = pd.read_csv("parcels.csv")
    result = df[df["reg_no"].astype(str).str.strip() == reg_no.strip()]

    if len(result) > 0:
        st.success(f"Found {len(result)} parcel(s) for your account.")

        # --- Pickup Slot Booking ---
        available_slots = [
            "6:00 PM - 6:30 PM",
            "6:30 PM - 7:00 PM",
            "7:00 PM - 7:30 PM",
            "7:30 PM - 8:00 PM",
            "8:00 PM - 8:30 PM",
        ]

        for index, parcel in result.iterrows():
            with st.expander(f"📦 {parcel['courier_company']} — {parcel['tracking_number']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Student:** {parcel['student_name']}")
                    st.write(f"**Hostel:** {parcel['hostel']}")
                    st.write(f"**Status:** {parcel['status']}")
                    if parcel.get("registered_on"):
                        st.write(f"**Registered On:** {parcel['registered_on']}")

                with col2:
                    current_slot = parcel.get("pickup_slot", "")
                    if current_slot:
                        st.info(f"🕐 Pickup Slot: **{current_slot}**")
                    else:
                        st.warning("No pickup slot booked yet.")

                progress_map = {
                    "Not Arrived Yet": 0,
                    "Collected at Gate": 25,
                    "Arrived at Mail Desk": 65,
                    "Parcel Collected": 100
                }
                st.progress(progress_map.get(parcel["status"], 0))

                # Slot Booking
                if parcel["status"] not in ["Parcel Collected"]:
                    st.markdown("**📅 Book / Change Pickup Slot**")
                    slot_key = f"slot_{index}"
                    selected_slot = st.selectbox(
                        "Choose a slot (after academic hours):",
                        available_slots,
                        key=slot_key
                    )
                    if st.button(f"Confirm Slot", key=f"confirm_{index}"):
                        df.loc[index, "pickup_slot"] = selected_slot
                        df.to_csv("parcels.csv", index=False)
                        st.success(f"✅ Pickup slot booked: {selected_slot}")
                        st.rerun()

                st.divider()
    else:
        st.info("📭 No parcels found for your account yet.")

# =====================================================
# ADMIN DASHBOARD
# =====================================================
def admin_dashboard():
    st.markdown("## 📊 Admin Dashboard")

    df = pd.read_csv("parcels.csv")

    # --- Metrics ---
    total = len(df)
    not_arrived    = len(df[df["status"] == "Not Arrived Yet"])
    gate_count     = len(df[df["status"] == "Collected at Gate"])
    maildesk_count = len(df[df["status"] == "Arrived at Mail Desk"])
    collected_count= len(df[df["status"] == "Parcel Collected"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Total",       total)
    col2.metric("⏳ Not Arrived", not_arrived)
    col3.metric("🚪 At Gate",     gate_count)
    col4.metric("📬 Mail Desk",   maildesk_count)
    col5.metric("✅ Collected",   collected_count)

    st.markdown("---")

    # --- Analytics Charts ---
    st.subheader("📈 Analytics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig1 = px.pie(
            status_counts, names="Status", values="Count",
            title="Parcel Status Distribution",
            color_discrete_sequence=["#5C3D2E", "#7a5240", "#a0714f", "#c8a882", "#e8d5b7"]
        )
        st.plotly_chart(fig1, width="stretch")

    with chart_col2:
        if "hostel" in df.columns and len(df) > 0:
            hostel_counts = df["hostel"].value_counts().reset_index()
            hostel_counts.columns = ["Hostel", "Count"]
            fig2 = px.bar(
                hostel_counts, x="Hostel", y="Count",
                title="Parcels by Hostel",
                color_discrete_sequence=["#5C3D2E"]
            )
            st.plotly_chart(fig2, width="stretch")

    if "registered_on" in df.columns and df["registered_on"].notna().any():
        df["date"] = pd.to_datetime(df["registered_on"], errors="coerce").dt.date
        daily = df.groupby("date").size().reset_index(name="Parcels")
        fig3 = px.line(
            daily, x="date", y="Parcels",
            title="Daily Parcel Registrations",
            markers=True,
            color_discrete_sequence=["#5C3D2E"]
        )
        st.plotly_chart(fig3, width="stretch")

    st.markdown("---")

    # --- All Parcels Table ---
    st.subheader("📋 All Parcels")
    keyword = st.text_input("🔍 Search by Registration Number or Name")
    filtered_df = df

    if keyword:
        filtered_df = df[
            df["reg_no"].astype(str).str.contains(keyword, case=False, na=False) |
            df["student_name"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    st.dataframe(filtered_df, width="stretch")

    st.markdown("---")

    # --- DELETE PARCEL RECORD FEATURE ---
    st.subheader("🗑️ Delete Parcel Record")
    st.caption("Permanently remove a parcel record from the system by Tracking Number.")
    
    del_tracking = st.text_input("Tracking Number to Delete", key="delete_track_input")
    
    if st.button("🗑️ Delete Record", width="stretch"):
        if del_tracking:
            df_del = pd.read_csv("parcels.csv")
            idx = df_del[df_del["tracking_number"].astype(str) == del_tracking].index
            
            if len(idx) > 0:
                df_del = df_del.drop(idx)
                df_del.to_csv("parcels.csv", index=False)
                
                # Clean up OTP store if it exists for this tracking number
                if del_tracking in st.session_state.otp_store:
                    del st.session_state.otp_store[del_tracking]
                    
                st.success(f"✅ Record for tracking number **{del_tracking}** deleted successfully.")
                st.rerun()
            else:
                st.error("❌ Tracking Number not found.")
        else:
            st.warning("Please enter a tracking number.")

    st.markdown("---")

    # --- Update Parcel Status + OTP ---
    st.subheader("🔄 Update Parcel Status")

    col_a, col_b = st.columns(2)
    with col_a:
        tracking_number = st.text_input("Tracking Number")
    with col_b:
        new_status = st.selectbox(
            "Select New Status",
            ["Not Arrived Yet", "Collected at Gate", "Arrived at Mail Desk", "Parcel Collected"]
        )

    if st.button("Update Status", width="stretch"):
        index = df[df["tracking_number"].astype(str) == tracking_number].index

        if len(index) > 0:
            student_email = df.loc[index[0], "email"]
            student_name  = df.loc[index[0], "student_name"]

            df.loc[index, "status"] = new_status
            df.to_csv("parcels.csv", index=False)

            otp = None
            # Generate OTP when parcel is ready to collect
            if new_status == "Arrived at Mail Desk":
                otp = generate_otp()
                st.session_state.otp_store[tracking_number] = otp
                st.info(f"🔐 OTP generated for **{tracking_number}**: `{otp}` (also sent to student via email)")

            with st.spinner("Sending status update email..."):
                email_sent = send_notification_email(
                    student_email, student_name, tracking_number, new_status, otp
                )

            if email_sent:
                st.success("✅ Status updated! Student notified via email.")
            else:
                st.success("Status updated! (Email notification failed)")
        else:
            st.error("❌ Tracking Number not found.")

    st.markdown("---")

    # --- OTP Verification ---
    st.subheader("🔐 OTP Verification for Collection")
    st.caption("Verify student OTP before handing over the parcel.")

    otp_col1, otp_col2 = st.columns(2)
    with otp_col1:
        verify_tracking = st.text_input("Tracking Number for Verification")
    with otp_col2:
        entered_otp = st.text_input("Enter OTP from Student")

    if st.button("✅ Verify OTP & Mark Collected", width="stretch"):
        stored_otp = st.session_state.otp_store.get(verify_tracking)
        if not stored_otp:
            st.error("❌ No OTP found for this tracking number. Please update status to 'Arrived at Mail Desk' first.")
        elif entered_otp.strip() == stored_otp:
            # Mark as collected
            idx = df[df["tracking_number"].astype(str) == verify_tracking].index
            if len(idx) > 0:
                df.loc[idx, "status"] = "Parcel Collected"
                df.to_csv("parcels.csv", index=False)
                del st.session_state.otp_store[verify_tracking]

                student_email = df.loc[idx[0], "email"]
                student_name  = df.loc[idx[0], "student_name"]
                send_notification_email(student_email, student_name, verify_tracking, "Parcel Collected")
                st.success("✅ OTP verified! Parcel marked as Collected and student notified.")
            else:
                st.error("❌ Tracking number not found.")
        else:
            st.error("❌ Incorrect OTP. Please try again.")

    st.markdown("---")

    # --- Registered Students ---
    st.subheader("👥 Registered Students")
    students_df = pd.read_csv("students.csv")
    st.dataframe(
        students_df[["student_name", "reg_no", "email", "hostel"]],
        width="stretch"
    )

    st.markdown("---")

    # --- Download ---
    st.subheader("📥 Download Records")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Parcels CSV",
        data=csv,
        file_name="unidrop_parcels.csv",
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