import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
from telethon import TelegramClient, types, errors
from telethon.tl.functions.contacts import GetContactsRequest
import threading
import asyncio
import os
import time
import pandas as pd # ต้องติดตั้ง: pip install pandas openpyxl

class TelegramMarketingPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Marketing Pro v4.2 (Excel/CSV Support)")
        self.root.geometry("600x950")
        self.image_path_var = tk.StringVar()
        self.imported_phones = [] # เก็บรายชื่อเบอร์ที่โหลดมาจากไฟล์
        self.setup_ui()

    def setup_ui(self):
        # --- 1. API Setup ---
        frame_api = tk.LabelFrame(self.root, text=" 1. ตั้งค่าบัญชี ", padx=10, pady=10)
        frame_api.pack(pady=10, fill="x", padx=20)
        tk.Label(frame_api, text="API ID:").grid(row=0, column=0, sticky="w")
        self.api_id_entry = tk.Entry(frame_api, width=30)
        self.api_id_entry.grid(row=0, column=1, pady=2)
        tk.Label(frame_api, text="API Hash:").grid(row=1, column=0, sticky="w")
        self.api_hash_entry = tk.Entry(frame_api, width=30)
        self.api_hash_entry.grid(row=1, column=1, pady=2)

        # --- 2. Import Excel/CSV ---
        frame_import = tk.LabelFrame(self.root, text=" 2. นำเข้าข้อมูลเป้าหมาย ", padx=10, pady=10, fg="green")
        frame_import.pack(pady=5, fill="x", padx=20)
        
        tk.Button(frame_import, text="📂 เลือกไฟล์ Excel/CSV", command=self.import_phones).pack(side="left")
        self.import_label = tk.Label(frame_import, text="ยังไม่ได้นำเข้าไฟล์", fg="gray")
        self.import_label.pack(side="left", padx=10)

        # --- 3. Broadcast Mode ---
        frame_mode = tk.LabelFrame(self.root, text=" 3. เลือกเป้าหมายการส่ง ", padx=10, pady=10)
        frame_mode.pack(pady=5, fill="x", padx=20)
        self.mode_var = tk.StringVar(value="contacts")
        tk.Radiobutton(frame_mode, text="ผู้ติดต่อ (Contacts)", variable=self.mode_var, value="contacts").pack(side="left")
        tk.Radiobutton(frame_mode, text="กลุ่ม/แชนเนล", variable=self.mode_var, value="groups").pack(side="left")
        tk.Radiobutton(frame_mode, text="เบอร์ที่นำเข้า (Excel)", variable=self.mode_var, value="imported", fg="blue").pack(side="left")

        # --- 4. Message & Media ---
        frame_msg = tk.LabelFrame(self.root, text=" 4. ข้อความและสื่อ ", padx=10, pady=10)
        frame_msg.pack(pady=5, fill="x", padx=20)
        self.msg_entry = tk.Text(frame_msg, width=50, height=5)
        self.msg_entry.pack(pady=5)
        tk.Button(frame_msg, text="🖼️ เลือกรูปภาพ", command=self.select_image).pack()
        self.img_label = tk.Label(frame_msg, text="ไม่ได้เลือกรูป", fg="gray")
        self.img_label.pack()
        
        tk.Label(frame_msg, text="ปุ่ม CTA:").pack(side="left")
        self.cta_text = tk.Entry(frame_msg, width=12)
        self.cta_text.pack(side="left", padx=2)
        tk.Label(frame_msg, text="URL:").pack(side="left")
        self.cta_url = tk.Entry(frame_msg, width=18)
        self.cta_url.pack(side="left")

        # --- 5. Logs & Main Button ---
        self.send_btn = tk.Button(self.root, text="🚀 เริ่มรันระบบ Broadcast", font=("Arial", 12, "bold"), 
                                 bg="#28a745", fg="white", height=2, command=self.start_process)
        self.send_btn.pack(pady=10, fill="x", padx=50)

        self.log_area = scrolledtext.ScrolledText(self.root, height=10, width=70, font=("Consolas", 9))
        self.log_area.pack(pady=10, padx=20)

    # --- ฟังก์ชันนำเข้าไฟล์ ---
    def import_phones(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # สมมติว่าเบอร์โทรศัพท์อยู่ในคอลัมน์แรก หรือคอลัมน์ที่ชื่อ 'phone'
            column_name = 'phone' if 'phone' in df.columns else df.columns[0]
            self.imported_phones = df[column_name].astype(str).tolist()
            
            # ทำความสะอาดข้อมูลเบอร์โทร (ลบช่องว่าง, ลบขีด)
            self.imported_phones = [p.replace(" ", "").replace("-", "") for p in self.imported_phones if p.strip()]
            
            self.import_label.config(text=f"นำเข้าแล้ว {len(self.imported_phones)} เบอร์", fg="black")
            self.write_log(f"📂 โหลดไฟล์สำเร็จ: พบ {len(self.imported_phones)} รายชื่อ")
            messagebox.showinfo("Success", f"โหลดรายชื่อสำเร็จ {len(self.imported_phones)} เบอร์")
            self.mode_var.set("imported") # เปลี่ยนโหมดให้โดยอัตโนมัติ
            
        except Exception as e:
            messagebox.showerror("Import Error", f"ไม่สามารถอ่านไฟล์ได้: {str(e)}")

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path: self.image_path_var.set(path); self.img_label.config(text=os.path.basename(path))

    def write_log(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n"); self.log_area.see(tk.END)

    def safe_ask(self, title, prompt, is_pwd=False):
        res = [None]; event = threading.Event()
        def ask(): res[0] = simpledialog.askstring(title, prompt, parent=self.root, show="*" if is_pwd else None); event.set()
        self.root.after(0, ask); event.wait(); return res[0]

    def start_process(self):
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        if not api_id: return messagebox.showerror("Error", "กรุณาระบุ API ID")
        
        if self.mode_var.get() == "imported" and not self.imported_phones:
            return messagebox.showwarning("Warning", "ยังไม่ได้นำเข้าเบอร์โทรศัพท์จากไฟล์")

        self.send_btn.config(state="disabled")
        threading.Thread(target=self.worker, args=(int(api_id), api_hash), daemon=True).start()

    def worker(self, api_id, api_hash):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main_task(api_id, api_hash))

    async def main_task(self, api_id, api_hash):
        client = TelegramClient(f"session_{api_id}", api_id, api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                phone = self.safe_ask("Login", "เบอร์โทรศัพท์ (+66...):")
                await client.send_code_request(phone)
                code = self.safe_ask("OTP", "รหัส 5 หลัก:")
                try:
                    await client.sign_in(phone, code)
                except errors.SessionPasswordNeededError:
                    pwd = self.safe_ask("2FA", "กรอก Cloud Password:", is_pwd=True)
                    await client.sign_in(password=pwd)

            self.write_log("✅ เข้าสู่ระบบสำเร็จ")
            
            msg = self.msg_entry.get("1.0", tk.END).strip()
            btn = [types.KeyboardButtonUrl(self.cta_text.get(), self.cta_url.get())] if self.cta_text.get() else None
            img = self.image_path_var.get() or None

            # --- เลือกเป้าหมายตามโหมด ---
            targets = []
            if self.mode_var.get() == "contacts":
                res = await client(GetContactsRequest(hash=0))
                targets = [u.id for u in res.users if not u.bot and not u.deleted]
            elif self.mode_var.get() == "groups":
                dialogs = await client.get_dialogs()
                targets = [d.id for d in dialogs if d.is_group or d.is_channel]
            else: # โหมด imported
                targets = self.imported_phones

            self.write_log(f"📢 เริ่มส่งทั้งหมด {len(targets)} รายการ")

            success = 0
            for t in targets:
                try:
                    # ตรวจสอบว่ามีรูปภาพหรือไม่
                    if img:
                        # มีรูป: ใช้ send_file (รวม Caption และปุ่ม)
                        await client.send_file(t, img, caption=msg, buttons=btn)
                    else:
                        # ไม่มีรูป:ใช้ send_message แทน
                        await client.send_message(t, msg, buttons=btn)
                    
                    success += 1
                    self.write_log(f"OK -> {t}")
                    await asyncio.sleep(4) # หน่วงเวลาป้องกันโดนแบน
                except Exception as e:
                    self.write_log(f"FAIL -> {t}: {str(e)}")
                    if "A wait of" in str(e):
                        self.write_log("⚠️ ติด Flood Wait... พักระบบ 30 วินาที")
                        await asyncio.sleep(30)
            
            self.root.after(0, lambda: messagebox.showinfo("เสร็จสิ้น", f"ส่งสำเร็จ {success} รายการ"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            await client.disconnect()
            self.root.after(0, lambda: self.send_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramMarketingPro(root)
    root.mainloop()