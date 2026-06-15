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

st.title("📦 MU Couriers")
st.write("Campus Courier Management System")

# -------------------------
# CREATE CSV IF NOT EXISTS
# -------------------------
if not os.path.exists("parcels.csv"):
    df = pd.DataFrame(
        columns=[
            "student_name",
            "reg_no",
            "email",
            "hostel",
            "courier_company",
            "tracking_number",
            "status"
        ]
    )
    df.to_csv("parcels.csv", index=False)

# -------------------------
# OUTLOOK EMAIL NOTIFICATION FUNCTION
# -------------------------
def send_notification_email(to_email, student_name, tracking_number, status="Collected at Gate"):
    # --- YOUR OUTLOOK CREDENTIALS ---
    SENDER_EMAIL = "sm25ubbd198@mahindrauniversity.edu.in" 
    SENDER_PASSWORD = "Jay@3121" 
    # --------------------------------

    msg = EmailMessage()
    msg['Subject'] = f"MU Couriers: {status}"
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
        # Microsoft 365 / Outlook SMTP Server details
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls() # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
portal = st.sidebar.selectbox(
    "Select Portal",
    [
        "Student Portal",
        "Gate Portal",
        "Admin Dashboard"
    ]
)

# =====================================================
# GATE PORTAL
# =====================================================
if portal == "Gate Portal":
    st.header("🚪 Gate Portal")

    student = st.text_input("Student Name")
    reg_no = st.text_input("Registration Number")
    email = st.text_input("Student Email")
    hostel = st.selectbox(
        "Hostel",
        ["Phase 1", "Phase 2", "Phase 3", "Phase 4A", "Phase 4B"]
    )
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

            # --- TRIGGER EMAIL NOTIFICATION ---
            with st.spinner("Sending email notification..."):
                email_sent = send_notification_email(email, student, tracking)
            
            if email_sent:
                st.success("Parcel Registered Successfully! 📧 Notification email sent to student.")
            else:
                st.warning("Parcel Registered, but failed to send email. (Check password or IT settings).")
            # ----------------------------------

        else:
            st.warning("Please fill all fields.")

# =====================================================
# STUDENT PORTAL
# =====================================================
elif portal == "Student Portal":
    st.header("🎓 Student Portal")

    search = st.text_input("Enter Registration Number")

    if st.button("Track Parcel"):
        df = pd.read_csv("parcels.csv")
        
        # Find all parcels for this registration number
        result = df[
            df["reg_no"]
            .astype(str)
            .str.strip()
            == search.strip()
        ]

        if len(result) > 0:
            st.success(f"Found {len(result)} parcel(s) for Registration No: {search}")
            
            # Loop through all parcels to show them cleanly
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
            st.error("No parcels found for this Registration Number.")

# =====================================================
# ADMIN DASHBOARD
# =====================================================
elif portal == "Admin Dashboard":
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
            df["reg_no"]
            .astype(str)
            .str.contains(keyword, case=False, na=False)
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
            # Get student details before updating
            student_email = df.loc[index[0], "email"]
            student_name = df.loc[index[0], "student_name"]
            
            # Update status in CSV
            df.loc[index, "status"] = new_status
            df.to_csv("parcels.csv", index=False)
            
            # --- TRIGGER EMAIL NOTIFICATION FOR STATUS CHANGE ---
            with st.spinner("Sending status update email..."):
                email_sent = send_notification_email(student_email, student_name, tracking_number, new_status)
            
            if email_sent:
                st.success("Status Updated Successfully! 📧 Student notified via email.")
            else:
                st.success("Status Updated Successfully! (Email notification failed)")
            # ----------------------------------------------------
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