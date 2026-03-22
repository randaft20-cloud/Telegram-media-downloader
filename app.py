import customtkinter as ctk
from tkinter import filedialog
import asyncio
import threading
import os
from downloader import TelegramDownloader
from history import load_history, save_history

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Telegram Media Downloader")
        self.geometry("680x880")
        self.resizable(False, False)
        self.downloader = None
        self.loop = None
        self.channels = []
        self._build()

    def _build(self):
        # ── Credentials ──
        cred = ctk.CTkFrame(self)
        cred.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(cred, text="🔑 Credentials", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        for label, attr, placeholder in [
            ("API ID",   "api_id",   "123456"),
            ("API Hash", "api_hash", "abcdef..."),
            ("Phone",    "phone",    "+1234567890"),
        ]:
            row = ctk.CTkFrame(cred, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=label, width=80).pack(side="left")
            entry = ctk.CTkEntry(row, width=350, placeholder_text=placeholder)
            entry.pack(side="left", padx=5)
            setattr(self, attr, entry)

        login_row = ctk.CTkFrame(cred, fg_color="transparent")
        login_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(login_row, text="OTP Code", width=80).pack(side="left")
        self.otp = ctk.CTkEntry(login_row, width=150, placeholder_text="Check Telegram app")
        self.otp.pack(side="left", padx=5)
        self.otp_btn = ctk.CTkButton(login_row, text="Submit OTP", width=110, state="disabled", command=self.submit_otp)
        self.otp_btn.pack(side="left", padx=5)
        self.login_btn = ctk.CTkButton(login_row, text="🔐 Login", width=110, command=self.login)
        self.login_btn.pack(side="left", padx=10)

        # ── Channel ──
        ch_frame = ctk.CTkFrame(self)
        ch_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(ch_frame, text="📢 Channel / Group", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.channel_var = ctk.StringVar()
        self.channel_menu = ctk.CTkOptionMenu(ch_frame, variable=self.channel_var, values=["Login first..."], state="disabled", width=500)
        self.channel_menu.pack(padx=10, pady=5)

        # ── File Type ──
        type_frame = ctk.CTkFrame(self)
        type_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(type_frame, text="🗂 File Type Filter", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        self.media_type = ctk.StringVar(value="all")
        quick_row = ctk.CTkFrame(type_frame, fg_color="transparent")
        quick_row.pack(fill="x", padx=10)

        for label, value in [("All","all"),("Photos","photo"),("Videos","video"),("Audio","audio"),("PDF",".pdf"),("Word",".docx"),("Excel",".xlsx"),("ZIP",".zip"),("Custom","custom")]:
            ctk.CTkRadioButton(quick_row, text=label, variable=self.media_type, value=value).pack(side="left", padx=5)

        custom_row = ctk.CTkFrame(type_frame, fg_color="transparent")
        custom_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(custom_row, text="Custom:").pack(side="left")
        self.custom_ext = ctk.CTkEntry(custom_row, width=200, placeholder_text=".psd / .dwg / .pdf,.xlsx,.csv")
        self.custom_ext.pack(side="left", padx=8)
        self.custom_ext.bind("<Key>", lambda e: self.media_type.set("custom"))

        # ── Limit ──
        limit_frame = ctk.CTkFrame(self)
        limit_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(limit_frame, text="🔢 How Many Files", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        self.limit_mode = ctk.StringVar(value="all")
        limit_row = ctk.CTkFrame(limit_frame, fg_color="transparent")
        limit_row.pack(fill="x", padx=10)

        for label, value in [("Last 20","20"),("Last 50","50"),("Last 100","100"),("All","all"),("Custom","custom")]:
            ctk.CTkRadioButton(limit_row, text=label, variable=self.limit_mode, value=value).pack(side="left", padx=8)

        custom_limit_row = ctk.CTkFrame(limit_frame, fg_color="transparent")
        custom_limit_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(custom_limit_row, text="Custom number:").pack(side="left")
        self.custom_limit = ctk.CTkEntry(custom_limit_row, width=100, placeholder_text="e.g. 23")
        self.custom_limit.pack(side="left", padx=8)
        self.custom_limit.bind("<Key>", lambda e: self.limit_mode.set("custom"))

        # ── Download Order ──
        dir_frame = ctk.CTkFrame(self)
        dir_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(dir_frame, text="📅 Download Order", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        dir_row = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_row.pack(fill="x", padx=10, pady=5)
        self.reverse = ctk.BooleanVar(value=False)
        ctk.CTkRadioButton(dir_row, text="Newest → Oldest (default)", variable=self.reverse, value=False).pack(side="left", padx=10)
        ctk.CTkRadioButton(dir_row, text="Oldest → Newest", variable=self.reverse, value=True).pack(side="left", padx=10)

        # ── Folder ──
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(folder_frame, text="📁 Save To", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        folder_row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_row.pack(fill="x", padx=10)
        self.folder_path = ctk.StringVar(value=os.path.expanduser("~/Downloads/Telegram"))
        ctk.CTkEntry(folder_row, textvariable=self.folder_path, width=450).pack(side="left", padx=5)
        ctk.CTkButton(folder_row, text="Browse", width=80, command=self.browse).pack(side="left")

        # ── Buttons ──
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=8)
        self.start_btn  = ctk.CTkButton(btn_row, text="⬇ Start",  width=130, state="disabled", command=self.start_download)
        self.pause_btn  = ctk.CTkButton(btn_row, text="⏸ Pause",  width=130, state="disabled", command=self.pause)
        self.cancel_btn = ctk.CTkButton(btn_row, text="⛔ Cancel", width=130, state="disabled", fg_color="red", command=self.cancel)
        for btn in [self.start_btn, self.pause_btn, self.cancel_btn]:
            btn.pack(side="left", padx=8)

        # ── Progress ──
        self.progress = ctk.CTkProgressBar(self, width=620)
        self.progress.pack(padx=15, pady=4)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(self, text="Ready")
        self.progress_label.pack()

        # ── Tabs ──
        tab = ctk.CTkTabview(self)
        tab.pack(fill="both", expand=True, padx=15, pady=5)
        tab.add("📋 Log")
        tab.add("🕘 History")

        self.log_box = ctk.CTkTextbox(tab.tab("📋 Log"), font=("Courier", 11))
        self.log_box.pack(fill="both", expand=True)

        self.history_box = ctk.CTkTextbox(tab.tab("🕘 History"), font=("Courier", 11))
        self.history_box.pack(fill="both", expand=True)
        self._load_history_tab()

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def log(self, msg):
        self.after(0, self._log_safe, msg)

    def _log_safe(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _load_history_tab(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        for h in reversed(load_history()):
            self.history_box.insert("end",
                f"📅 {h['date']}  |  📢 {h['channel']}  |  ✅ {h['files']} files  |  📁 {h['folder']}\n"
            )
        self.history_box.configure(state="disabled")

    def login(self):
        api_id   = self.api_id.get().strip()
        api_hash = self.api_hash.get().strip()
        phone    = self.phone.get().strip()

        if not api_id or not api_hash or not phone:
            self.log("❌ Please fill in API ID, API Hash and Phone first.")
            return

        self.loop = asyncio.new_event_loop()
        self.downloader = TelegramDownloader(int(api_id), api_hash, phone)
        self.after(0, lambda: self.login_btn.configure(state="disabled"))
        self.log("🔄 Connecting to Telegram...")
        threading.Thread(
            target=lambda: self.loop.run_until_complete(self._async_login()),
            daemon=True
        ).start()

    async def _async_login(self):
        try:
            await self.downloader.client.connect()
            if not await self.downloader.client.is_user_authorized():
                await self.downloader.client.send_code_request(self.downloader.phone)
                self.log("📱 OTP sent to your Telegram app! Enter it and click Submit OTP.")
                self.after(0, lambda: self.otp_btn.configure(state="normal"))
                self.downloader.otp_future = self.loop.create_future()
                code = await self.downloader.otp_future
                await self.downloader.client.sign_in(self.downloader.phone, code)

            self.log("✅ Logged in successfully!")
            self.after(0, lambda: self.otp_btn.configure(state="disabled"))

            channels = await self.downloader.get_channels()
            self.channels = channels
            names = [f"{'📢' if c.is_channel else '👥'} {c.name}" for c in channels]

            self.after(0, lambda: self.channel_menu.configure(values=names, state="normal"))
            self.after(0, lambda: self.channel_menu.set(names[0]))
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.login_btn.configure(state="normal"))
            self.log(f"📋 {len(channels)} channels & groups loaded.")

        except Exception as e:
            self.log(f"❌ Login error: {e}")
            self.after(0, lambda: self.login_btn.configure(state="normal"))

    def submit_otp(self):
        code = self.otp.get().strip()
        if code and self.downloader and self.downloader.otp_future:
            self.loop.call_soon_threadsafe(self.downloader.otp_future.set_result, code)
            self.after(0, lambda: self.otp_btn.configure(state="disabled"))
            self.log("✅ OTP submitted.")
        else:
            self.log("❌ No OTP entered or login not started.")

    def start_download(self):
        idx = next(
            i for i, c in enumerate(self.channels)
            if f"{'📢' if c.is_channel else '👥'} {c.name}" == self.channel_var.get()
        )
        selected = self.channels[idx]

        selected_type = self.media_type.get()
        if selected_type == "custom":
            selected_type = self.custom_ext.get().strip().lower() or None

        limit_mode = self.limit_mode.get()
        custom_limit = int(self.custom_limit.get()) if limit_mode == "custom" and self.custom_limit.get().isdigit() else 20

        folder = os.path.join(self.folder_path.get(), selected.name.replace("/", "_"))

        self.after(0, lambda: self.progress.set(0))
        self.after(0, lambda: self.progress_label.configure(text="Starting..."))
        self.after(0, lambda: self.start_btn.configure(state="disabled"))
        self.after(0, lambda: self.pause_btn.configure(state="normal"))
        self.after(0, lambda: self.cancel_btn.configure(state="normal"))

        def on_progress(count, skipped, fraction):
            self.after(0, lambda: self.progress_label.configure(
                text=f"✅ {count} downloaded  |  ⏭ {skipped} skipped"
            ))
            self.after(0, lambda: self.progress.set(min(fraction, 1.0)))

        def on_done(count, skipped):
            save_history(selected.name, folder, count)
            self.after(0, self._load_history_tab)
            self.log(f"\n🎉 Done! {count} downloaded, {skipped} skipped.")
            self.log(f"📁 Saved to: {os.path.abspath(folder)}")
            self.after(0, lambda: self.progress.set(1))
            self.after(0, lambda: self.progress_label.configure(text=f"✅ Complete — {count} files"))
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.pause_btn.configure(state="disabled"))
            self.after(0, lambda: self.cancel_btn.configure(state="disabled"))

        threading.Thread(
            target=lambda: self.loop.run_until_complete(
                self.downloader.download(
                    selected, folder, selected_type,
                    limit_mode, custom_limit,
                    self.reverse.get(),
                    on_progress, self.log, on_done
                )
            ), daemon=True
        ).start()

    def pause(self):
        self.downloader.paused = not self.downloader.paused
        label = "▶ Resume" if self.downloader.paused else "⏸ Pause"
        self.after(0, lambda: self.pause_btn.configure(text=label))
        self.log("⏸ Paused." if self.downloader.paused else "▶ Resumed.")

    def cancel(self):
        self.downloader.cancelled = True
        self.log("⛔ Cancelling...")
        self.after(0, lambda: self.pause_btn.configure(state="disabled"))
        self.after(0, lambda: self.cancel_btn.configure(state="disabled"))
        self.after(0, lambda: self.start_btn.configure(state="normal"))
