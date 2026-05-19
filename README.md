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
## แบบ Docker
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
├── data/                               # ข้อมูลตัวอย่างและข้อมูลที่ผ่านการประมวลผล
│   ├── mock_data.csv                   # ข้อมูลจำลองที่สร้างด้วย generator.py
│   └── processed_analytics_data.csv    # ข้อมูลที่ผ่านการวิเคราะห์แล้วจาก analytics.py
├── src/                                # ซอร์สโค้ดหลักของโปรเจกต์
│   ├── analytics.py                    # ฟังก์ชันวิเคราะห์ข้อมูลและคำนวณสถิติ
│   ├── app.py                          # Streamlit dashboard entrypoint
│   └── generator.py                    # สคริปต์สร้าง mock data
├── Dockerfile                          # สร้าง container สำหรับรัน Streamlit app
├── docker-compose.yml                  # คอนฟิกการรัน Docker Compose
├── requirements.txt                    # รายการ dependency ของ Python
├── README.md                           # ไฟล์นี้
└── Report.pdf                          # รายงาน/เอกสารประกอบโปรเจกต์
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