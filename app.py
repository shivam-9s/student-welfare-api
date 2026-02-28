import streamlit as st
import requests
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="University Welfare Portal", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Campus Navigation")
role = st.sidebar.selectbox("Select your role:", ["Student", "Faculty/Staff", "DSO Admin", "Security Guard"])

st.title(f"🏫 {role} Portal")
st.divider()

# --- 1. STUDENT VIEW ---
if role == "Student":
    tab1, tab2, tab3, tab4 = st.tabs(["💡 Submit Idea", "💼 Job Search", "🎫 My Interest", "🎭 Organizations"])
    
    with tab1:
        st.subheader("Share your Idea with Management")
        with st.form("idea_form"):
            s_id = st.text_input("Your Student ID")
            title = st.text_input("Idea Title")
            desc = st.text_area("Detailed Description")
            if st.form_submit_button("Submit Idea"):
                payload = {"student_id": s_id, "title": title, "description": desc}
                res = requests.post(f"{API_URL}/ideas/submit", json=payload)
                if res.status_code == 200:
                    st.success("Your idea has been sent to the review board!")

    with tab2:
        st.subheader("Available Internal Part-Time Jobs")
        if st.button("Refresh Job Postings"):
            res = requests.get(f"{API_URL}/search/jobs")
            if res.status_code == 200:
                jobs = res.json()
                if jobs:
                    for job in jobs:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            col1.write(f"**{job['job_title']}** ({job['hours_per_week']} hrs/week)")
                            if col2.button("Apply", key=job['id']):
                                # This triggers the Time Management logic we built
                                apply_res = requests.post(f"{API_URL}/jobs/apply", 
                                                        params={"student_id": "test_user", "job_id": job['id']})
                                st.write(apply_res.json()['status'])
                else:
                    st.info("No open positions at the moment.")
    
    with tab3: # Using the Gate Pass/Profile tab
        st.subheader("My Interests & Preferences")
        # This list should match the 'interest_tags' used in recruitment drives
        available_tags = ["Sports", "Tech", "Arts", "Music", "Social Service", "Coding"]
        selected = st.multiselect("Select interests to get notified about:", available_tags)
        
        if st.button("Save Preferences"):
            res = requests.put(f"{API_URL}/students/interests", 
                            params={"student_id": "test_user_id"}, json=selected)
            if res.status_code == 200:
                st.success("Preferences saved! You will now receive matching recruitment drives.")
    
    with tab4: # New Tab: Organizations
        st.subheader("Start a Club or Event")
        choice = st.radio("What would you like to do?", ["Register New Club", "Post an Event"])
        
        if choice == "Register New Club":
            with st.form("club_reg"):
                c_name = st.text_input("Club Name")
                c_cat = st.selectbox("Category", ["Tech", "Arts", "Sports", "Literature"])
                if st.form_submit_button("Submit for Approval"):
                    requests.post(f"{API_URL}/clubs/register", 
                                params={"name": c_name, "lead_id": "test_user", "category": c_cat})
                    st.success("Registration sent to Teacher Review.")

        else:
            # Event Details View
            st.write("### Upcoming Campus Events")
            res = requests.get(f"{API_URL}/events/all")
            events = res.json().get("data", [])
            for e in events:
                with st.expander(f"📅 {e['title']} - Hosted by {e['clubs']['name']}"):
                    st.write(f"**Venue:** {e['venue']}")
                    st.write(f"**Date:** {e['event_date']}")
                    if st.button("Interested", key=f"ev_{e['id']}"):
                        st.toast("Marked as interested!")

# --- 2. FACULTY / STAFF ROLE ---
if role == "Faculty/Staff":
    st.header("👨‍🏫 Faculty Dashboard")
    
    tab_clubs, tab_courses = st.tabs(["Club Approvals", "Course Management"])

    with tab_clubs:
        st.subheader("Pending Club Recommendations")
        res = requests.get(f"{API_URL}/approvals/pending/teacher")
        pending_clubs = res.json().get("data", [])

        if not pending_clubs:
            st.success("No clubs awaiting your recommendation.")
        else:
            for club in pending_clubs:
                with st.expander(f"Review: {club['name']}"):
                    st.write(f"**Lead Student:** {club['students']['full_name']}")
                    st.write(f"**Category:** {club['category']}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Recommend to DSO", key=f"rec_{club['id']}"):
                        requests.post(f"{API_URL}/approvals/move-to-next/{club['id']}", 
                                      params={"current_user_role": "TEACHER", "action": "APPROVE"})
                        st.rerun()
                    if c2.button("❌ Reject", key=f"rej_{club['id']}", type="primary"):
                        requests.post(f"{API_URL}/approvals/move-to-next/{club['id']}", 
                                      params={"current_user_role": "TEACHER", "action": "REJECT"})
                        st.rerun()

    with tab_courses:
        st.subheader("Departmental Enrollments")
        # Logic for Course Approvals as discussed
        e_id = st.text_input("Enrollment ID")
        if st.button("Approve Student for Course"):
            requests.post(f"{API_URL}/courses/approve", params={"enrollment_id": e_id, "action": "APPROVE"})
            st.success("Enrollment confirmed.")


# --- 3. DSO ADMIN ROLE ---
elif role == "DSO Admin":
    st.header("⚖️ DSO Administrative Portal")
    
    t1, t2, t3, t4 = st.tabs(["📊 Analytics", "🏢 Final Club Approval", "💰 Price Control", "🛠️ Job Postings"])

    with t1:
        st.subheader("University Welfare Overview")
        if st.button("Refresh Report"):
            report = requests.get(f"{API_URL}/admin/registration-report").json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Clubs", report['club_stats']['total'])
            col2.metric("Active Jobs", "12") # Mocked for now
            col3.metric("Pending Tasks", report['system_health']['pending_tasks_for_faculty'])
            st.bar_chart(report['engagement']['top_interests'])

    with t2:
        st.subheader("🏢 Club Registration Pipeline")
        st.info("Monitor and manage the approval stage of all organizations.")
        
        res = requests.get(f"{API_URL}/approvals/all-clubs")
        all_clubs = res.json().get("data", [])
        
        if not all_clubs:
            st.write("No clubs registered in the system.")
        else:
            for club in all_clubs:
                with st.container(border=True):
                    col_info, col_status, col_action = st.columns([2, 1, 1])
                    
                    # 1. Club Info
                    col_info.write(f"**{club['name']}**")
                    col_info.caption(f"Lead: {club['students']['full_name']} | {club['category']}")
                    
                    # 2. Stage Visualization
                    status = club['status']
                    if status == "PENDING_TEACHER":
                        col_status.warning("🕒 Stage 1: Teacher Review")
                    elif status == "PENDING_DSO":
                        col_status.info("⏳ Stage 2: DSO Final Review")
                    elif status == "APPROVED":
                        col_status.success("✅ Stage 3: Live/Approved")
                    elif status == "REJECTED":
                        col_status.error("❌ Rejected")

                    # 3. DSO Power Actions
                    if status == "PENDING_DSO":
                        if col_action.button("Finalize Approval", key=f"fin_{club['id']}"):
                            requests.post(f"{API_URL}/approvals/move-to-next/{club['id']}", 
                                        params={"current_user_role": "DSO_ADMIN", "action": "APPROVE"})
                            st.rerun()
                    elif status == "PENDING_TEACHER":
                        if col_action.button("Bypass to DSO", key=f"bp_{club['id']}"):
                            # In real-world emergencies, DSO can bypass Teacher
                            requests.post(f"{API_URL}/approvals/move-to-next/{club['id']}", 
                                        params={"current_user_role": "TEACHER", "action": "APPROVE"})
                            st.rerun()

    with t3:
        st.subheader("Vendor Price Approval Queue")
        res = requests.get(f"{API_URL}/approvals/pending/prices")
        prices = res.json().get("data", [])
        
        for p in prices:
            st.warning(f"Item ID: {p['id']} | Requesting change to ${p['proposed_price']}")
            if st.button("Confirm Price Update", key=f"p_app_{p['id']}"):
                requests.post(f"{API_URL}/admin/approve-price/{p['id']}")
                st.rerun()

    with t4:
        st.subheader("Post New Internal Job")
        with st.form("job_form"):
            title = st.text_input("Job Title")
            hrs = st.number_input("Hours/Week", 5, 20)
            pay = st.number_input("Pay/Hour", 10.0)
            if st.form_submit_button("Launch Posting"):
                requests.post(f"{API_URL}/jobs/post", params={"title": title, "dept": "Admin", "hours": hrs, "pay": pay})
                st.success("Job live on student dashboard.")

# --- 4. SECURITY GUARD VIEW ---
elif role == "Security Guard":
    st.subheader("Gate Access Verification")
    u_id = st.text_input("Scan or Enter User/Student ID")
    loc = st.selectbox("Area for Access", ["Main Campus", "Event Hall", "Vendor Zone", "Staff Quarters"])
    
    if st.button("Verify Access"):
        # Hits the Security logic we wrote in main.py
        res = requests.get(f"{API_URL}/security/verify", params={"user_id": u_id, "location": loc})
        if res.status_code == 200:
            data = res.json()
            if data["access"] == "GRANTED":
                st.success(f"✅ ACCESS GRANTED: {data['details']['scope']}")
                st.balloons()
            else:
                st.error(f"❌ ACCESS DENIED: {data['reason']}")