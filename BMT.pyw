import os
import sys
import json
import shutil
import zipfile
import tempfile
import threading
import traceback
import subprocess
import tkinter as tk
from datetime import datetime
from zipfile import BadZipFile
from collections import Counter
from tkinter import ttk, filedialog, messagebox, simpledialog

class MergeToolGUI:
    def __init__(s):
        
        s.var_files = []
        s.artist_name = ""
        s.package_name = ""
        s.version_number = ""
        s.output_file = ""
        s.merge_thread = None
        button_width = 20
        wide_button_width = 25

        s.root = tk.Tk()
        s.root.title("BlafKing's .var Merge Tool (BMT)")
        s.root.minsize(650, 500)
        s.root.pack_propagate(False)
        
        s.dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            s.theme_path = sys._MEIPASS + '\\azure.tcl'
            s.icon_path = sys._MEIPASS + '\\icon.ico'
        else:
            s.theme_path = os.path.join(s.dir, 'azure.tcl')
            s.icon_path = os.path.join(s.dir, 'icon.ico')

        s.root.tk.call("source", s.theme_path)
        s.root.tk.call("set_theme", "dark")
        s.root.iconbitmap(default=s.icon_path)
        s.button_style = ttk.Style()

        s.file_frame = ttk.Frame(s.root)
        s.file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        s.file_list_label = ttk.Label(s.file_frame, text="Selected Files:")
        s.file_list_label.pack(anchor=tk.W)

        s.file_scrollbar = ttk.Scrollbar(s.file_frame, orient=tk.VERTICAL)
        s.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        s.file_listbox = tk.Listbox(s.file_frame, selectmode=tk.MULTIPLE, width=60, height=5, state="normal")
        s.file_listbox.configure(exportselection=False)
        s.file_listbox.bind("<<ListboxSelect>>", lambda event: s.file_listbox.selection_clear(0, tk.END))
        s.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        s.file_listbox.config(yscrollcommand=s.file_scrollbar.set)
        s.file_scrollbar.config(command=s.file_listbox.yview)

        s.add_file_button = ttk.Button(s.root, text="Select Files", command=s.select_var_files, width=wide_button_width)
        s.add_file_button.pack(padx=10, pady=5)

        s.save_frame = ttk.Frame(s.root)
        s.save_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        s.save_label = ttk.Label(s.save_frame, text="Save Location:")
        s.save_label.pack(side=tk.LEFT, anchor=tk.W)

        s.save_entry = ttk.Entry(s.save_frame, width=60, state="normal")
        s.save_entry.bind("<FocusIn>", lambda event: s.save_entry.selection_range(0, tk.END))
        s.save_entry.bind("<Key>", lambda event: "break")
        s.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        s.save_button = ttk.Button(s.save_frame, text="Choose", command=s.choose_save_location)
        s.save_button.pack(side=tk.LEFT, padx=(5, 0))

        s.edit_frame = ttk.Frame(s.root)
        s.edit_frame.pack(fill=tk.X, padx=50, pady=(5, 0))    

        s.edit_artist_button = ttk.Button(s.edit_frame, text="Edit Artist Name", command=s.edit_artist_name, width=button_width)
        s.edit_artist_button.pack(side=tk.LEFT, pady=(5, 0))

        s.edit_version_button = ttk.Button(s.edit_frame, text="Edit Version Number", command=s.edit_version_number, width=button_width)
        s.edit_version_button.pack(side=tk.RIGHT, pady=(5, 0))

        s.edit_package_button = ttk.Button(s.edit_frame, text="Edit Package Name", command=s.edit_package_name, width=button_width)
        s.edit_package_button.pack(pady=(5, 0))

        s.merge_button = ttk.Button(s.root, text="Merge Files", command=s.start_merge, width=wide_button_width)
        s.merge_button.pack(pady=(30, 0))
        
        s.progress_label = ttk.Label(s.root, text="")
        s.progress_label.pack(padx=10, pady=(0, 5))
        
        s.progressbar = ttk.Progressbar(s.root, orient=tk.HORIZONTAL, mode='determinate')
        s.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        s.disable_buttons_init()

    def run(s):
        s.SaveLocation = True
        s.root.mainloop()

    def select_var_files(s):
        file_paths = filedialog.askopenfilenames(filetypes=[("VAR Files", "*.var")])
        if file_paths:
            s.var_files = list(file_paths)
            s.display_selected_files()
            if s.SaveLocation:
                s.enable_buttons_file()

    def display_selected_files(s):
        s.file_listbox.delete(0, tk.END)
        for file in s.var_files:
            s.file_listbox.insert(tk.END, file)
        s.update_save_location()

    def choose_save_location(s):
        folder_path = filedialog.askdirectory()
        if folder_path:
            package_name = f"{s.artist_name}.{s.package_name}.{s.version_number}"
            s.output_file = os.path.normpath(os.path.join(folder_path, package_name + ".var"))
            s.save_entry.delete(0, tk.END)
            s.save_entry.insert(tk.END, s.output_file)
            s.SaveLocation = False
            s.enable_buttons()

    def edit_artist_name(s):
        artist_name = s.get_user_input("Enter the new artist name:")
        if artist_name:
            s.artist_name = artist_name.replace(" ", "_")
            s.update_save_location()

    def edit_package_name(s):
        package_name = s.get_user_input("Enter the new package name:")
        if package_name:
            s.package_name = package_name.replace(" ", "_")
            s.update_save_location()

    def edit_version_number(s):
        version_number = s.get_user_input("Enter the new version number:")
        if version_number:
            s.version_number = version_number
            s.update_save_location()

    def get_user_input(s, prompt):
        user_input = simpledialog.askstring("Input", prompt)
        return user_input.strip() if user_input else None

    def update_save_location(s):
        if not s.artist_name:
            artist_name_counts = Counter()
            for file_path in s.var_files:
                file_name = os.path.basename(file_path)
                artist_name = file_name.split(".")[0]
                artist_name_counts[artist_name] += 1

            artist = artist_name_counts.most_common(1)
            s.artist_name = artist[0][0] if artist else ""

        if not s.package_name:
            s.package_name = "Package"

        if not s.version_number:
            s.version_number = "1"

        package_name = f"{s.artist_name}.{s.package_name}.{s.version_number}"
        s.output_file = os.path.normpath(os.path.join(os.path.dirname(s.output_file), package_name + ".var"))
        s.save_entry.delete(0, tk.END)
        s.save_entry.insert(tk.END, s.output_file)

    def start_merge(s):
        if len(s.var_files) == 0:
            messagebox.showinfo("Error", "No files selected.")
            return
        if not s.output_file:
            messagebox.showinfo("Error", "No save location provided.")
            return

        if s.merge_thread is None or not s.merge_thread.is_alive():
            s.disable_buttons()
            s.progressbar["maximum"] = len(s.var_files)
            s.progressbar["value"] = 0
            s.merge_thread = threading.Thread(target=s.merge_files_thread)
            s.merge_thread.start()

    def merge_files_thread(s):
        artist_name_counts = Counter()
        for file_path in s.var_files:
            file_name = os.path.basename(file_path)
            artist_name = file_name.split(".")[0]
            artist_name_counts[artist_name] += 1

        artist = artist_name_counts.most_common(1)
        s.artist_name = artist[0][0] if artist else ""

        s.merge_files()
            

    def set_button_state(s, add_file_state, add_file_color, save_state, save_color, artist_state, artist_color, version_state, version_color, package_state, package_color, merge_state, merge_color):
        s.add_file_button.config(state=add_file_state, style=add_file_color)
        s.save_button.config(state=save_state, style=save_color)
        s.edit_artist_button.config(state=artist_state, style=artist_color)
        s.edit_version_button.config(state=version_state, style=version_color)
        s.edit_package_button.config(state=package_state, style=package_color)
        s.merge_button.config(state=merge_state, style=merge_color)

    def disable_buttons_init(s):
        s.button_style.configure("White.TButton", foreground="white")
        s.button_style.configure("Grey.TButton", foreground="grey")
        s.button_style.map("Grey.TButton",
                        foreground=[("disabled", "grey")],
                        background=[("disabled", "!focus", "grey")])
        
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton")

    def disable_buttons(s):
        s.set_button_state(tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton")

    def enable_buttons(s):
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton")

    def enable_buttons_file(s):
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton")

    def merge_files(s):
        try:
            combined_content_list = set()
            combined_dependencies = {}

            existing_files = set()
            highest_program_version = None
            unusable_files = []
            
            for i, file_path in enumerate(s.var_files):
                s.progress_label.configure(text=f"Checking files: {file_path}")
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        file_list = zip_ref.namelist()
                        for file_name in file_list:
                            try:
                                zip_ref.open(file_name)
                            except BadZipFile:
                                unusable_files.append(file_path)
                                break
                except Exception as e:
                    unusable_files.append(file_path)
                    
            if unusable_files:
                response = messagebox.askquestion("Unable to process", f"The following files are unable to be processed:\n\n{unusable_files}\n\nDo you want to continue without them?")
                if response == 'no':
                    os._exit(0)

            temp_output_file = tempfile.NamedTemporaryFile(delete=False)

            with zipfile.ZipFile(temp_output_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(s.var_files):
                    s.update_progress(i + 1)
                    if file_path in unusable_files:
                        continue
                    
                    s.progress_label.configure(text=f"Merging files: {file_path}")
                    
                    temp_dir = tempfile.mkdtemp()
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    meta_file = os.path.join(temp_dir, "meta.json")
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta_data = json.load(f)

                    combined_content_list.update(meta_data["contentList"])

                    for dep, dep_data in meta_data["dependencies"].items():
                        combined_dependencies.setdefault(dep, {}).setdefault("dependencies", {}).update(
                            dep_data["dependencies"])

                    program_version = meta_data.get("programVersion")
                    if program_version and (highest_program_version is None or program_version > highest_program_version):
                        highest_program_version = program_version

                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file == "meta.json":
                                continue
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, temp_dir)

                            if rel_path in existing_files:
                                continue

                            existing_files.add(rel_path)
                            zipf.write(file_path, rel_path)

                    shutil.rmtree(temp_dir)

                    s.update_progress(i + 1)

            s.progress_label.configure(text=f"Merging completed!")
            combined_content_list = sorted(combined_content_list)
            combined_dependencies = dict(sorted(combined_dependencies.items()))

            combined_meta_data = {
                "licenseType": "PC",
                "creatorName": s.artist_name,
                "packageName": s.package_name,
                "standardReferenceVersionOption": "Latest",
                "scriptReferenceVersionOption": "Exact",
                "description": "This Package has been merged by BlafKing's Merge Tool",
                "credits": "",
                "instructions": "",
                "promotionalLink": "",
                "programVersion": highest_program_version,
                "contentList": combined_content_list,
                "dependencies": combined_dependencies,
                "customOptions": {"preloadMorphs": "false"},
                "hadReferenceIssues": "false",
                "referenceIssues": []
            }

            with zipfile.ZipFile(temp_output_file.name, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("meta.json", json.dumps(combined_meta_data, indent=3))

            temp_output_file.close()

            shutil.move(temp_output_file.name, s.output_file)
            messagebox.showinfo("Merge Complete", "All files merged successfully.")

            subprocess.Popen(f'explorer /select,"{s.output_file}"')
            s.root.quit()
            
        except Exception as e:
            error_message = f"Exception occurred during merge:\n{traceback.format_exc()}"
            current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
            errorlog_filename = f"Error_{current_datetime}.txt"
            errorlog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), errorlog_filename)
            with open(errorlog_path, "w") as errorlog_file:
                errorlog_file.write(error_message)
            messagebox.showerror("Merge Error", f"An error occurred during the merge process. error log saved to: {errorlog_path}")

    def update_progress(s, value):
        s.progressbar["value"] = value
        s.root.update_idletasks()


if __name__ == "__main__":
    merge_tool_gui = MergeToolGUI()
    merge_tool_gui.run()
