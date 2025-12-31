import tkinter as tk
from tkinter import messagebox, simpledialog
from telethon import TelegramClient, sync
from telethon.tl.functions.contacts import GetContactsRequest
from openpyxl import Workbook
import threading
import asyncio

def export_contacts():
    api_id_raw = api_id_entry.get().strip()
    api_hash = api_hash_entry.get().strip()

    if not api_id_raw or not api_hash:
        messagebox.showerror("Error", "Please enter API ID and API HASH")
        return

    try:
        api_id = int(api_id_raw)
    except ValueError:
        messagebox.showerror("Error", "API ID must be a number")
        return

    export_btn.config(state="disabled")
    status_label.config(text="⏳ Connecting to Telegram...")

    def task():
        # Create a new event loop for this background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            client = TelegramClient(f"session_{api_id}", api_id, api_hash)
            client.connect()

            # --- Check Authorization ---
            if not client.is_user_authorized():
                # Ask for phone number via UI
                phone = simpledialog.askstring("Phone", "Enter your phone number (with country code):", parent=root)
                if not phone:
                    raise Exception("Phone number required")
                
                client.send_code_request(phone)
                code = simpledialog.askstring("Code", "Enter the code sent to your Telegram:", parent=root)
                if not code:
                    raise Exception("Verification code required")
                
                client.sign_in(phone, code)

            # --- Fetch Contacts ---
            root.after(0, lambda: status_label.config(text="⏳ Fetching contacts..."))
            result = client(GetContactsRequest(hash=0))
            users = result.users

            # --- Save to Excel ---
            wb = Workbook()
            ws = wb.active
            ws.title = "Telegram Contacts"
            ws.append(["Telegram ID", "Username", "First Name", "Last Name", "Phone"])

            for u in users:
                ws.append([u.id, u.username or "", u.first_name or "", u.last_name or "", u.phone or ""])

            file_name = "telegram_contacts.xlsx"
            wb.save(file_name)
            client.disconnect()

            root.after(0, lambda: messagebox.showinfo("Success", f"✅ Exported {len(users)} contacts\nSaved as {file_name}"))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Failed: {str(e)}"))
        
        finally:
            root.after(0, lambda: export_btn.config(state="normal"))
            root.after(0, lambda: status_label.config(text="Ready"))

    threading.Thread(target=task, daemon=True).start()

# ===== UI Setup =====
root = tk.Tk()
root.title("Telegram Contacts Exporter v2")
root.geometry("420x280")

tk.Label(root, text="API ID", font=("Arial", 10)).pack(pady=(15, 0))
api_id_entry = tk.Entry(root, width=35)
api_id_entry.pack(pady=5)

tk.Label(root, text="API HASH", font=("Arial", 10)).pack(pady=(5, 0))
api_hash_entry = tk.Entry(root, width=35)
api_hash_entry.pack(pady=5)

export_btn = tk.Button(
    root, 
    text="📤 Export Contacts to Excel", 
    font=("Arial", 11, "bold"),
    bg="#0088cc", # Telegram Blue
    fg="white",
    padx=20,
    pady=10,
    command=export_contacts
)
export_btn.pack(pady=20)

status_label = tk.Label(root, text="Ready", fg="gray")
status_label.pack()

root.mainloop()