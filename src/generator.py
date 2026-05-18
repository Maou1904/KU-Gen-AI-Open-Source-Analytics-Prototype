import random
import pandas as pd
import faker
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Data Pools
FACULTIES = {
    "Engineering": ["Computer Science", "Civil Engineering", "Mechanical Engineering"],
    "Science": ["Mathematics", "Chemistry", "Physics"],
    "Business Administration": ["Marketing", "Accounting", "Finance"]
}
ROLES = ["Student", "Staff", "Faculty", "Lecturer"]
APPS = ["ChatGPT Chatflow for Education", "Gemini DeepResearch v1", "KIN Perplexity Chatflow"]
DEVICES = ["Desktop", "Mobile", "Tablet"]

TAGS_POOLS = {
    "Computer Science": [
        "Python Programming",
        "Data Structures",
        "Algorithms"
    ],
    "Civil Engineering": [
        "Structural Analysis",
        "Geotechnical Engineering",
        "Transportation Engineering"
    ],
    "Mechanical Engineering": [
        "Thermodynamics",
        "Fluid Mechanics",
        "Machine Design"
    ],
    "Mathematics": [
        "Calculus",
        "Linear Algebra",
        "Statistics"
    ],
    "Chemistry": [
        "Organic Chemistry",
        "Inorganic Chemistry",
        "Physical Chemistry"
    ],
    "Physics": [
        "Classical Mechanics",
        "Electromagnetism",
        "Quantum Physics"
    ],
    "Marketing": [
        "Digital Marketing",
        "Brand Management",
        "Consumer Behavior"
    ],
    "Accounting": [
        "Financial Accounting",
        "Managerial Accounting",
        "Taxation"
    ],
    "Finance": [
        "Investment Analysis",
        "Corporate Finance",
        "Risk Management"
    ]
}

# Generateion Logic
def generate_mock_data(num_records=1200):
    data_list = []
    
    # Data Last 30 Days
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_records):
        campus = random.choices(["Bangkhen", "Kamphaeng Saen", "Sriracha"], weights=[0.6, 0.2, 0.2])[0]

        faculty = random.choice(list(FACULTIES.keys()))
        department = random.choice(FACULTIES[faculty])
        
        role = random.choices(ROLES, weights=[0.7, 0.1, 0.1, 0.1])[0]
        if role == "Student":
            education_level = random.choices(["ป.ตรี", "ป.โท", "ป.เอก"], weights=[0.6, 0.25, 0.15])[0]
        else:
            education_level = "N/A"
        
        # 2.4 ลอจิกการแบ่งประเภทธุรกรรม (Usage vs Top-up)
        # TODO: สุ่มเลือกว่าแถวนี้จะเป็นการใช้งาน AI หรือการเติมเงิน
        transaction_type = random.choices(["Usage", "Top-up"], weights=[0.9, 0.1])[0]
        if transaction_type == "Top-up":
            msg = "Top-up"
            response = "Top-up Success"
            token = random.randint(100, 5000)
            proc_time = 0.0
            app_used = "N/A"
            status = "Success"
            is_copied = False
            is_shared = False
            is_saved = False
            tags = ""
        else: #Usage
            msg = fake.sentence(nb_words=6) + " " + random.choices(TAGS_POOLS[department], weights=[0.5, 0.3, 0.2], k=1)[0]
            proc_time = random.uniform(0.10, 10.00)
            app_used = random.choice(APPS)
            
            status = random.choices(["Success", "Failed"], weights=[0.95, 0.05])[0]
            if status == "Failed":
                response = "Error: AI processing failed."
                token = 10
                is_copied = False
                is_shared = False
                is_saved = False
                tags = ", ".join(random.sample(TAGS_POOLS.get(department, []), k=random.randint(1, 3)))
            else: # Success
                response = f"AI Response: {fake.sentence(nb_words=12)}"
                token = random.randint(10, 2000)
                is_copied = random.choices([True, False], weights=[0.3, 0.7])
                is_shared = random.choices([True, False], weights=[0.2, 0.8])
                is_saved = random.choices([True, False], weights=[0.4, 0.6])
                tags = ", ".join(random.sample(TAGS_POOLS.get(department, []), k=random.randint(1, 3)))

        # Combination
        record = {
            "UserID": f"{random.randint(66, 69)}{random.randint(10000000, 99999999)}",
            "Timestamp": start_date + timedelta(seconds=random.randint(0, 30*24*60*60)),
            "Campus": campus,
            "Faculty": faculty,
            "Department": department,
            "Role": role,
            "EducationLevel": education_level,
            "TransactionType": transaction_type,
            "Message/Prompt": msg,
            "AI_Response": response,
            "TokenUsed": token,
            "ProcessingTime": proc_time,
            "AppUsed": app_used,
            "Status": status,
            "IsCopied": is_copied,
            "IsShared": is_shared,
            "IsSaved": is_saved,
            "Tags": tags
        }
        data_list.append(record)
        
    # -------------------------------------------------------------
    # STEP 4: แปลงเป็น DataFrame และจัดระเบียบข้อมูลก่อนส่งออก
    # -------------------------------------------------------------
    df = pd.DataFrame(data_list)
    df = df.sort_values(by="Timestamp").reset_index(drop=True)
    
    # TODO: สั่งเรียงลำดับข้อมูลตามเวลา (Timestamp) เพื่อให้เหมือนไฟล์ Log ของจริง
    
    return df

if __name__ == "__main__":
    print("Generating mock data...")
    df_result = generate_mock_data(1200)

    df_result.to_csv("data/mock_data.csv", index=False)
    print("✅ Done! Save to data/mock_data.csv")