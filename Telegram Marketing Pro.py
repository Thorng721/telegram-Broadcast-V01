import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
from telethon import TelegramClient, types, errors
from telethon.tl.functions.contacts import GetContactsRequest
import threading
import asyncio
import os
import time
import random  # สำหรับสุ่มเวลา
import re      # สำหรับระบบสุ่มข้อความ (Spintax)
import pandas as pd

class TelegramMarketingPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Marketing Pro v4.4 (Anti-Ban Pro)")
        self.root.geometry("600x1000") # เพิ่มความสูงเล็กน้อย
        self.image_path_var = tk.StringVar()
        self.imported_phones = []
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

        # --- 2. Data Management ---
        frame_data = tk.LabelFrame(self.root, text=" 2. จัดการข้อมูลผู้ติดต่อ ", padx=10, pady=10)
        frame_data.pack(pady=5, fill="x", padx=20)
        btn_frame = tk.Frame(frame_data)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="📂 นำเข้า Excel/CSV", command=self.import_phones, width=18).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📥 ส่งออกรายชื่อเครื่อง", command=self.start_export, width=18).pack(side="left", padx=5)
        self.data_status_label = tk.Label(frame_data, text="สถานะ: ยังไม่ได้โหลดข้อมูล", fg="gray")
        self.data_status_label.pack(pady=5, anchor="w")

        # --- 3. Anti-Ban Settings (NEW!) ---
        frame_delay = tk.LabelFrame(self.root, text=" 3. ตั้งค่าหน่วงเวลา (Anti-Ban) ", padx=10, pady=10, fg="darkred")
        frame_delay.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_delay, text="สุ่มรอระหว่าง:").pack(side="left")
        self.delay_min = tk.Spinbox(frame_delay, from_=1, to=60, width=5)
        self.delay_min.delete(0, tk.END)
        self.delay_min.insert(0, "5")
        self.delay_min.pack(side="left", padx=5)
        tk.Label(frame_delay, text="ถึง").pack(side="left")
        self.delay_max = tk.Spinbox(frame_delay, from_=1, to=120, width=5)
        self.delay_max.delete(0, tk.END)
        self.delay_max.insert(0, "15")
        self.delay_max.pack(side="left", padx=5)
        tk.Label(frame_delay, text="วินาที").pack(side="left")

        # --- 4. Message & Media ---
        frame_msg = tk.LabelFrame(self.root, text=" 4. เนื้อหาข้อความ (รองรับ {สุ่ม|คำ}) ", padx=10, pady=10)
        frame_msg.pack(pady=5, fill="x", padx=20)
        self.msg_entry = tk.Text(frame_msg, width=50, height=5)
        self.msg_entry.pack(pady=5)
        tk.Button(frame_msg, text="🖼️ เลือกรูปภาพประกอบ", command=self.select_image).pack()
        self.img_label = tk.Label(frame_msg, text="ยังไม่ได้เลือกรูป", fg="gray")
        self.img_label.pack()
        
        tk.Label(frame_msg, text="ปุ่ม CTA:").pack(side="left")
        self.cta_text = tk.Entry(frame_msg, width=12)
        self.cta_text.pack(side="left", padx=2)
        tk.Label(frame_msg, text="URL:").pack(side="left")
        self.cta_url = tk.Entry(frame_msg, width=18)
        self.cta_url.pack(side="left")

        # --- 5. Logs & Control ---
        self.mode_var = tk.StringVar(value="contacts")
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="ผู้ติดต่อ", variable=self.mode_var, value="contacts").pack(side="left")
        tk.Radiobutton(mode_frame, text="จากไฟล์", variable=self.mode_var, value="imported").pack(side="left")

        self.send_btn = tk.Button(self.root, text="🚀 เริ่มส่งระบบสุ่มหน่วงเวลา", font=("Arial", 12, "bold"), 
                                 bg="#d32f2f", fg="white", height=2, command=self.start_process)
        self.send_btn.pack(pady=10, fill="x", padx=50)

        self.log_area = scrolledtext.ScrolledText(self.root, height=10, width=70, font=("Consolas", 9))
        self.log_area.pack(pady=10, padx=20)

    # --- ระบบ Spintax (สุ่มข้อความ) ---
    def spin_text(self, text):
        """ แปลง {a|b|c} เป็นข้อความที่สุ่มเลือกมา 1 อย่าง """
        def replace(match):
            options = match.group(1).split('|')
            return random.choice(options)
        return re.sub(r'\{(.*?)\}', replace, text)

    # --- ฟังก์ชันหลัก (ปรับปรุงการหน่วงเวลา) ---
    async def main_broadcast_task(self, api_id, api_hash):
        client = TelegramClient(f"session_{api_id}", api_id, api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await self.login_process(client)

            raw_msg = self.msg_entry.get("1.0", tk.END).strip()
            img = self.image_path_var.get() or None
            btn_txt = self.cta_text.get()
            btn_url = self.cta_url.get()
            
            # ดึงค่าดีเลย์จาก UI
            d_min = int(self.delay_min.get())
            d_max = int(self.delay_max.get())

            targets = []
            if self.mode_var.get() == "contacts":
                res = await client(GetContactsRequest(hash=0))
                targets = [u.id for u in res.users if not u.bot]
            else:
                targets = self.imported_phones

            self.write_log(f"📢 เตรียมส่ง {len(targets)} รายการ (สุ่มหน่วงเวลา {d_min}-{d_max} วิ)")
            
            success = 0
            for t in targets:
                try:
                    # สุ่มข้อความสำหรับคนนี้
                    current_msg = self.spin_text(raw_msg)
                    btn = [types.KeyboardButtonUrl(btn_txt, btn_url)] if btn_txt else None

                    if img:
                        await client.send_file(t, img, caption=current_msg, buttons=btn)
                    else:
                        await client.send_message(t, current_msg, buttons=btn)
                    
                    success += 1
                    self.write_log(f"✅ สำเร็จ -> {t}")
                    
                    # สุ่มเวลารอก่อนส่งคนถัดไป
                    wait_time = random.randint(d_min, d_max)
                    self.write_log(f"⏳ รอสุ่ม {wait_time} วินาที...")
                    await asyncio.sleep(wait_time)

                except Exception as e:
                    self.write_log(f"❌ พลาด -> {t}: {e}")
                    if "A wait of" in str(e):
                        wait_flood = int(re.findall(r'\d+', str(e))[0]) + 5
                        self.write_log(f"⚠️ โดนจำกัดเวลา! ต้องรอ {wait_flood} วินาที")
                        await asyncio.sleep(wait_flood)
            
            messagebox.showinfo("เสร็จสิ้น", f"ส่งเรียบร้อย! สำเร็จ {success} รายการ")
        finally:
            await client.disconnect()
            self.root.after(0, lambda: self.send_btn.config(state="normal"))

    # --- ส่วนที่เหลือ (เหมือนเดิมจาก v4.3) ---
    def import_phones(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                col = 'phone' if 'phone' in df.columns else df.columns[0]
                self.imported_phones = [str(p).replace(" ", "").replace("-", "").replace(".0", "") for p in df[col].tolist() if str(p).strip()]
                self.data_status_label.config(text=f"✅ นำเข้าสำเร็จ {len(self.imported_phones)} รายชื่อ", fg="blue")
            except Exception as e: messagebox.showerror("Error", str(e))

    def start_export(self):
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        if api_id: threading.Thread(target=self.worker_export, args=(int(api_id), api_hash), daemon=True).start()

    def worker_export(self, api_id, api_hash):
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(self.export_contacts_task(api_id, api_hash))

    async def export_contacts_task(self, api_id, api_hash):
        client = TelegramClient(f"session_{api_id}", api_id, api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized(): await self.login_process(client)
            res = await client(GetContactsRequest(hash=0))
            df = pd.DataFrame([{"Name": f"{u.first_name} {u.last_name or ''}", "Phone": u.phone, "User ID": u.id} for u in res.users])
            path = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if path: df.to_excel(path, index=False); messagebox.showinfo("Success", "Export เรียบร้อย")
        finally: await client.disconnect()

    def start_process(self):
        api_id = self.api_id_entry.get().strip(); api_hash = self.api_hash_entry.get().strip()
        if not api_id: return
        self.send_btn.config(state="disabled")
        threading.Thread(target=self.worker_broadcast, args=(int(api_id), api_hash), daemon=True).start()

    def worker_broadcast(self, api_id, api_hash):
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main_broadcast_task(api_id, api_hash))

    async def login_process(self, client):
        phone = self.safe_ask("Login", "เบอร์โทร (+...):")
        await client.send_code_request(phone)
        code = self.safe_ask("OTP", "รหัส 5 หลัก:")
        try: await client.sign_in(phone, code)
        except errors.SessionPasswordNeededError:
            pwd = self.safe_ask("2FA", "Cloud Password:", is_pwd=True)
            await client.sign_in(password=pwd)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path: self.image_path_var.set(path); self.img_label.config(text=os.path.basename(path))

    def write_log(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n"); self.log_area.see(tk.END)

    def safe_ask(self, title, prompt, is_pwd=False):
        res = [None]; event = threading.Event()
        def ask(): res[0] = simpledialog.askstring(title, prompt, parent=self.root, show="*" if is_pwd else None); event.set()
        self.root.after(0, ask); event.wait(); return res[0]

if __name__ == "__main__":
    root = tk.Tk(); app = TelegramMarketingPro(root); root.mainloop()