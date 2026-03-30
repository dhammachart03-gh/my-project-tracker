import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(page_title="Project Activity Tracker", layout="wide")

# --- Session State Data (จำลอง Database) ---
if 'activities' not in st.session_state:
    st.session_state.activities = []

# --- Header ---
st.title("🚀 Project: " + "Your Project Name") # แก้ไขชื่อโปรเจกต์ตรงนี้

# --- Form: Create Activity ---
with st.expander("➕ เพิ่มกิจกรรมใหม่ (Create Activity)"):
    with st.form("activity_form"):
        col1, col2 = st.columns(2)
        with col1:
            act_name = st.text_input("ชื่อกิจกรรม")
            assignee = st.text_input("ผู้รับผิดชอบ")
            deadline = st.date_input("Deadline", datetime.now())
        with col2:
            # รายชื่อกิจกรรมที่มีอยู่เดิม เพื่อกำหนด Dependency
            existing_acts = [a['name'] for a in st.session_state.activities]
            dependency = st.selectbox("ต้องทำสิ่งนี้ก่อน (Dependency)", ["None"] + existing_acts)
            follow_up = st.text_input("ผู้ที่ต้องติดตามผล (Follow-up with)")
            
        submit = st.form_submit_button("เพิ่มกิจกรรม")
        
        if submit and act_name:
            st.session_state.activities.append({
                "name": act_name,
                "assignee": assignee,
                "deadline": deadline,
                "dependency": dependency,
                "follow_up": follow_up,
                "status": "In Progress"
            })
            st.success(f"เพิ่ม '{act_name}' เรียบร้อยแล้ว!")

# --- Filtering Section ---
st.divider()
st.subheader("🔍 ตัวกรอง (Filters)")
col_f1, col_f2 = st.columns(2)

today = datetime.now().date()
end_of_week = today + timedelta(days=(6 - today.weekday()))

with col_f1:
    filter_today = st.checkbox("กิจกรรมที่ต้องทำวันนี้")
with col_f2:
    filter_week = st.checkbox("กิจกรรมที่ต้องส่งภายในสัปดาห์นี้")

# --- Data Processing & Display ---
if st.session_state.activities:
    df = pd.DataFrame(st.session_state.activities)
    
    # Apply Filters
    if filter_today:
        df = df[df['deadline'] == today]
    if filter_week:
        df = df[(df['deadline'] >= today) & (df['deadline'] <= end_of_week)]

    # Display Table
    st.subheader("📋 รายการกิจกรรม (Activity List)")
    
    # ปรับแต่งการแสดงผล Table
    formatted_df = df.copy()
    formatted_df['deadline'] = formatted_df['deadline'].apply(lambda x: x.strftime('%Y-%m-%d'))
    
    st.dataframe(
        formatted_df,
        column_config={
            "name": "Activity Name",
            "assignee": "Responsible Person",
            "deadline": "Deadline",
            "dependency": "Prerequisite (Must do first)",
            "follow_up": "Follow-up Contact",
            "status": "Current Status"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("ยังไม่มีข้อมูลกิจกรรมในขณะนี้ กรุณาเพิ่มที่ปุ่มด้านบน")
