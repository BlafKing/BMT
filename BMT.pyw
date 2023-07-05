import os
import json
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
import zipfile
from collections import Counter
import threading
import subprocess

class MergeToolGUI:
    def __init__(self):
        
        self.var_files = []
        self.artist_name = ""
        self.package_name = ""
        self.version_number = ""
        self.output_file = ""
        self.merge_thread = None
        button_width = 20
        wide_button_width = 25
        
        self.root = tk.Tk()
        self.root.title("BlafKing's .var Merge Tool (BMT)")
        self.root.minsize(600, 350)
        self.root.pack_propagate(False)
        self.root.configure(bg="#252526")
        self.root.option_add('*foreground', 'white')
        self.root.option_add('*background', '#252526')

        self.file_frame = tk.Frame(self.root, bg="#252526")
        self.file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.file_list_label = tk.Label(self.file_frame, text="Selected Files:", bg="#252526", fg="white")
        self.file_list_label.pack(anchor=tk.W)

        self.file_scrollbar = tk.Scrollbar(self.file_frame, orient=tk.VERTICAL)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(self.file_frame, selectmode=tk.MULTIPLE, width=60, height=5, state="normal", bg="#3A3A3C", fg="white", selectbackground="#2D2D30", selectforeground="white")
        self.file_listbox.configure(exportselection=False)
        self.file_listbox.bind("<<ListboxSelect>>", lambda event: self.file_listbox.selection_clear(0, tk.END))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.file_listbox.config(yscrollcommand=self.file_scrollbar.set)
        self.file_scrollbar.config(command=self.file_listbox.yview)

        self.add_file_button = tk.Button(self.root, text="Select Files", command=self.select_var_files, width=wide_button_width, bg="#393939", fg="white")
        self.add_file_button.pack(padx=10, pady=5)

        self.save_frame = tk.Frame(self.root, bg="#252526")
        self.save_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.save_label = tk.Label(self.save_frame, text="Save Location:", bg="#252526", fg="white")
        self.save_label.pack(side=tk.LEFT, anchor=tk.W)

        self.save_entry = tk.Entry(self.save_frame, width=60, state="normal", bg="#3A3A3C", fg="white", insertbackground="white")
        self.save_entry.bind("<FocusIn>", lambda event: self.save_entry.selection_range(0, tk.END))
        self.save_entry.bind("<Key>", lambda event: "break")
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.save_button = tk.Button(self.save_frame, text="Choose", command=self.choose_save_location, bg="#393939", fg="white")
        self.save_button.pack(side=tk.LEFT, padx=(5, 0))

        self.edit_frame = tk.Frame(self.root, bg="#252526")
        self.edit_frame.pack(fill=tk.X, padx=50, pady=(5, 0))

        self.edit_artist_button = tk.Button(self.edit_frame, text="Edit Artist Name", command=self.edit_artist_name, width=button_width, bg="#393939", fg="white")
        self.edit_artist_button.pack(side=tk.LEFT, pady=(5, 0))

        self.edit_version_button = tk.Button(self.edit_frame, text="Edit Version Number", command=self.edit_version_number, width=button_width, bg="#393939", fg="white")
        self.edit_version_button.pack(side=tk.RIGHT, pady=(5, 0))

        self.edit_package_button = tk.Button(self.edit_frame, text="Edit Package Name", command=self.edit_package_name, width=button_width, bg="#393939", fg="white")
        self.edit_package_button.pack(pady=(5, 0))

        self.merge_button = tk.Button(self.root, text="Merge Files", command=self.start_merge, width=wide_button_width, bg="#393939", fg="white")
        self.merge_button.pack(padx=10, pady=10)

        self.progressbar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='determinate', style="Dark.Horizontal.TProgressbar")
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.disable_buttons_init()

        # Configure styles for dark theme
        self.style = ttk.Style()
        self.style.configure("Dark.Horizontal.TProgressbar", troughcolor="#303030", background="black")

    def run(self):
        self.SaveLocation = True
        self.root.mainloop()

    def select_var_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("VAR Files", "*.var")])
        if file_paths:
            self.var_files = list(file_paths)
            self.display_selected_files()
            if self.SaveLocation:
                self.enable_buttons_file()

    def display_selected_files(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.var_files:
            self.file_listbox.insert(tk.END, file)
        self.update_save_location()

    def choose_save_location(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            package_name = f"{self.artist_name}.{self.package_name}.{self.version_number}"
            self.output_file = os.path.normpath(os.path.join(folder_path, package_name + ".var"))
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(tk.END, self.output_file)
            self.SaveLocation = False
            self.enable_buttons()

    def edit_artist_name(self):
        artist_name = self.get_user_input("Enter the new artist name:")
        if artist_name:
            self.artist_name = artist_name.replace(" ", "_")
            self.update_save_location()

    def edit_package_name(self):
        package_name = self.get_user_input("Enter the new package name:")
        if package_name:
            self.package_name = package_name.replace(" ", "_")
            self.update_save_location()

    def edit_version_number(self):
        version_number = self.get_user_input("Enter the new version number:")
        if version_number:
            self.version_number = version_number
            self.update_save_location()

    def get_user_input(self, prompt):
        user_input = simpledialog.askstring("Input", prompt)
        return user_input.strip() if user_input else None

    def update_save_location(self):
        if not self.artist_name:
            artist_name_counts = Counter()
            for file_path in self.var_files:
                file_name = os.path.basename(file_path)
                artist_name = file_name.split(".")[0]
                artist_name_counts[artist_name] += 1

            artist = artist_name_counts.most_common(1)
            self.artist_name = artist[0][0] if artist else ""

        if not self.package_name:
            self.package_name = "Package"

        if not self.version_number:
            self.version_number = "1"

        package_name = f"{self.artist_name}.{self.package_name}.{self.version_number}"
        self.output_file = os.path.normpath(os.path.join(os.path.dirname(self.output_file), package_name + ".var"))
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(tk.END, self.output_file)

    def start_merge(self):
        if len(self.var_files) == 0:
            messagebox.showinfo("Error", "No files selected.")
            return
        if not self.output_file:
            messagebox.showinfo("Error", "No save location provided.")
            return

        if self.merge_thread is None or not self.merge_thread.is_alive():
            self.disable_buttons()
            self.progressbar["maximum"] = len(self.var_files)
            self.progressbar["value"] = 0
            self.merge_thread = threading.Thread(target=self.merge_files_thread)
            self.merge_thread.start()

    def merge_files_thread(self):
        artist_name_counts = Counter()
        for file_path in self.var_files:
            file_name = os.path.basename(file_path)
            artist_name = file_name.split(".")[0]
            artist_name_counts[artist_name] += 1

        artist = artist_name_counts.most_common(1)
        self.artist_name = artist[0][0] if artist else ""

        self.merge_files()
        self.enable_buttons_after_merge()

    def set_button_state(self, add_file_state, save_state, artist_state, version_state, package_state, merge_state):
        self.add_file_button.config(state=add_file_state)
        self.save_button.config(state=save_state)
        self.edit_artist_button.config(state=artist_state)
        self.edit_version_button.config(state=version_state)
        self.edit_package_button.config(state=package_state)
        self.merge_button.config(state=merge_state)

    def disable_buttons_init(self):
        self.set_button_state(tk.NORMAL, tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED)

    def disable_buttons(self):
        self.set_button_state(tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED)

    def enable_buttons(self):
        self.set_button_state(tk.NORMAL, tk.NORMAL, tk.NORMAL, tk.NORMAL, tk.NORMAL, tk.NORMAL)

    def enable_buttons_file(self):
        self.set_button_state(tk.NORMAL, tk.NORMAL, tk.DISABLED, tk.DISABLED, tk.DISABLED, tk.DISABLED)

    def enable_buttons_after_merge(self):
        self.enable_buttons()

    def merge_files(self):
        combined_content_list = set()
        combined_dependencies = {}

        existing_files = set()
        highest_program_version = None

        with zipfile.ZipFile(self.output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(self.var_files):
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

                self.update_progress(i + 1)

        combined_content_list = sorted(combined_content_list)
        combined_dependencies = dict(sorted(combined_dependencies.items()))

        combined_meta_data = {
            "licenseType": "PC",
            "creatorName": self.artist_name,
            "packageName": self.package_name,
            "standardReferenceVersionOption": "Latest",
            "scriptReferenceVersionOption": "Exact",
            "description": "This package has been generated by using BlafKing's Merge Tool.",
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

        with zipfile.ZipFile(self.output_file, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("meta.json", json.dumps(combined_meta_data, indent=3))
            messagebox.showinfo("Merge Complete", "Files merged successfully.")
            folder_path = os.path.dirname(self.output_file)
            subprocess.Popen(f'explorer "{folder_path}"')

            self.root.quit()

    def update_progress(self, value):
        self.progressbar["value"] = value
        self.root.update_idletasks()


if __name__ == "__main__":
    merge_tool_gui = MergeToolGUI()
    merge_tool_gui.run()
