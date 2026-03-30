import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
st.set_page_config(page_title="Project & Sales Tracker", layout="wide")

# --- Google Sheets Connection ---
# ก๊อปปี้ URL จาก Google Sheet ที่แชร์แบบ Editor มาวางที่นี่
gsheet_url = "https://docs.google.com/spreadsheets/d/1B1JT3yRh1R1u2fGSYBCSWR3jrDqU8QoEmNA9lzQGlXs/edit?gid=0#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ดึงข้อมูล 9 คอลัมน์หลัก
        data = conn.read(spreadsheet=gsheet_url, usecols=list(range(9)))
        return data.dropna(how='all') # ลบแถวที่ว่างทั้งหมดออก
    except:
        return pd.DataFrame(columns=['project', 'name', 'assignee', 'deadline', 'status', 'value', 'dependency', 'follow_up', 'next_step'])

# --- Load Initial Data ---
df = load_data()

# --- Interface ---
st.title("💼 Project Activity & Sales Tracker")

# --- Form: Create Activity ---
with st.expander("➕ เพิ่มกิจกรรมใหม่ (Add Activity to Project)"):
    # 1. ส่วนการเลือก Project (มีอยู่แล้วหรือสร้างใหม่)
    existing_projects = sorted(df['project'].unique().tolist()) if not df.empty else []
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        project_selection = st.selectbox("เลือกโปรเจกต์ที่มีอยู่", ["-- สร้างโปรเจกต์ใหม่ --"] + existing_projects)
    with col_p2:
        new_project_name = st.text_input("หรือพิมพ์ชื่อโปรเจกต์ใหม่")

    final_project_name = new_project_name if project_selection == "-- สร้างโปรเจกต์ใหม่ --" else project_selection

    # 2. ส่วนการกรอกรายละเอียด Activity
    if final_project_name:
        with st.form("activity_form"):
            st.info(f"กำลังเพิ่มกิจกรรมให้โปรเจกต์: **{final_project_name}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                act_name = st.text_input("ชื่อกิจกรรม (Activity Name)")
                assignee = st.text_input("ผู้รับผิดชอบ")
                deadline = st.date_input("Deadline", datetime.now())
            with c2:
                status = st.selectbox("สถานะปัจจุบัน", ["Open", "In Progress", "Waiting for Client", "Closed"])
                lead_value = st.number_input("มูลค่า (Lead Value)", min_value=0, step=1000)
                
                # Logic: ดึงเฉพาะ Activity ของโปรเจกต์เดียวกันมาทำ Dependency
                relevant_activities = df[df['project'] == final_project_name]['name'].unique().tolist()
                dependency = st.selectbox("ต้องทำสิ่งนี้ก่อน (Dependency)", ["None"] + relevant_activities)
                
            with c3:
                follow_up = st.text_input("ต้องติดตามผลจากใคร")
                next_step = st.text_area("Next Step Action")

            submit = st.form_submit_button("บันทึกกิจกรรม")

            if submit:
                if not act_name:
                    st.error("กรุณาระบุชื่อกิจกรรม")
                else:
                    new_row = pd.DataFrame([{
                        "project": final_project_name,
                        "name": act_name,
                        "assignee": assignee,
                        "deadline": deadline.strftime('%Y-%m-%d'),
                        "status": status,
                        "value": lead_value,
                        "dependency": dependency,
                        "follow_up": follow_up,
                        "next_step": next_step
                    }])
                    
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(spreadsheet=https://docs.google.com/spreadsheets/d/1B1JT3yRh1R1u2fGSYBCSWR3jrDqU8QoEmNA9lzQGlXs/edit?gid=0#gid=0, data=updated_df)
                    st.success(f"บันทึกกิจกรรม '{act_name}' เรียบร้อยแล้ว!")
                    st.rerun()
    else:
        st.warning("กรุณาเลือกหรือระบุชื่อโปรเจกต์ก่อนเริ่ม")

# --- Search & Filter Section ---
st.divider()
st.subheader("🔍 ค้นหาและติดตามผล")

col_f1, col_f2 = st.columns(2)
with col_f1:
    search_project = st.multiselect("กรองตามชื่อโปรเจกต์", options=existing_projects)
with col_f2:
    search_text = st.text_input("ค้นหาจากชื่อกิจกรรม/ผู้รับผิดชอบ")

# Apply Filters
filtered_df = df.copy()
if search_project:
    filtered_df = filtered_df[filtered_df['project'].isin(search_project)]
if search_text:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_text, case=False, na=False) | 
                              filtered_df['assignee'].str.contains(search_text, case=False, na=False)]

# --- Display Result ---
if not filtered_df.empty:
    # คำนวณยอดเงินรวม (Sales Pipeline)
    total_pipeline = pd.to_numeric(filtered_df['value']).sum()
    st.metric("Total Filtered Value", f"฿{total_pipeline:,.2f}")
    
    # แสดงตารางแบบจัดกลุ่มตามโปรเจกต์
    st.dataframe(
        filtered_df.sort_values(by=['project', 'deadline']),
        column_config={
            "project": "Project Name",
            "name": "Activity",
            "value": st.column_config.NumberColumn("Value (฿)", format="%d"),
            "dependency": "Must do first"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("ไม่พบข้อมูลที่ตรงตามเงื่อนไข")
