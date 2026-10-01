import streamlit as st
import pandas as pd
import plotly.express as px # นำเข้าไลบรารี Plotly สำหรับทำกราฟสีสันสดใส

# 1. ตั้งค่าหน้าเพจ Dashboard
st.set_page_config(page_title="RUN & SHARE Dashboard", layout="wide")

# 2. เพิ่ม CSS เพื่อตกแต่งสีสันของตัวอักษรหัวข้อ
st.markdown("""
<style>
/* ตั้งค่าเริ่มต้นสำหรับหน้าจอคอมพิวเตอร์ */
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

/* ---------------------------------------------------------
   เพิ่มส่วนนี้: กฎสำหรับขนาดหน้าจอ (Responsive Design)
   ถ้าหน้าจอขนาดเล็กกว่า 768px (มือถือ/แท็บเล็ต) ให้ลดขนาดฟอนต์ลง
   --------------------------------------------------------- */
@media (max-width: 768px) {
    .title-font {
        font-size: 32px !important; /* ลดจาก 45px เหลือ 32px */
    }
    .subtitle-font {
        font-size: 16px !important; /* ลดจาก 20px เหลือ 16px */
    }
}

/* ---------------------------------------------------------
   เพิ่มส่วนนี้เพื่อซ่อนแถบเมนู ลายน้ำ และปุ่ม Profile ของ Streamlit
   --------------------------------------------------------- */
/* ซ่อนแถบ Header ด้านบน (เมนู 3 จุด) */
[data-testid="stHeader"] {
    display: none !important;
}

/* ซ่อน Footer ด้านล่าง (Made with Streamlit) */
footer {
    display: none !important;
}

/* ซ่อนปุ่ม Profile มุมขวาล่าง (Viewer Badge) */
.viewerBadge_container {
    display: none !important;
}
.viewerBadge_link {
    display: none !important;
}
#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-font">🏃‍♂️ RUN & SHARE 60 Days Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">สะสมระยะทางไปด้วยกันตลอด 60 วัน (21 ก.ย. - 19 พ.ย. 69)</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# นำลิงก์ที่คัดลอกจาก Google Sheets มาวางในเครื่องหมายคำพูดด้านล่างนี้
SHEET_CSV_URL = st.secrets["SHEET_URL"]
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    return df

# ตรวจสอบว่าใส่ลิงก์หรือยัง
if SHEET_CSV_URL == "วางลิงก์ที่คัดลอกมาตรงนี้":
    st.warning("⚠️ กรุณานำลิงก์จาก Google Sheets มาใส่ในตัวแปร SHEET_CSV_URL ในไฟล์โค้ดก่อนครับ")
    st.stop()

# โหลดข้อมูล
df = load_data(SHEET_CSV_URL)

# ---------------------------------------------------------
# ดึงรายชื่อนักวิ่งทั้งหมดมาจัดเรียงตามตัวอักษร เพื่อให้แต่ละคนได้หมายเลขเดิมเสมอ
unique_names = sorted(df['ชื่อ - สกุล'].unique())

# สร้างระบบจับคู่ชื่อจริง กับชื่อสมมติ (เช่น "นักวิ่งคนที่ 1", "นักวิ่งคนที่ 2")
name_mapping = {name: f"นักวิ่งคนที่ {i+1}" for i, name in enumerate(unique_names)}

# สร้างคอลัมน์ 'ชื่อที่แสดงผล' โดยนำชื่อจริงไปเทียบกับระบบจับคู่ที่เราสร้างไว้
df['ชื่อที่แสดงผล'] = df['ชื่อ - สกุล'].map(name_mapping)
# ---------------------------------------------------------

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
                  color_continuous_scale='blugrn',
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
    dept_distance = dept_distance.sample(frac=1).reset_index(drop=True)
    
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
summary_df = df.groupby('ชื่อที่แสดงผล')['รวมระยะวิ่งที่ส่ง'].sum().reset_index()

# เปลี่ยนชื่อคอลัมน์ให้อ่านเข้าใจง่ายขึ้น
summary_df = summary_df.rename(columns={'รวมระยะวิ่งที่ส่ง': 'ระยะทางสะสมรวม (กม.)'})

# เพื่อสับเปลี่ยนแถวข้อมูลทั้งหมดแบบสุ่ม (Random)
summary_df = summary_df.sample(frac=1).reset_index(drop=True)

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
dept_summary_df = dept_summary_df.sample(frac=1).reset_index(drop=True)

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
    st.dataframe(df[['Timestamp', 'ชื่อที่แสดงผล', 'สัปดาห์สำหรับการส่งผลวิ่ง', 'รวมระยะวิ่งที่ส่ง']], use_container_width=True)
