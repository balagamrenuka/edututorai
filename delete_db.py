import os

db_path = "data/edututor.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Deleted old edututor.db")
else:
    print("❌ No database found at", db_path)
