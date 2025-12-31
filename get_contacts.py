from telethon import TelegramClient
from telethon.tl.functions.contacts import GetContactsRequest
from openpyxl import Workbook

# ===== CONFIG =====
api_id = 20460444       # ใส่ API ID
api_hash = "258de181baaf84d467f7ef6a0f29d39b"  # ใส่ API HASH
session_name = "my_account"
output_file = "telegram_contacts.xlsx"

# ==================
with TelegramClient(session_name, api_id, api_hash) as client:
    result = client(GetContactsRequest(hash=0))
    users = result.users

    print(f"Total contacts: {len(users)}")

    with open("telegram_contacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Username", "First Name", "Last Name", "Phone"])

        for user in users:
            writer.writerow([
                user.id,
                user.username or "",
                user.first_name or "",
                user.last_name or "",
                user.phone or ""
            ])

    print("✅ Exported to telegram_contacts.csv")
