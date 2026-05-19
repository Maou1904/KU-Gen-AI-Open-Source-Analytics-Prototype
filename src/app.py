import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------
# STEP 0: ตั้งค่าหน้าเว็บเริ่มต้น (ต้องอยู่บรรทัดแรกสุดของ Streamlit เสมอ)
# -------------------------------------------------------------
st.set_page_config(
    page_title="KU Gen AI - Open Source Analytics Prototype",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# STEP 1: โหลดข้อมูลที่ผ่านการประมวลผลแล้ว
# -------------------------------------------------------------
@st.cache_data
def load_processed_data():
    # ดึงไฟล์ที่มาจากการรัน pipeline ล่าสุดของคุณ
    df = pd.read_csv("data/processed_analytics_data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

df = load_processed_data()

# -------------------------------------------------------------
# STEP 2: ตัวกรองข้อมูลแถบข้าง (Sidebar Filters) -> ตรงตามข้อกำหนด Optional
# -------------------------------------------------------------
st.sidebar.title("🔍 ตัวกรองระบบ (Filters)")

# 2.1 ตัวกรองวิทยาเขต (Campus)
campuses = ["All"] + list(df['Campus'].unique())
selected_campus = st.sidebar.selectbox("วิทยาเขต", options=campuses)

# 2.2 ตัวกรองคณะ (Faculty)
faculties = ["All"] + list(df['Faculty'].unique())
selected_faculty = st.sidebar.selectbox("คณะ", options=faculties)

# 2.3 ตัวกรองระดับการศึกษา (Education Level)
edu_levels = ["All"] + [level for level in df['EducationLevel'].unique()]
selected_edu = st.sidebar.selectbox("ระดับการศึกษา", options=edu_levels)

# ลอจิกการกรองข้อมูลแบบ Dynamic ผูกสัมพันธ์ตามปุ่มที่เลือก
filtered_df = df.copy()
if selected_campus != "All":
    filtered_df = filtered_df[filtered_df['Campus'] == selected_campus]
if selected_faculty != "All":
    filtered_df = filtered_df[filtered_df['Faculty'] == selected_faculty]
if selected_edu != "All":
    filtered_df = filtered_df[filtered_df['EducationLevel'] == selected_edu]

# แยกตารางสำหรับเอาไปคิดค่าสถิติฝั่ง Usage และ Top-up เหมือนใน pipeline ของคุณ
usage_df = filtered_df[filtered_df["TransactionType"] == "Usage"]

# -------------------------------------------------------------
# STEP 3: ส่วนหัวแดชบอร์ดและ Metric Cards (สรุปตัวเลขสำคัญ)
# -------------------------------------------------------------
st.title("🎓 KU Gen AI - Open Source Analytics Prototype")
st.caption("ระบบต้นแบบรายงานผลสถิติและพฤติกรรมการใช้งานโมเดลปัญญาประดิษฐ์ในมหาวิทยาลัย")
st.markdown("---")

# แบ่งพื้นที่แสดงการ์ดสรุปตัวเลข 4 กล่องสี่เหลี่ยมเรียงหน้ากระดาน
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.metric(label="จำนวนผู้ใช้งานที่ไม่ซ้ำ (Unique Users)", value=filtered_df['UserID'].nunique())
with m_col2:
    total_tokens = usage_df['TokenUsed'].sum() if not usage_df.empty else 0
    st.metric(label="ปริมาณ Token ที่ใช้รวม", value=f"{total_tokens:,}")
with m_col3:
    avg_proc = usage_df['ProcessingTime'].mean() if not usage_df.empty else 0.0
    st.metric(label="เวลาประมวลผลเฉลี่ย (วินาที)", value=f"{avg_proc:.2f} s")
with m_col4:
    # คำนวณหา Success Rate แบบสดๆ ตามข้อมูลที่กรอง
    success_count = len(filtered_df[filtered_df['Status'] == 'Success'])
    success_rate = (success_count / len(filtered_df)) if len(filtered_df) > 0 else 0.0
    st.metric(label="อัตราความสำเร็จของระบบ", value=f"{success_rate:.2%}")

st.markdown("---")

# -------------------------------------------------------------
# STEP 4: การจัดวางและวาดกราฟ (ความต้องการบังคับ: กราฟไม่น้อยกว่า 4 ประเภท)
# -------------------------------------------------------------
# แถวกราฟที่ 1: วิเคราะห์แนวโน้มกับความรู้สึก
chart_row1_col1, chart_row1_col2 = st.columns(2)

with chart_row1_col1:
    st.write("### 📈 แนวโน้มกิจกรรมการใช้งาน (Line Chart)")
    # TODO: สรุปข้อมูลรายวันจาก filtered_df แล้วใช้ px.line() พลอตกราฟเส้น
    # ตัวอย่าง: daily_data = filtered_df.groupby(filtered_df['Timestamp'].dt.date).size().reset_index(name='Count')
    # fig_line = px.line(daily_data, x='Timestamp', y='Count', labels={'Count': 'จำนวนรายการ'})
    # st.plotly_chart(fig_line, use_container_width=True)

with chart_row1_col2:
    st.write("### 🍩 สัดส่วนความรู้สึกจาก Prompt (Pie/Donut Chart)")
    # TODO: ใช้ px.pie() หรือ px.donut() ดึงคอลัมน์ 'Sentiment' มาพลอตแบ่งกลุ่มความรู้สึก
    # fig_pie = px.pie(filtered_df, names='Sentiment', hole=0.4)
    # st.plotly_chart(fig_pie, use_container_width=True)

# แถวกราฟที่ 2: วิเคราะห์โครงสร้างหน่วยงานและฟีเจอร์เด็ด
chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row2_col1:
    st.write("### 🏛️ สถิติการใช้งานแยกตามภาควิชา (Bar Chart)")
    # TODO: ใช้ px.bar() ดึงคอลัมน์ 'Department' มานับจำนวนครั้งที่เรียกใช้
    # dept_counts = usage_df['Department'].value_counts().reset_index(name='Counts')
    # fig_bar = px.bar(dept_counts, x='Department', y='Counts', color='Department')
    # st.plotly_chart(fig_bar, use_container_width=True)

with chart_row2_col2:
    st.write("### 📲 สัดส่วนการเลือกใช้ Micro Apps (Bar Chart/Pie)")
    # TODO: ดึงคอลัมน์ 'AppUsed' (หรือ AppUsed ตามชื่อหัวคอลัมน์ตารางคุณ) มาส่องสถิติความนิยม
    # app_counts = usage_df['AppUsed'].value_counts().reset_index(name='Calls')
    # fig_app = px.bar(app_counts, x='Calls', y='AppUsed', orientation='h')
    # st.plotly_chart(fig_app, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# STEP 5: ตารางแสดงข้อมูลดิบ (Log Viewer)
# -------------------------------------------------------------
st.write("### 📋 ตารางประวัติบันทึกการใช้งาน (Data Log Viewer)")
# แสดงตาราง DataFrame ที่ผ่านการ Filter เรียบร้อยแล้วให้ผู้ตรวจสามารถกดค้นหาหรือดาวน์โหลดได้
st.dataframe(filtered_df, use_container_width=True)