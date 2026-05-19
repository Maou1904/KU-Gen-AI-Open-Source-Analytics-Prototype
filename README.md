# KU Gen AI - Open Source Analytics Prototype

## วิธีติดตั้ง (Installation)
1. เปิดเทอร์มินัลในโฟลเดอร์โปรเจกต์:
   ```bash
   cd KU-Gen-AI-Open-Source-Analytics-Prototype
   ```
2. ติดตั้ง dependencies จากไฟล์ `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
## วิธีเปิดผ่าน Docker
1. เปิดเทอร์มินัลในโฟลเดอร์โปรเจกต์:
   ```bash
   docker compose up --build -d
   ```
2. เข้า Website:
   ```bash
   http://localhost:8501/
   ```

## วิธีรันโปรเจกต์ (How to run)

1. สร้างข้อมูลจำลองถ้ายังไม่มีไฟล์ `data/mock_data.csv`:
   ```bash
   python src/generator.py
   ```
2. รัน Streamlit dashboard:
   ```bash
   streamlit run src/app.py
   ```
3. ถ้าต้องการรีเฟรชข้อมูลใหม่ ให้รัน `generator.py` ก่อนแล้วค่อยรัน dashboard อีกครั้ง.
4. หรือเข้าผ่าน link ที่ deploy แล้ว https://ku-gen-ai-prototype.streamlit.app/

## โครงสร้างของโปรเจกต์ (Project Structure)

```text
KU-Gen-AI-Open-Source-Analytics-Prototype/
│
├── data/                               # โฟลเดอร์เก็บข้อมูลของระบบ
│   ├── mock_data.csv                   # ข้อมูลดิบที่ได้จากการสุ่ม (Phase 1)
│   └── processed_analytics_data.csv    # ข้อมูลที่ผ่านการคลีนและวิเคราะห์ความรู้สึกแล้ว (Phase 2)
│
├── src/                                # โฟลเดอร์เก็บซอร์สโค้ดหลัก
│   ├── generator.py                    # สคริปต์สร้างข้อมูลจำลอง mock data
│   ├── analytics.py                    # ท่อประมวลผลข้อมูล คลีน type และทำ Sentiment Analysis
│   └── app.py                          # โค้ดหน้าจอ Interactive Dashboard ด้วย Streamlit
│
├── README.md                           # คู่มือการติดตั้งและใช้งานโปรเจกต์ (ไฟล์นี้)
└── requirements.txt                    # รายการ Library ทั้งหมดที่โปรเจกต์จำเป็นต้องใช้
```

## รายการ Library ที่ใช้ (requirements.txt)

ไฟล์ `requirements.txt` ของโปรเจกต์ประกอบด้วย:

- `streamlit` — สร้าง dashboard UI
- `pandas` — จัดการข้อมูลตาราง
- `plotly` — วาดกราฟ interactive
- `textblob` — วิเคราะห์ sentiment จากข้อความ
- `Faker` — สร้าง mock data จำลอง
- `nltk` — รองรับการดาวน์โหลด corpora สำหรับ TextBlob
- `python-dateutil` — ช่วยจัดการวันที่ใน pandas
- `pytz` — ตัวจัดการ timezone

ดูไฟล์ `requirements.txt` เพื่อปรับเวอร์ชันหรือเพิ่ม dependency เพิ่มเติมตามต้องการ.