import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(page_title="Pro-Sales Activity Tracker", layout="wide")

# --- Session State Data (Database จำลอง) ---
if 'activities' not in st.session_state:
    # เพิ่มข้อมูลตัวอย่างสำหรับงาน Sales
    st.session_state.activities = []

# --- Custom Functions ---
def get_project_list():
    if not st.session_state.activities:
        return ["General Project"]
    return list(set([a['project'] for a in st.session_state.activities]))

# --- Sidebar: Search & Navigation ---
st.sidebar.header("🔍 ค้นหาและตัวกรอง")
search_query = st.sidebar.text_input("ค้นหาชื่อกิจกรรม หรือ Project")

# Filter สำหรับงาน Sales
st.sidebar.subheader("🎯 Sales Filter")
status_filter = st.sidebar.multiselect("สถานะ", ["Open", "In Progress", "Waiting for Client", "Closed"], default=["Open", "In Progress", "Waiting for Client"])

# --- Main Interface ---
st.title("💼 Project & Sales Activity Tracker")

# --- Form: Create/Edit Activity ---
with st.expander("➕ เพิ่มกิจกรรมใหม่ หรือ ดีลงานขาย"):
    with st.form("main_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            project_name = st.text_input("Project Name (ชื่อโครงการ/ชื่อลูกค้า)")
            act_name = st.text_input("Activity (สิ่งที่ต้องทำ/ขั้นตอนการขาย)")
            assignee = st.text_input("ผู้รับผิดชอบ")
        with col2:
            deadline = st.date_input("Deadline", datetime.now())
            status = st.selectbox("Status", ["Open", "In Progress", "Waiting for Client", "Closed"])
            lead_value = st.number_input("Lead Value (มูลค่าคาดการณ์)", min_value=0, value=0)
        with col3:
            existing_acts = [a['name'] for a in st.session_state.activities]
            dependency = st.selectbox("Dependency (ทำต่อจาก...)", ["None"] + existing_acts)
            follow_up = st.text_input("ติดตามผลจากใคร (Client/Partner)")
            next_step = st.text_area("Next Step Action (แผนถัดไป)")

        submit = st.form_submit_button("บันทึกข้อมูล")
        
        if submit and act_name and project_name:
            st.session_state.activities.append({
                "id": len(st.session_state.activities),
                "project": project_name,
                "name": act_name,
                "assignee": assignee,
                "deadline": deadline,
                "status": status,
                "value": lead_value,
                "dependency": dependency,
                "follow_up": follow_up,
                "next_step": next_step
            })
            st.success(f"บันทึก '{act_name}' ในโปรเจกต์ '{project_name}' แล้ว!")

# --- Data Processing ---
if st.session_state.activities:
    df = pd.DataFrame(st.session_state.activities)
    
    # Search Logic
    if search_query:
        df = df[df['project'].str.contains(search_query, case=False) | 
                df['name'].str.contains(search_query, case=False)]
    
    # Status Filter Logic
    df = df[df['status'].isin(status_filter)]

    # --- Metrics for Sales ---
    total_value = df['value'].sum()
    st.metric("Total Pipeline Value", f"{total_value:,.2f} THB")

    # --- Display Table ---
    st.subheader("📋 รายการที่กำลังดำเนินการ")
    
    # แก้ไขชื่อ Column ให้ดูง่าย
    display_df = df.copy()
    display_df['deadline'] = display_df['deadline'].apply(lambda x: x.strftime('%Y-%m-%d'))
    
    st.dataframe(
        display_df[["project", "name", "assignee", "deadline", "status", "value", "follow_up", "next_step"]],
        column_config={
            "project": "Project/Client",
            "name": "Activity",
            "value": st.column_config.NumberColumn("Value", format="฿%d"),
            "status": "Status"
        },
        use_container_width=True,
        hide_index=True
    )

    # --- Edit Section ---
    st.divider()
    st.subheader("📝 แก้ไขสถานะกิจกรรม")
    edit_id = st.selectbox("เลือกกิจกรรมที่จะอัปเดต (ตามลำดับ)", options=df.index, format_func=lambda x: f"{df.iloc[x]['project']} - {df.iloc[x]['name']}")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        new_status = st.selectbox("ปรับสถานะใหม่", ["Open", "In Progress", "Waiting for Client", "Closed"], key="new_stat")
    with col_e2:
        if st.button("อัปเดตสถานะ"):
            st.session_state.activities[edit_id]['status'] = new_status
            st.rerun()

else:
    st.info("ยังไม่มีข้อมูลกิจกรรม เริ่มต้นโดยการเพิ่มกิจกรรมที่ปุ่มด้านบน")
