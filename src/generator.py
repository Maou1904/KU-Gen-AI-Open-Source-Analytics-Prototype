import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Data Pools
CAMPUSES = ["Bangkhen", "Kamphaeng Saen", "Sriracha"]
FACULTIES = {
    "Engineering": ["Computer Science", "Civil Engineering", "Mechanical Engineering"],
    "Science": ["Mathematics", "Chemistry", "Physics"],
    "Business Administration": ["Marketing", "Accounting", "Finance"]
}
ROLES = ["Student", "Student", "Student", "Student", "Staff", "Faculty", "Lecturer"]
EDUCATION_LEVELS = ["ป.ตรี", "ป.โท", "ป.เอก", "N/A"]
APPS = ["ChatGPT Chatflow for Education", "Gemini DeepResearch v1", "KIN Perplexity Chatflow"]
DEVICES = ["Desktop", "Mobile", "Tablet"]



