from telethon import TelegramClient
from telethon.tl.functions.contacts import GetContactsRequest
from openpyxl import Workbook

# ===== CONFIG =====
api_id = 30775549            # ใส่ API ID ของคุณ
api_hash = "3747bf1f1748fbc7185683de75d23a8a"    # ใส่ API HASH
session_name = "my_account"
output_file = "telegram_contacts.xlsx"
# ==================

with TelegramClient(session_name, api_id, api_hash) as client:
    result = client(GetContactsRequest(hash=0))
    users = result.users

    print(f"Total contacts: {len(users)}")

    wb = Workbook()
    ws = wb.active
    ws.title = "Telegram Contacts"

    # Header
    ws.append([
        "Telegram ID",
        "Username",
        "First Name",
        "Last Name",
        "Phone"
    ])

    for user in users:
        ws.append([
            user.id,
            user.username or "",
            user.first_name or "",
            user.last_name or "",
            user.phone or ""
        ])

    wb.save(output_file)

    print(f"✅ Exported to {output_file}")
