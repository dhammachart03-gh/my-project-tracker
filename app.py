import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
st.set_page_config(page_title="Project & Sales Tracker", layout="wide")

# --- Google Sheets Connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # อ่านข้อมูลทั้งหมด (ใช้ ttl=0 เพื่อให้ดึงค่าใหม่ล่าสุดเสมอ ไม่ติด Cache)
        data = conn.read(ttl=0)
        # ลบแถวที่ว่างทิ้ง และแปลงทุกอย่างในคอลัมน์สำคัญเป็น String เพื่อป้องกัน Error
        data = data.dropna(how='all')
        if not data.empty:
            for col in ['project', 'name', 'assignee', 'status']:
                if col in data.columns:
                    data[col] = data[col].astype(str).replace('nan', '')
        return data
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลจาก Sheets ได้: {e}")
        return pd.DataFrame(columns=['project', 'name', 'assignee', 'deadline', 'status', 'value', 'dependency', 'follow_up', 'next_step'])

# --- Load Data ---
df = load_data()

# --- Interface ---
st.title("💼 Project Activity & Sales Tracker")

# --- Form: Create Activity ---
with st.expander("➕ เพิ่มกิจกรรมใหม่ (Add Activity to Project)", expanded=True):
    # ดึงรายชื่อโปรเจกต์ที่ไม่ซ้ำกัน และต้องไม่เป็นค่าว่าง
    if not df.empty and 'project' in df.columns:
        existing_projects = sorted([p for p in df['project'].unique() if p.strip() != ""])
    else:
        existing_projects = []
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        # แก้ไขจุดนี้: ใช้ index=0 เป็น default
        project_selection = st.selectbox(
            "เลือกโปรเจกต์ที่มีอยู่", 
            ["-- สร้างโปรเจกต์ใหม่ --"] + existing_projects,
            key="proj_select"
        )
    with col_p2:
        new_project_input = st.text_input("หรือพิมพ์ชื่อโปรเจกต์ใหม่", key="new_proj_input")

    # สรุปชื่อโปรเจกต์ที่จะใช้
    if project_selection == "-- สร้างโปรเจกต์ใหม่ --":
        final_project_name = new_project_input.strip()
    else:
        final_project_name = project_selection

    if final_project_name:
        with st.form("activity_form", clear_on_submit=True):
            st.info(f"📁 โปรเจกต์: **{final_project_name}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                act_name = st.text_input("ชื่อกิจกรรม")
                assignee = st.text_input("ผู้รับผิดชอบ")
                deadline = st.date_input("Deadline", datetime.now())
            with c2:
                status = st.selectbox("สถานะ", ["Open", "In Progress", "Waiting for Client", "Closed"])
                lead_value = st.number_input("มูลค่า (฿)", min_value=0)
                
                # กรอง Dependency เฉพาะของโปรเจกต์นี้
                rel_acts = df[df['project'] == final_project_name]['name'].unique().tolist() if not df.empty else []
                dependency = st.selectbox("Dependency (ทำต่อจาก...)", ["None"] + rel_acts)
                
            with c3:
                follow_up = st.text_input("ติดตามผลจากใคร")
                next_step = st.text_area("Next Step Action")

            submit = st.form_submit_button("บันทึกข้อมูล")

            if submit:
                if not act_name:
                    st.warning("กรุณาใส่ชื่อกิจกรรมด้วยครับ")
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
                    
                    # รวมและอัปเดต
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success("บันทึกสำเร็จ!")
                    st.rerun()
