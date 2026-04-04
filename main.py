import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os
import sys

# Check if pyperclip is installed, if not, provide a fallback or instruct user.
try:
    import pyperclip
except ImportError:
    print("pyperclip not found. Please install it using 'pip install pyperclip' for clipboard functionality.")
    pyperclip = None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("☁️ Accounting Prog for Lazy People ☁️") # Set a default size
        self.root.geometry("1200x900") # Increased size for better fit
        self.root.config(bg="#F0F4FF") # Soft Blue-Lavender background

        # --- Set App Icon (รูปดาวบนมุมซ้ายบนและ Taskbar) ---
        icon_path = self.get_resource_path("star.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(default=icon_path)
            except Exception:
                pass

        # --- Modern, Minimalist, Futuristic Style Setup ---
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        
        # --- Cute Blue & Purple Pastel Theme ---
        self.style.configure(".", background="#F0F4FF", foreground="#605C88", font=("Mali", 10)) # Dark dusty purple text
        self.style.configure("TButton", padding=8, relief="flat", background="#D6E0FF", borderwidth=0, focuscolor="#D6E0FF") # Pastel Blue
        self.style.map("TButton", background=[("active", "#C2D3FF")], foreground=[("active", "#605C88")])
        self.style.configure("Danger.TButton", foreground="#FFFFFF", background="#FFD1DC", font=("Mali", 10, "bold")) # Pastel Pink for danger
        self.style.map("Danger.TButton", background=[("active", "#FFB6C1")])
        self.style.configure("Header.TLabel", font=("Mali", 12, "bold"), background="#F0F4FF", foreground="#847BB9") # Purple header text
        self.style.configure("Search.TLabel", font=("Mali", 10, "bold"), background="#F0F4FF", foreground="#847BB9")
        self.style.configure("Sub.TLabel", font=("Mali", 10, "bold"), background="#E3D7FF", foreground="#605C88", padding=5) # Pastel Purple sub label
        self.style.configure("TCheckbutton", background="#F0F4FF", focuscolor="#F0F4FF")
        self.style.map("TCheckbutton", background=[("active", "#F0F4FF")])
        self.style.configure("TRadiobutton", background="#F0F4FF", focuscolor="#F0F4FF")
        self.style.map("TRadiobutton", background=[("active", "#F0F4FF")])
        self.style.configure("TLabelframe", background="#F0F4FF")
        self.style.configure("TLabelframe.Label", font=("Mali", 10, "bold"), background="#F0F4FF", foreground="#847BB9")
        self.style.configure("Card.TButton", background="#FFFFFF", padding=8, relief="flat") # White buttons for items
        self.style.map("Card.TButton", background=[("active", "#F0F4FF")], foreground=[("active", "#605C88")])

        self.themes = {
            "pastel": {
                "bg": "#F0F4FF", "fg": "#605C88", "btn_bg": "#D6E0FF", "btn_active": "#C2D3FF",
                "danger_bg": "#FFD1DC", "danger_active": "#FFB6C1", "header_fg": "#847BB9",
                "sub_bg": "#E3D7FF", "card_bg": "#FFFFFF", "border": "#D0C4FF",
                "col_details": "#E6F0FF", "col_link": "#EBE3FF", "col_month_year": "#FFF5D1",
                "text_bg": "#FFFFFF", "handle": "#847BB9", "handle_search": "#C2D3FF"
            },
            "dark": {
                "bg": "#1E1E2E", "fg": "#CDD6F4", "btn_bg": "#313244", "btn_active": "#45475A",
                "danger_bg": "#F38BA8", "danger_active": "#EBA0AC", "header_fg": "#B4BEFE",
                "sub_bg": "#45475A", "card_bg": "#181825", "border": "#585B70",
                "col_details": "#242536", "col_link": "#282436", "col_month_year": "#2E2A24",
                "text_bg": "#11111B", "handle": "#A6ADC8", "handle_search": "#45475A"
            }
        }
        self.load_settings()
        self.data_file = "account_data.json"
        self.details_data = [] # Stores all the detail dictionaries
        self.load_data() # โหลดข้อมูลตอนเริ่มต้นโปรแกรม
        self.currently_displayed_detail = None # Keep track of the last detail clicked
        self.drag_window = None # หน้าต่างสำหรับแสดงผลจำลองตอนที่กำลังลาก

        # --- Main Layout Frames ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.config(bg="#F0F4FF")

        # --- Search Frame ---
        self.search_frame = tk.Frame(self.main_frame, bg="#F0F4FF")
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.search_frame, text="🔍 ค้นหา (Search):", font=("Mali", 10, "bold"), style="Search.TLabel").pack(side=tk.LEFT, padx=(5, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, font=("Mali", 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.theme_btn = ttk.Button(self.search_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))
        self.header_frame.config(bg="#F0F4FF")

        self.columns_container_frame = tk.Frame(self.main_frame)
        self.columns_container_frame.pack(fill=tk.BOTH, expand=True)
        self.columns_container_frame.config(bg="#F0F4FF")

        self.add_button_frame = tk.Frame(self.main_frame)
        self.add_button_frame.pack(fill=tk.X, pady=(5, 0))
        self.add_button_frame.config(bg="#F0F4FF")

        # Frame for display areas and control buttons
        self.display_control_frame = tk.Frame(self.main_frame, bd=0, highlightthickness=2, highlightbackground="#D0C4FF", highlightcolor="#D0C4FF") # Pastel purple border
        self.display_control_frame.pack(fill=tk.X, pady=(10, 0))
        self.display_control_frame.config(bg="#F0F4FF")

        self.display_frame = tk.Frame(self.display_control_frame)
        self.display_frame.pack(fill=tk.X, pady=(10, 0))
        self.display_frame.config(bg="#F0F4FF")
        # --- Header Labels for Columns ---
        ttk.Label(self.header_frame, text="✨ รายละเอียด ✨", style="Header.TLabel").pack(side=tk.LEFT, expand=True)
        ttk.Label(self.header_frame, text="☁️ คำเชื่อม ☁️", style="Header.TLabel").pack(side=tk.LEFT, expand=True)
        ttk.Label(self.header_frame, text="❄️ เดือน ปี ❄️", style="Header.TLabel").pack(side=tk.LEFT, expand=True)

        # --- Columns (Scrollable) ---
        self.column_frames = {}
        column_names = ["details", "link", "month_year"]
        column_colors = {"details": "#E6F0FF", "link": "#EBE3FF", "month_year": "#FFF5D1"} # Pastel Blue, Purple, Yellow

        for name in column_names:
            col_bg = column_colors[name]
            col_frame = tk.Frame(self.columns_container_frame, bd=0, highlightthickness=2, highlightbackground="#D0C4FF") # Purple border
            col_frame.config(bg=col_bg)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5) # More padding between cute columns
            self.column_frames[name] = col_frame

            canvas = tk.Canvas(col_frame, bg=col_bg, highlightthickness=0)
            scrollable_frame = tk.Frame(canvas, bg=col_bg)
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            scrollbar = ttk.Scrollbar(col_frame, orient="vertical", command=canvas.yview)

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Store the inner scrollable frame and canvas for adding widgets
            setattr(self, f"{name}_inner_frame", scrollable_frame)
            setattr(self, f"{name}_canvas", canvas)

        # --- Add Item Buttons for each column (using ttk.Button for modern look) ---
        ttk.Button(self.add_button_frame, text="เพิ่มรายละเอียด (Details)",
                   command=lambda: self.show_add_item_form('details')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(self.add_button_frame, text="เพิ่มคำเชื่อม (Link)",
                   command=lambda: self.show_add_item_form('link')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(self.add_button_frame, text="เพิ่มเดือน ปี (Month Year)",
                   command=lambda: self.show_add_item_form('month_year')).pack(side=tk.LEFT, expand=True, padx=2)

        # --- Global Delete Button ---
        self.delete_button_frame = tk.Frame(self.main_frame, bg="#F0F4FF")
        self.delete_button_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(self.delete_button_frame, text="ลบรายการที่เลือก (Delete Selected Items)",
                   command=self.show_delete_selection_form, style='Danger.TButton').pack(pady=5)

        # --- Display Areas ---
        self.display_content_frame = tk.Frame(self.display_control_frame)
        self.display_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.display_content_frame.config(bg="#F0F4FF")

        # History for main display area
        self.display_history_states = []
        self.current_history_state_index = -1

        # Control buttons for display area
        self.display_buttons_frame = tk.Frame(self.display_control_frame, bg="#F0F4FF")
        self.display_buttons_frame.pack(fill=tk.X, pady=(5, 0), padx=5)
        ttk.Button(self.display_buttons_frame, text="Reset", command=self.reset_display).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.display_buttons_frame, text="Undo", command=lambda: self.navigate_history(-1)).pack(side=tk.LEFT, padx=2) # Navigate back in history
        ttk.Button(self.display_buttons_frame, text="Redo", command=lambda: self.navigate_history(1)).pack(side=tk.LEFT, padx=2) # Navigate forward in history

        # Main Display Area (copyable)
        self.main_display_area_frame = tk.Frame(self.display_content_frame, bd=0, highlightthickness=2, highlightbackground="#D0C4FF")
        self.main_display_area_frame.config(bg="#F0F4FF") 
        self.main_display_area_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(self.main_display_area_frame, text="ข้อมูลที่แสดงผล (Copyable):", style="Sub.TLabel", anchor="w").pack(fill=tk.X, pady=(0, 2))

        self.display_text_area = tk.Text(self.main_display_area_frame, height=5, wrap=tk.WORD, state=tk.NORMAL, bd=0, font=("Mali", 10), padx=10, pady=10, fg="#605C88")
        self.display_text_area.config(bg="#FFFFFF") # Pure white for text area
        
        # Adorable Welcome Text
        self.display_text_area.insert("1.0", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ยินดีต้อนรับสู่โปรแกรมคนขี้เกียจ~ ☁️❄️\nกดปุ่มด้านบนเพื่อเริ่มเพิ่มข้อมูลได้เลย!")
        self.display_text_area.config(state=tk.DISABLED)

        self.display_text_area.pack(fill=tk.BOTH, expand=True)
        self.display_text_area.bind("<Button-1>", self.copy_to_clipboard)

        self.copied_message_label = tk.Label(self.main_display_area_frame, text="", fg="#82C7A5", bg="#FFFFFF", font=("Mali", 9)) # Pastel green color, white bg
        self.copied_message_label.pack(fill=tk.X, pady=(2,0))

        # Side Display Area (non-copyable)
        self.side_display_area_frame = tk.Frame(self.display_content_frame, width=250, bd=0, highlightthickness=2, highlightbackground="#D0C4FF") 
        self.side_display_area_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        self.side_display_area_frame.pack_propagate(False) # Prevent frame from resizing to content

        ttk.Label(self.side_display_area_frame, text="รายละเอียดเพิ่มเติม (Non-Copyable):", style="Sub.TLabel", anchor="w").pack(fill=tk.X, pady=(0, 2), padx=5)

        self.side_details_text = tk.Text(self.side_display_area_frame, height=5, wrap=tk.WORD, state=tk.DISABLED, bd=0, font=("Mali", 10), padx=10, pady=10, fg="#605C88")
        self.side_details_text.config(bg="#FFFFFF") # Pure white for text area
        self.side_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        # Apply initial theme and populate columns
        self.apply_theme()
        
    def get_resource_path(self, relative_path):
        """ฟังก์ชันสำหรับหาตำแหน่งไฟล์ รองรับทั้งตอนเป็นโค้ด .py และตอนเป็นโปรแกรม .exe"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def load_data(self):
        """โหลดข้อมูลจากไฟล์ JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.details_data = json.load(f)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

    def save_data(self):
        """บันทึกข้อมูลลงไฟล์ JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.details_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")

    def load_settings(self):
        self.settings = {"theme": "pastel"}
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
            except:
                pass

    def save_settings(self):
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f)
        except:
            pass

    def toggle_theme(self):
        self.settings["theme"] = "dark" if self.settings.get("theme", "pastel") == "pastel" else "pastel"
        self.save_settings()
        self.apply_theme()

    def apply_theme(self):
        th = self.themes[self.settings.get("theme", "pastel")]
        
        self.root.config(bg=th["bg"])
        self.main_frame.config(bg=th["bg"])
        self.search_frame.config(bg=th["bg"])
        self.header_frame.config(bg=th["bg"])
        self.columns_container_frame.config(bg=th["bg"])
        self.add_button_frame.config(bg=th["bg"])
        self.display_control_frame.config(bg=th["bg"], highlightbackground=th["border"], highlightcolor=th["border"])
        self.display_frame.config(bg=th["bg"])
        self.delete_button_frame.config(bg=th["bg"])
        self.display_content_frame.config(bg=th["bg"])
        self.display_buttons_frame.config(bg=th["bg"])
        self.main_display_area_frame.config(bg=th["bg"], highlightbackground=th["border"])
        self.display_text_area.config(bg=th["text_bg"], fg=th["fg"])
        self.side_display_area_frame.config(bg=th["bg"], highlightbackground=th["border"])
        self.side_details_text.config(bg=th["text_bg"], fg=th["fg"])
        self.copied_message_label.config(bg=th["text_bg"])

        for name in ["details", "link", "month_year"]:
            col_bg = th[f"col_{name}"]
            if name in self.column_frames:
                self.column_frames[name].config(bg=col_bg, highlightbackground=th["border"])
            if hasattr(self, f"{name}_canvas"):
                getattr(self, f"{name}_canvas").config(bg=col_bg)
            if hasattr(self, f"{name}_inner_frame"):
                getattr(self, f"{name}_inner_frame").config(bg=col_bg)

        self.style.configure(".", background=th["bg"], foreground=th["fg"])
        self.style.configure("TButton", background=th["btn_bg"], focuscolor=th["btn_bg"])
        self.style.map("TButton", background=[("active", th["btn_active"])], foreground=[("active", th["fg"])])
        self.style.configure("Danger.TButton", foreground="#FFFFFF", background=th["danger_bg"])
        self.style.map("Danger.TButton", background=[("active", th["danger_active"])])
        self.style.configure("Header.TLabel", background=th["bg"], foreground=th["header_fg"])
        self.style.configure("Search.TLabel", background=th["bg"], foreground=th["header_fg"])
        self.style.configure("Sub.TLabel", background=th["sub_bg"], foreground=th["fg"])
        self.style.configure("TCheckbutton", background=th["bg"], focuscolor=th["bg"])
        self.style.map("TCheckbutton", background=[("active", th["bg"])])
        self.style.configure("TRadiobutton", background=th["bg"], focuscolor=th["bg"])
        self.style.map("TRadiobutton", background=[("active", th["bg"])])
        self.style.configure("TLabelframe", background=th["bg"])
        self.style.configure("TLabelframe.Label", background=th["bg"], foreground=th["header_fg"])
        self.style.configure("Card.TButton", background=th["card_bg"])
        self.style.map("Card.TButton", background=[("active", th["bg"])], foreground=[("active", th["fg"])])

        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="🌙 Dark Mode" if self.settings.get("theme") == "pastel" else "☀️ Light Mode")

        self._clear_and_repopulate_columns()

    def show_add_item_form(self, column_type):
        th = self.themes[self.settings.get("theme", "pastel")]
        form_window = tk.Toplevel(self.root)
        form_window.title(f"เพิ่มรายการในคอลัมน์: {column_type.replace('_', ' ').title()}")
        form_window.transient(self.root) # Make it appear on top of the main window
        form_window.grab_set() # Make it modal
        
        # Calculate position to center the window
        dialog_width = 400
        dialog_height = 460 if column_type == 'details' else 200
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dialog_width // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dialog_height // 2)
        form_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        form_window.config(bg=th["bg"]) # Apply background color
        # Labels and Entry widgets
        ttk.Label(form_window, text="ชื่อปุ่ม (Button Name):").pack(pady=5)
        button_name_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
        button_name_entry.pack(pady=2)

        ttk.Label(form_window, text="รายละเอียด (Description):").pack(pady=5)
        description_entry = None
        account_entry = None
        credit_type_var = None

        if column_type == 'details':
            description_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
            description_entry.pack(pady=2)

            ttk.Label(form_window, text="เลขบัญชี (Account Number):").pack(pady=5)
            account_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
            account_entry.pack(pady=2)

            ttk.Label(form_window, text="เครดิต (Credit Type):").pack(pady=5)
            credit_type_var = tk.StringVar(form_window, value="เงินสด") # Default value
            ttk.Radiobutton(form_window, text="เงินสด (Cash)", variable=credit_type_var, value="เงินสด").pack(anchor=tk.W, padx=10)
            ttk.Radiobutton(form_window, text="เงินฝาก (Deposit)", variable=credit_type_var, value="เงินฝาก").pack(anchor=tk.W, padx=10)
            ttk.Radiobutton(form_window, text="อื่นๆ (Other)", variable=credit_type_var, value="อื่นๆ").pack(anchor=tk.W, padx=10)
        else:
            # For 'link' and 'month_year', the button name is the description, no separate description entry needed.
            # The "รายละเอียด (Description):" label is not packed for these types.
            pass

        # Save Button
        save_button = ttk.Button(form_window, text="บันทึก (Save)",
                                 command=lambda: self.save_item(form_window, column_type,
                                                                button_name_entry, description_entry,
                                                                account_entry, credit_type_var))
        save_button.pack(pady=10)

        form_window.wait_window() # Wait for the form to close before continuing

    def save_item(self, form_window, column_type, button_name_entry, description_entry, account_entry, credit_type_var):
        button_name = button_name_entry.get().strip()

        if not button_name:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกชื่อปุ่ม")
            return

        detail = {
            'button_name': button_name,
            'column_type': column_type,
        }

        if column_type == 'details':
            detail['description'] = description_entry.get().strip() if description_entry else ""
            detail['account_number'] = account_entry.get().strip() if account_entry else ""
            detail['credit_type'] = credit_type_var.get() if credit_type_var else ""
        else: # For 'link' and 'month_year', the button_name is the description
            detail['description'] = button_name

        self.details_data.append(detail)

        self.save_data() # บันทึกข้อมูลหลังเพิ่มเสร็จ
        self._clear_and_repopulate_columns() # Rebuild all columns after adding
        form_window.destroy()

    def show_edit_item_form(self, detail):
        th = self.themes[self.settings.get("theme", "pastel")]
        form_window = tk.Toplevel(self.root)
        column_type = detail['column_type']
        form_window.title(f"แก้ไขรายการ: {column_type.replace('_', ' ').title()}")
        form_window.transient(self.root) # Make it appear on top of the main window
        form_window.grab_set() # Make it modal
        
        # Calculate position to center the window
        dialog_width = 400
        dialog_height = 460 if column_type == 'details' else 200
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dialog_width // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dialog_height // 2)
        form_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        form_window.config(bg=th["bg"]) # Apply background color
        # Labels and Entry widgets
        ttk.Label(form_window, text="ชื่อปุ่ม (Button Name):").pack(pady=5)
        button_name_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
        button_name_entry.insert(0, detail.get('button_name', ''))
        button_name_entry.pack(pady=2)

        description_entry = None
        account_entry = None
        credit_type_var = None

        if column_type == 'details':
            ttk.Label(form_window, text="รายละเอียด (Description):").pack(pady=5)
            description_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
            description_entry.insert(0, detail.get('description', ''))
            description_entry.pack(pady=2)

            ttk.Label(form_window, text="เลขบัญชี (Account Number):").pack(pady=5)
            account_entry = ttk.Entry(form_window, width=40, font=("Mali", 10))
            account_entry.insert(0, detail.get('account_number', ''))
            account_entry.pack(pady=2)

            ttk.Label(form_window, text="เครดิต (Credit Type):").pack(pady=5)
            credit_type_var = tk.StringVar(form_window, value=detail.get('credit_type', 'เงินสด'))
            ttk.Radiobutton(form_window, text="เงินสด (Cash)", variable=credit_type_var, value="เงินสด").pack(anchor=tk.W, padx=10)
            ttk.Radiobutton(form_window, text="เงินฝาก (Deposit)", variable=credit_type_var, value="เงินฝาก").pack(anchor=tk.W, padx=10)
            ttk.Radiobutton(form_window, text="อื่นๆ (Other)", variable=credit_type_var, value="อื่นๆ").pack(anchor=tk.W, padx=10)

        # Update Button
        update_button = ttk.Button(form_window, text="อัปเดต (Update)",
                                 command=lambda: self.update_item(form_window, detail, column_type,
                                                                button_name_entry, description_entry,
                                                                account_entry, credit_type_var))
        update_button.pack(pady=10)

        form_window.wait_window()

    def update_item(self, form_window, detail, column_type, button_name_entry, description_entry, account_entry, credit_type_var):
        button_name = button_name_entry.get().strip()

        if not button_name:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกชื่อปุ่ม")
            return

        detail['button_name'] = button_name

        if column_type == 'details':
            detail['description'] = description_entry.get().strip() if description_entry else ""
            detail['account_number'] = account_entry.get().strip() if account_entry else ""
            detail['credit_type'] = credit_type_var.get() if credit_type_var else ""
        else:
            detail['description'] = button_name

        self.save_data() # บันทึกข้อมูลหลังแก้ไขเสร็จ
        self._clear_and_repopulate_columns() # Rebuild all columns after update
        
        # อัปเดตการแสดงผลด้านข้างหากรายการที่ถูกแก้ไขกำลังแสดงอยู่
        if self.currently_displayed_detail == detail and column_type == 'details':
            self.side_details_text.config(state=tk.NORMAL)
            self.side_details_text.delete("1.0", tk.END)
            side_text = f"ชื่อปุ่ม: {detail['button_name']}\n" \
                        f"เลขบัญชี: {detail['account_number']}\n" \
                        f"เครดิต: {detail['credit_type']}\n" \
                        f"{'-'*30}\n"
            self.side_details_text.insert(tk.END, side_text)
            self.side_details_text.config(state=tk.DISABLED)

        form_window.destroy()

    def add_button_to_column(self, detail, target_frame, target_canvas):
        col_bg = target_frame.cget("bg")
        item_frame = tk.Frame(target_frame, bg=col_bg)
        item_frame.pack(pady=4, padx=8, fill=tk.X)

        th = self.themes[self.settings.get("theme", "pastel")]
        is_searching = bool(self.search_var.get().strip())
        cursor_type = "arrow" if is_searching else "fleur"
        handle_color = th["handle_search"] if is_searching else th["handle"]

        # Drag handle (จุดจับสำหรับลาก)
        drag_handle = tk.Label(item_frame, text="☰", cursor=cursor_type, bg=col_bg, fg=handle_color, font=("Mali", 12))
        drag_handle.pack(side=tk.LEFT, padx=(0, 5))

        # ปุ่มไอคอนแก้ไข (Edit)
        edit_btn = tk.Label(item_frame, text="✏️", cursor="hand2", bg=col_bg, fg=th["header_fg"], font=("Mali", 10))
        edit_btn.pack(side=tk.RIGHT, padx=(5, 0))
        edit_btn.bind("<Button-1>", lambda e, d=detail: self.show_edit_item_form(d))

        btn = ttk.Button(item_frame, text=detail['button_name'],
                        command=lambda d=detail: self.on_detail_button_click(d),
                        style="Card.TButton") # White cards inside pastel columns
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ผูก Event สำหรับการลาก (Drag & Drop) เข้ากับจุดจับ (Drag handle)
        if not is_searching:
            drag_handle.bind("<ButtonPress-1>", lambda e, d=detail, f=target_frame: self.start_drag(e, d, f))
            drag_handle.bind("<B1-Motion>", self.do_drag)
            drag_handle.bind("<ButtonRelease-1>", lambda e, d=detail, f=target_frame: self.stop_drag(e, d, f))
        else:
            drag_handle.bind("<ButtonPress-1>", lambda e: messagebox.showinfo("แจ้งเตือน", "กรุณาลบคำค้นหาก่อนทำการลากสลับตำแหน่ง"))

        # Update the scroll region of the canvas
        target_canvas.update_idletasks() # Ensure widgets are drawn before calculating bbox
        target_canvas.config(scrollregion=target_canvas.bbox("all"))

    def on_search(self, event=None):
        self._clear_and_repopulate_columns()

    def _clear_and_repopulate_columns(self):
        """Clears all column frames and repopulates them based on self.details_data."""
        search_query = self.search_var.get().strip().lower()

        for name in ["details", "link", "month_year"]:
            inner_frame = getattr(self, f"{name}_inner_frame")
            canvas = getattr(self, f"{name}_canvas")

            # Clear existing widgets
            for widget in inner_frame.winfo_children():
                widget.destroy()

            # Repopulate
            for detail in self.details_data:
                if detail['column_type'] == name:
                    if search_query:
                        searchable_text = f"{detail.get('button_name', '')} {detail.get('description', '')} {detail.get('account_number', '')}".lower()
                        if search_query not in searchable_text:
                            continue # ข้ามปุ่มนี้ถ้าไม่ตรงกับคำค้นหา

                    self.add_button_to_column(detail, inner_frame, canvas)

            # Update scroll region after repopulating
            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

    def start_drag(self, event, detail, target_frame):
        """เริ่มการลาก (Drag)"""
        self.drag_window = tk.Toplevel(self.root)
        self.drag_window.overrideredirect(True) # ซ่อนกรอบหน้าต่าง
        self.drag_window.attributes('-alpha', 0.8) # ทำให้โปร่งใสเล็กน้อย
        
        # สร้างปุ่มจำลองขึ้นมาในหน้าต่างลอย
        lbl = tk.Label(self.drag_window, text=detail['button_name'], font=("Mali", 10), bg="#FFFFFF", fg="#605C88", padx=10, pady=5, relief="solid", bd=1)
        lbl.pack()
        
        # ให้ตำแหน่งเริ่มต้นตรงกับเมาส์
        x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        self.drag_window.geometry(f"+{x+10}+{y+10}")

    def do_drag(self, event):
        """อัปเดตตำแหน่งหน้าต่างจำลองตามเมาส์ขณะลาก"""
        if self.drag_window:
            x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
            self.drag_window.geometry(f"+{x+10}+{y+10}")

    def stop_drag(self, event, detail, target_frame):
        """สิ้นสุดการลาก เลื่อนข้อมูลไปตำแหน่งใหม่และบันทึก"""
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None

        # คำนวณหาตำแหน่งแกน Y ที่เมาส์ปล่อยลงมาเทียบกับกรอบแสดงผลด้านใน
        y_relative = target_frame.winfo_pointery() - target_frame.winfo_rooty()
        children = target_frame.winfo_children()
        drop_index = len(children)
        
        for i, child in enumerate(children):
            if y_relative < child.winfo_y() + (child.winfo_height() / 2):
                drop_index = i
                break

        col_type = detail['column_type']
        col_items = [d for d in self.details_data if d['column_type'] == col_type]
        
        if detail in col_items:
            current_index = col_items.index(detail)
            col_items.remove(detail)
            
            if drop_index > current_index:
                drop_index -= 1 # ปรับ index หากเราลากลงมาด้านล่าง
                
            col_items.insert(drop_index, detail)

            # อัปเดตข้อมูล self.details_data โดยรักษารายการในคอลัมน์อื่นไว้เหมือนเดิม
            self.details_data = [d for d in self.details_data if d['column_type'] != col_type] + col_items
            
            self.save_data() # บันทึกลง JSON
            self._clear_and_repopulate_columns() # โหลดคอลัมน์ใหม่

    def show_delete_selection_form(self):
        th = self.themes[self.settings.get("theme", "pastel")]
        delete_form_window = tk.Toplevel(self.root)
        delete_form_window.title("เลือกรายการที่จะลบ (Select Items to Delete)")
        delete_form_window.transient(self.root)
        delete_form_window.grab_set()
        
        # Calculate position to center the window
        dialog_width = 600
        dialog_height = 700
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dialog_width // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dialog_height // 2)
        delete_form_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        delete_form_window.config(bg=th["bg"])

        main_frame = tk.Frame(delete_form_window, bg=th["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable area for checkboxes
        canvas = tk.Canvas(main_frame, bg=th["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=th["bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.delete_checkboxes = [] # Stores (BooleanVar, detail) tuples

        # Group by column type
        grouped_details = {
            "details": [],
            "link": [],
            "month_year": []
        }
        for detail in self.details_data:
            grouped_details[detail['column_type']].append(detail)

        column_names_thai = {
            "details": "รายละเอียด",
            "link": "คำเชื่อม",
            "month_year": "เดือน ปี"
        }

        for col_type, details_list in grouped_details.items():
            if details_list:
                # เปลี่ยนไปใช้ ttk.LabelFrame แทน tk ธรรมดา เพื่อให้รองรับ TLabelframe.Label padding ที่ตั้งค่าไว้
                type_frame = ttk.LabelFrame(scrollable_frame, text=f"หมวดหมู่: {column_names_thai[col_type]}")
                type_frame.pack(fill=tk.X, pady=5, padx=5)

                # Check All in Type button
                btn_frame = tk.Frame(type_frame, bg=th["bg"])
                btn_frame.pack(fill=tk.X, pady=(0, 5))
                ttk.Button(btn_frame, text=f"เลือกทั้งหมด",
                           command=lambda ct=col_type: self._toggle_type_checkboxes(ct, True)).pack(side=tk.LEFT, padx=2, pady=2)
                ttk.Button(btn_frame, text=f"ยกเลิกทั้งหมด",
                           command=lambda ct=col_type: self._toggle_type_checkboxes(ct, False)).pack(side=tk.LEFT, padx=2, pady=2)

                for detail in details_list:
                    var = tk.BooleanVar(value=False)
                    chk = ttk.Checkbutton(type_frame, text=detail['button_name'], variable=var)
                    chk.pack(fill=tk.X, padx=10, pady=1)
                    self.delete_checkboxes.append((var, detail))

        # Control buttons at the bottom of the delete form
        control_frame = tk.Frame(delete_form_window, bg=th["bg"])
        control_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(control_frame, text="เลือกทั้งหมด (Check All)", command=lambda: self._toggle_all_checkboxes(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="ยกเลิกทั้งหมด (Uncheck All)", command=lambda: self._toggle_all_checkboxes(False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="ยืนยันการลบ (Confirm Delete)", command=lambda: self._confirm_delete_selected(delete_form_window), style='Danger.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="ยกเลิก (Cancel)", command=delete_form_window.destroy).pack(side=tk.RIGHT, padx=5)

    def _toggle_all_checkboxes(self, state):
        for var, _ in self.delete_checkboxes:
            var.set(state)

    def _toggle_type_checkboxes(self, column_type, state):
        for var, detail in self.delete_checkboxes:
            if detail['column_type'] == column_type:
                var.set(state)

    def _confirm_delete_selected(self, delete_form_window):
        details_to_remove = []
        for var, detail in self.delete_checkboxes:
            if var.get():
                details_to_remove.append(detail)

        if not details_to_remove:
            messagebox.showinfo("ไม่มีรายการ", "กรุณาเลือกรายการที่จะลบ")
            return

        if messagebox.askyesno("ยืนยันการลบ", f"คุณแน่ใจหรือไม่ที่จะลบ {len(details_to_remove)} รายการ?"):
            for detail_to_delete in details_to_remove:
                if detail_to_delete in self.details_data:
                    self.details_data.remove(detail_to_delete)
                    # If the deleted item was the one currently displayed, clear the display
                    if self.currently_displayed_detail == detail_to_delete:
                        self.reset_display()

            self.save_data() # บันทึกข้อมูลหลังลบเสร็จ
            self._clear_and_repopulate_columns() # Rebuild all columns after deletion
            delete_form_window.destroy()
            messagebox.showinfo("ลบสำเร็จ", f"ลบ {len(details_to_remove)} รายการเรียบร้อยแล้ว")
        else:
            messagebox.showinfo("ยกเลิก", "การลบถูกยกเลิก")

    def on_detail_button_click(self, detail):
        # Get current content of main display area
        self.currently_displayed_detail = detail # Store the currently displayed detail

        current_main_content = self.display_text_area.get("1.0", tk.END).strip()

        # Determine the text to append to the main display
        display_text_main = ""
        if detail['column_type'] == 'details':
            display_text_main = f"{detail['description']}"
        elif detail['column_type'] in ['link', 'month_year']:
            display_text_main = f"{detail['button_name']}"

        new_main_content = current_main_content + display_text_main

        # Manage history for the main display area
        if self.current_history_state_index < len(self.display_history_states) - 1:
            # If we've navigated back and now adding new content, truncate history
            self.display_history_states = self.display_history_states[:self.current_history_state_index + 1]
        self.display_history_states.append(new_main_content)
        self.current_history_state_index = len(self.display_history_states) - 1

        # Update main display area
        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.insert(tk.END, new_main_content)
        self.display_text_area.see(tk.END) # Scroll to the end
        self.display_text_area.config(state=tk.DISABLED)

        # Update side display area
        if detail['column_type'] == 'details':
            self.side_details_text.config(state=tk.NORMAL)
            self.side_details_text.delete("1.0", tk.END) # Clear previous details
            # Display other details in the side display
            side_text = f"ชื่อปุ่ม: {detail['button_name']}\n" \
                        f"เลขบัญชี: {detail['account_number']}\n" \
                        f"เครดิต: {detail['credit_type']}\n" \
                        f"{'-'*30}\n"
            self.side_details_text.insert(tk.END, side_text)
            self.side_details_text.config(state=tk.DISABLED)
        else:
            # Clear side display if a non-details item is clicked
            self.side_details_text.config(state=tk.NORMAL)
            self.side_details_text.delete("1.0", tk.END)
            self.side_details_text.config(state=tk.DISABLED)

    def reset_display(self):
        """Clears both display areas and resets the history."""
        self.display_text_area.config(state=tk.NORMAL)
        self.display_text_area.delete("1.0", tk.END)
        self.display_text_area.config(state=tk.DISABLED)

        self.side_details_text.config(state=tk.NORMAL)
        self.side_details_text.delete("1.0", tk.END)
        self.side_details_text.config(state=tk.DISABLED)

        self.display_history_states = []
        self.current_history_state_index = -1
        self.currently_displayed_detail = None # Clear the reference
        self.copied_message_label.config(text="") # Clear copied message

    def navigate_history(self, direction):
        """Navigates through the history of the main display area."""
        new_index = self.current_history_state_index + direction

        if 0 <= new_index < len(self.display_history_states):
            self.current_history_state_index = new_index
            content_to_display = self.display_history_states[self.current_history_state_index]

            self.display_text_area.config(state=tk.NORMAL)
            self.display_text_area.delete("1.0", tk.END)
            self.display_text_area.insert(tk.END, content_to_display)
            self.display_text_area.see(tk.END)
            self.display_text_area.config(state=tk.DISABLED)

            # When navigating history, we don't have a specific 'detail' object
            # to update self.currently_displayed_detail or the side display.
            # For simplicity, clear the side display when navigating history.
            self.side_details_text.config(state=tk.NORMAL)
            self.side_details_text.delete("1.0", tk.END)
            self.side_details_text.config(state=tk.DISABLED)
            self.copied_message_label.config(text="") # Clear copied message
        elif new_index < 0 and self.current_history_state_index != -1: # Go back to empty state
            self.reset_display()

    def copy_to_clipboard(self, event=None):
        if pyperclip:
            text_to_copy = self.display_text_area.get("1.0", tk.END).strip()
            if text_to_copy:
                pyperclip.copy(text_to_copy)
                self.copied_message_label.config(text="คัดลอกไปยังคลิปบอร์ดแล้ว!", fg="#FF8C94") # Cute success color
                self.root.after(2000, self.clear_copied_message) # Clear message after 2 seconds
        else:
            self.copied_message_label.config(text="ไม่สามารถคัดลอกได้: pyperclip ไม่ได้ติดตั้ง", fg="#FF6B77")

    def clear_copied_message(self):
        self.copied_message_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()