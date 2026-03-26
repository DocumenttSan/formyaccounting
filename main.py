import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

# Check if pyperclip is installed, if not, provide a fallback or instruct user.
try:
    import pyperclip
except ImportError:
    print("pyperclip not found. Please install it using 'pip install pyperclip' for clipboard functionality.")
    pyperclip = None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Management GUI") # Set a default size
        self.root.geometry("1000x800")

        self.details_data = [] # Stores all the detail dictionaries

        # --- Main Layout Frames ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))

        self.columns_container_frame = tk.Frame(self.main_frame)
        self.columns_container_frame.pack(fill=tk.BOTH, expand=True)

        self.add_button_frame = tk.Frame(self.main_frame)
        self.add_button_frame.pack(fill=tk.X, pady=(5, 0))

        # Frame for display areas and control buttons
        self.display_control_frame = tk.Frame(self.main_frame, bd=2, relief=tk.GROOVE)
        self.display_control_frame.pack(fill=tk.X, pady=(10, 0))

        self.display_frame = tk.Frame(self.display_control_frame)
        self.display_frame.pack(fill=tk.X, pady=(10, 0))

        # --- Header Labels for Columns ---
        tk.Label(self.header_frame, text="รายละเอียด (Details)", font=("Arial", 12, "bold")).pack(side=tk.LEFT, expand=True)
        tk.Label(self.header_frame, text="คำเชื่อม (Link)", font=("Arial", 12, "bold")).pack(side=tk.LEFT, expand=True)
        tk.Label(self.header_frame, text="เดือน ปี (Month Year)", font=("Arial", 12, "bold")).pack(side=tk.LEFT, expand=True)

        # --- Columns (Scrollable) ---
        self.column_frames = {}
        column_names = ["details", "link", "month_year"]

        for name in column_names:
            col_frame = tk.Frame(self.columns_container_frame, bd=1, relief=tk.SUNKEN)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            self.column_frames[name] = col_frame

            canvas = tk.Canvas(col_frame)
            scrollbar = tk.Scrollbar(col_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Store the inner scrollable frame and canvas for adding widgets
            setattr(self, f"{name}_inner_frame", scrollable_frame)
            setattr(self, f"{name}_canvas", canvas)

        # --- Add Item Buttons for each column ---
        tk.Button(self.add_button_frame, text="เพิ่มรายละเอียด (Details)",
                  command=lambda: self.show_add_item_form('details')).pack(side=tk.LEFT, expand=True, padx=2)
        tk.Button(self.add_button_frame, text="เพิ่มคำเชื่อม (Link)",
                  command=lambda: self.show_add_item_form('link')).pack(side=tk.LEFT, expand=True, padx=2)
        tk.Button(self.add_button_frame, text="เพิ่มเดือน ปี (Month Year)",
                  command=lambda: self.show_add_item_form('month_year')).pack(side=tk.LEFT, expand=True, padx=2)

        # --- Display Areas ---
        self.display_content_frame = tk.Frame(self.display_control_frame)
        self.display_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # History for main display area
        self.display_history_states = []
        self.current_history_state_index = -1

        # Control buttons for display area
        self.display_buttons_frame = tk.Frame(self.display_control_frame)
        self.display_buttons_frame.pack(fill=tk.X, pady=(5, 0), padx=5)
        tk.Button(self.display_buttons_frame, text="รีเซ็ต (Reset)", command=self.reset_display).pack(side=tk.LEFT, padx=2)
        tk.Button(self.display_buttons_frame, text="ย้อนกลับ (Undo)", command=lambda: self.navigate_history(-1)).pack(side=tk.LEFT, padx=2) # Navigate back in history
        tk.Button(self.display_buttons_frame, text="ทำซ้ำ (Redo)", command=lambda: self.navigate_history(1)).pack(side=tk.LEFT, padx=2) # Navigate forward in history

        # Main Display Area (copyable)
        self.main_display_area_frame = tk.Frame(self.display_content_frame, bd=1, relief=tk.SUNKEN)
        self.main_display_area_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(self.main_display_area_frame, text="ข้อมูลที่แสดงผล (Copyable):", anchor="w", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(0, 2))

        self.display_text_area = tk.Text(self.main_display_area_frame, height=10, wrap=tk.WORD, state=tk.DISABLED, bg="lightgray")
        self.display_text_area.pack(fill=tk.BOTH, expand=True)
        self.display_text_area.bind("<Button-1>", self.copy_to_clipboard)

        self.copied_message_label = tk.Label(self.main_display_area_frame, text="", fg="green")
        self.copied_message_label.pack(fill=tk.X, pady=(2,0))

        # Side Display Area (non-copyable)
        self.side_display_area_frame = tk.Frame(self.display_content_frame, width=250, bd=1, relief=tk.SUNKEN) # Adjusted width
        self.side_display_area_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        self.side_display_area_frame.pack_propagate(False) # Prevent frame from resizing to content

        tk.Label(self.side_display_area_frame, text="รายละเอียดเพิ่มเติม (Non-Copyable):", anchor="w", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(0, 2), padx=5)

        self.side_details_text = tk.Text(self.side_display_area_frame, height=10, wrap=tk.WORD, state=tk.DISABLED, bg="lightyellow")
        self.side_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))


    def show_add_item_form(self, column_type):
        form_window = tk.Toplevel(self.root)
        form_window.title(f"เพิ่มรายการในคอลัมน์: {column_type.replace('_', ' ').title()}")
        form_window.transient(self.root) # Make it appear on top of the main window
        form_window.grab_set() # Make it modal
        form_window.geometry("400x350" if column_type == 'details' else "400x150") # Adjust size based on fields

        # Labels and Entry widgets
        tk.Label(form_window, text="ชื่อปุ่ม (Button Name):").pack(pady=5)
        button_name_entry = tk.Entry(form_window, width=40)
        button_name_entry.pack(pady=2)

        tk.Label(form_window, text="รายละเอียด (Description):").pack(pady=5)
        description_entry = None
        account_entry = None
        credit_type_var = None

        if column_type == 'details':
            description_entry = tk.Entry(form_window, width=40)
            description_entry.pack(pady=2)

            tk.Label(form_window, text="เลขบัญชี (Account Number):").pack(pady=5)
            account_entry = tk.Entry(form_window, width=40)
            account_entry.pack(pady=2)

            tk.Label(form_window, text="เครดิต (Credit Type):").pack(pady=5)
            credit_type_var = tk.StringVar(form_window, value="เงินสด") # Default value
            tk.Radiobutton(form_window, text="เงินสด (Cash)", variable=credit_type_var, value="เงินสด").pack(anchor=tk.W, padx=10)
            tk.Radiobutton(form_window, text="เงินฝาก (Deposit)", variable=credit_type_var, value="เงินฝาก").pack(anchor=tk.W, padx=10)
            tk.Radiobutton(form_window, text="อื่นๆ (Other)", variable=credit_type_var, value="อื่นๆ").pack(anchor=tk.W, padx=10)
        else:
            # For 'link' and 'month_year', the button name is the description, no separate description entry needed.
            # The "รายละเอียด (Description):" label is not packed for these types.
            pass

        # Save Button
        save_button = tk.Button(form_window, text="บันทึก (Save)",
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

        # Determine target frame and canvas based on column_type
        target_frame = getattr(self, f"{column_type}_inner_frame")
        target_canvas = getattr(self, f"{column_type}_canvas")

        self.add_button_to_column(detail, target_frame, target_canvas)
        form_window.destroy()

    def add_button_to_column(self, detail, target_frame, target_canvas):
        btn = tk.Button(target_frame, text=detail['button_name'],
                        command=lambda d=detail: self.on_detail_button_click(d),
                        width=25, anchor="w") # Set a fixed width and anchor left
        btn.pack(pady=2, padx=5, fill=tk.X)

        # Update the scroll region of the canvas
        target_canvas.update_idletasks() # Ensure widgets are drawn before calculating bbox
        target_canvas.config(scrollregion=target_canvas.bbox("all"))

    def on_detail_button_click(self, detail):
        # Get current content of main display area
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

            self.copied_message_label.config(text="") # Clear copied message
        elif new_index < 0 and self.current_history_state_index != -1: # Go back to empty state
            self.reset_display()

    def copy_to_clipboard(self, event=None):
        if pyperclip:
            text_to_copy = self.display_text_area.get("1.0", tk.END).strip()
            if text_to_copy:
                pyperclip.copy(text_to_copy)
                self.copied_message_label.config(text="คัดลอกไปยังคลิปบอร์ดแล้ว!", fg="green")
                self.root.after(2000, self.clear_copied_message) # Clear message after 2 seconds
        else:
            self.copied_message_label.config(text="ไม่สามารถคัดลอกได้: pyperclip ไม่ได้ติดตั้ง", fg="red")

    def clear_copied_message(self):
        self.copied_message_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()