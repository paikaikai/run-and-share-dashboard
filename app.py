import streamlit as st
import pandas as pd
import plotly.express as px # นำเข้าไลบรารี Plotly สำหรับทำกราฟสีสันสดใส

# 1. ตั้งค่าหน้าเพจ Dashboard
st.set_page_config(page_title="RUN & SHARE Dashboard", layout="wide")

# 2. เพิ่ม CSS เพื่อตกแต่งสีสันของตัวอักษรหัวข้อ
st.markdown("""
<style>
.title-font {
    font-size: 45px !important;
    color: #E65100; /* สีส้มเข้ม (สีนี้สว่างพอที่จะเห็นชัดทั้งสองโหมด) */
    font-weight: 900;
}
.subtitle-font {
    color: #0D47A1; /* สีน้ำเงินเข้ม (ค่าเริ่มต้นสำหรับ Light Mode) */
    font-size: 20px !important;
}

/* ---------------------------------------------------------
   เพิ่มส่วนนี้: กฎสำหรับ Dark Mode
   ระบบจะตรวจสอบว่าถ้าจอเป็นสีมืด จะเปลี่ยนสีตัวอักษรให้สว่างขึ้น
   --------------------------------------------------------- */
@media (prefers-color-scheme: dark) {
    .subtitle-font {
        color: #0b7dda !important; /* เปลี่ยนเป็นสีฟ้าสว่าง (Light Blue) เพื่อให้ตัดกับพื้นสีดำ */
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-font">🏃‍♂️ RUN & SHARE 60 Days Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">สะสมระยะทางไปด้วยกันตลอด 60 วัน (21 ก.ย. - 19 พ.ย. 69)</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# นำลิงก์ที่คัดลอกจาก Google Sheets มาวางในเครื่องหมายคำพูดด้านล่างนี้
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBXP261CRZ3NDfd0ZWCCC6XTE9d_JdnKYNAwGw2NQfoKeNBEomZ22RjgNj6suJFewmjAS0XZnH1kh_/pub?output=csv"
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    return df

# 3. ฟังก์ชันสำหรับซ่อนชื่อ-นามสกุล (Anonymization)
def mask_name(name):
    # ป้องกันกรณีข้อมูลเป็นค่าว่าง ให้แปลงเป็น string ก่อน
    name_str = str(name).strip()
    # แยกคำด้วยช่องว่าง
    parts = name_str.split()
    
    if len(parts) >= 2:
        # หากมีทั้งชื่อและนามสกุล ให้แสดงชื่อเต็ม + อักษรแรกของนามสกุล + ***
        return f"{parts[0]} {parts[1][0]}***"
    elif len(name_str) > 2:
        # หากมีแค่ชื่อคำเดียว ให้แสดงแค่ 2 ตัวอักษรแรก + ***
        return f"{name_str[:2]}***"
    
    return name_str

# ตรวจสอบว่าใส่ลิงก์หรือยัง
if SHEET_CSV_URL == "วางลิงก์ที่คัดลอกมาตรงนี้":
    st.warning("⚠️ กรุณานำลิงก์จาก Google Sheets มาใส่ในตัวแปร SHEET_CSV_URL ในไฟล์โค้ดก่อนครับ")
    st.stop()

# โหลดข้อมูล
df = load_data(SHEET_CSV_URL)

# สร้างคอลัมน์ใหม่ชื่อ 'ชื่อที่แสดงผล' โดยนำฟังก์ชัน mask_name ไปปรับใช้กับคอลัมน์ 'ชื่อ - สกุล'
df['ชื่อที่แสดงผล'] = df['ชื่อ - สกุล'].apply(mask_name)

st.subheader("🏆 สรุปผลภาพรวม")
total_distance = df['รวมระยะวิ่งที่ส่ง'].sum()
total_runners = df['ชื่อ - สกุล'].nunique()

col1, col2 = st.columns(2)
col1.metric("ระยะทางรวมทั้งหมด (กิโลเมตร)", f"{total_distance:,.2f}")
col2.metric("จำนวนนักวิ่งทั้งหมด (คน)", f"{total_runners}")

st.divider()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("🥇 Top 10 นักวิ่งระยะทางสูงสุด")
    # รวมระยะทางและใช้ 'ชื่อที่แสดงผล' แทนชื่อจริง
    top_runners = df.groupby('ชื่อที่แสดงผล')['รวมระยะวิ่งที่ส่ง'].sum().reset_index()
    top_runners = top_runners.sort_values(by='รวมระยะวิ่งที่ส่ง', ascending=False).head(10)
    
    # 4. ใช้ Plotly สร้างกราฟแท่งแบบไล่เฉดสี (Color Scale)
    fig1 = px.bar(top_runners, 
                  x='ชื่อที่แสดงผล', 
                  y='รวมระยะวิ่งที่ส่ง',
                  color='รวมระยะวิ่งที่ส่ง', # ให้สีเปลี่ยนตามระยะทาง
                  color_continuous_scale='YlOrRd', # ใช้โทนสีส้มแดง
                  labels={'รวมระยะวิ่งที่ส่ง': 'ระยะทาง (กม.)', 'ชื่อที่แสดงผล': 'รายชื่อนักวิ่ง'})
    
    # แก้ไข 1: เปลี่ยนสีพื้นหลังกราฟให้โปร่งใส เพื่อให้รองรับทั้ง Light และ Dark Mode
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.subheader("🏢 ระยะทางรวมแบ่งตามหน่วยงาน")
    dept_distance = df.groupby('หน่วยงาน')['รวมระยะวิ่งที่ส่ง'].sum().reset_index()
    dept_distance = dept_distance.sort_values(by='รวมระยะวิ่งที่ส่ง', ascending=False)
    
    # ใช้ Plotly สร้างกราฟแท่งโดยแยกสีตามหน่วยงาน
    fig2 = px.bar(dept_distance, 
                  x='หน่วยงาน', 
                  y='รวมระยะวิ่งที่ส่ง',
                  color='หน่วยงาน', # ให้สีแตกต่างกันตามหน่วยงาน
                  color_discrete_sequence=px.colors.qualitative.Set1, # ใช้ชุดสีพาสเทลสดใส
                  labels={'รวมระยะวิ่งที่ส่ง': 'ระยะทาง (กม.)'})
    
    # แก้ไข 2: เปลี่ยนสีพื้นหลังกราฟให้โปร่งใสเช่นกัน
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig2, use_container_width=True)

# ... (โค้ดส่วนบนของเก่า ตั้งแต่ตั้งค่าเพจจนถึงสร้างกราฟ fig2 ยังคงเหมือนเดิม) ...

st.divider() # เพิ่มเส้นคั่นเพื่อความสวยงาม

# ==========================================
# 5. ส่วนแสดงผลตารางสรุป Leaderboard (เพิ่มใหม่)
# ==========================================
st.subheader("🏃‍♂️ สรุปยอดระยะทางสะสมของนักวิ่งแต่ละคน (Leaderboard)")

# จัดกลุ่มตามชื่อที่แสดงผลและหน่วยงาน แล้วนำระยะทางมารวมกัน
summary_df = df.groupby(['ชื่อที่แสดงผล', 'หน่วยงาน'])['รวมระยะวิ่งที่ส่ง'].sum().reset_index()

# เปลี่ยนชื่อคอลัมน์ให้อ่านเข้าใจง่ายขึ้น
summary_df = summary_df.rename(columns={'รวมระยะวิ่งที่ส่ง': 'ระยะทางสะสมรวม (กม.)'})

# เรียงลำดับจากระยะทางมากไปน้อย
summary_df = summary_df.sort_values(by='ระยะทางสะสมรวม (กม.)', ascending=False).reset_index(drop=True)

# เริ่มต้น Index ที่ 1 แทนที่จะเป็น 0 เพื่อให้เหมือนอันดับ
summary_df.index = summary_df.index + 1 

# หาค่าระยะทางสูงสุด เพื่อนำไปตั้งค่าความยาวสูงสุดของแถบ Progress
max_distance = float(summary_df['ระยะทางสะสมรวม (กม.)'].max())

# แก้ไข 3: ใช้ st.dataframe แบบตั้งค่าคอลัมน์ได้ (Column Config)
# วิธีนี้จะสร้าง Progress Bar แทรกเข้าไปในเซลล์ตัวเลขเลย และรองรับ Dark Mode ได้ดี
st.dataframe(
    summary_df,
    column_config={
        "ระยะทางสะสมรวม (กม.)": st.column_config.ProgressColumn(
            "ระยะทางสะสมรวม (กม.)",
            help="ระยะทางรวมของแต่ละบุคคล",
            format="%.2f", # ฟอร์แมตทศนิยม 2 ตำแหน่ง
            min_value=0,
            max_value=max_distance, # ตั้งขีดสุดของแถบสีเท่ากับคนที่วิ่งได้เยอะที่สุด
        ),
    },
    use_container_width=True,
    hide_index=False # ให้แสดงตัวเลขลำดับข้างหน้า
)

st.divider() # เพิ่มเส้นคั่นระหว่างตารางนักวิ่ง และตารางหน่วยงาน

# ==========================================
# 5.5 ส่วนแสดงผลตารางสรุปตามหน่วยงาน (เพิ่มใหม่)
# ==========================================
st.subheader("🏢 สรุปยอดระยะทางสะสมแบ่งตามหน่วยงาน")

# 1. จัดกลุ่มตามหน่วยงาน แล้วนำระยะทางมารวมกัน
dept_summary_df = df.groupby('หน่วยงาน')['รวมระยะวิ่งที่ส่ง'].sum().reset_index()

# 2. เปลี่ยนชื่อคอลัมน์ให้อ่านเข้าใจง่ายขึ้น
dept_summary_df = dept_summary_df.rename(columns={'รวมระยะวิ่งที่ส่ง': 'ระยะทางสะสมรวม (กม.)'})

# 3. เรียงลำดับจากระยะทางมากไปน้อย
dept_summary_df = dept_summary_df.sort_values(by='ระยะทางสะสมรวม (กม.)', ascending=False).reset_index(drop=True)

# 4. เริ่มต้น Index ที่ 1 เพื่อทำเป็นอันดับ
dept_summary_df.index = dept_summary_df.index + 1 

# 5. หาค่าระยะทางสูงสุดของหน่วยงาน เพื่อนำไปตั้งค่าความยาวสูงสุดของแถบ Progress
max_dept_distance = float(dept_summary_df['ระยะทางสะสมรวม (กม.)'].max())

# 6. แสดงตารางหน่วยงานพร้อมแถบ Progress Bar
st.dataframe(
    dept_summary_df,
    column_config={
        "ระยะทางสะสมรวม (กม.)": st.column_config.ProgressColumn(
            "ระยะทางสะสมรวม (กม.)",
            help="ระยะทางรวมของแต่ละหน่วยงาน",
            format="%.2f", # ฟอร์แมตทศนิยม 2 ตำแหน่ง
            min_value=0,
            max_value=max_dept_distance, # ตั้งขีดสุดของแถบสีเท่ากับหน่วยงานที่วิ่งได้เยอะที่สุด
        ),
    },
    use_container_width=True
)

# ==========================================
# 6. แสดงตารางข้อมูลดิบ (เปิด/ปิดได้เหมือนเดิม)
# ==========================================
with st.expander("ดูประวัติการส่งผลวิ่งแต่ละครั้งทั้งหมด (ข้อมูลอัปเดตทุก 5 นาที)"):
    # ในตารางข้อมูลดิบ เราจะแสดงเฉพาะ 'ชื่อที่แสดงผล' เพื่อความปลอดภัยของข้อมูล
    st.dataframe(df[['Timestamp', 'ชื่อที่แสดงผล', 'หน่วยงาน', 'สัปดาห์สำหรับการส่งผลวิ่ง', 'รวมระยะวิ่งที่ส่ง']], use_container_width=True)
