import os
import sys
import json
import shutil
import zipfile
import demjson3
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
        appdata_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'BMT')
        os.makedirs(appdata_dir, exist_ok=True)
        s.settings_file = os.path.join(appdata_dir, 'settings.cfg')

        if not os.path.exists(s.settings_file):
            open(s.settings_file, 'a').close()

        s.last_files_folder = s.load_last_folder("last_files_folder")
        s.last_save_folder = s.load_last_folder("last_save_folder")

        s.dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            s.theme_path = sys._MEIPASS + '\\azure.tcl'
            s.icon_path = sys._MEIPASS + '\\icon.ico'
        else:
            s.theme_path = os.path.join(s.dir, 'azure.tcl')
            s.icon_path = os.path.join(s.dir, 'icon.ico')

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
        s.add_file_button.pack(padx=10, pady=(5, 2))

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
        s.edit_frame.pack(fill=tk.X, padx=50, pady=(10, 0))

        s.edit_artist_button = ttk.Button(s.edit_frame, text="Edit Artist Name", command=s.edit_artist_name, width=button_width)
        s.edit_artist_button.pack(side=tk.LEFT, pady=(5, 0))

        s.edit_version_button = ttk.Button(s.edit_frame, text="Edit Version Number", command=s.edit_version_number, width=button_width)
        s.edit_version_button.pack(side=tk.RIGHT, pady=(5, 0))

        s.edit_package_button = ttk.Button(s.edit_frame, text="Edit Package Name", command=s.edit_package_name, width=button_width)
        s.edit_package_button.pack(pady=(5, 0))

        s.merge_frame = ttk.Frame(s.root)
        s.merge_frame.pack(fill=tk.X, padx=0, pady=(15, 0))

        s.checkboxes_frame = ttk.Frame(s.merge_frame)
        s.checkboxes_frame.pack(side=tk.LEFT, padx=(12, 0))

        s.openFolder = tk.IntVar()
        s.openFolder.set(s.load_checkbox_state(1))
        s.merge_checkbox1 = ttk.Checkbutton(s.checkboxes_frame, variable=s.openFolder, command=s.update_checkbox_state)
        s.merge_checkbox1.pack(side=tk.TOP)

        s.closeProgram = tk.IntVar()
        s.closeProgram.set(s.load_checkbox_state(2))
        s.merge_checkbox2 = ttk.Checkbutton(s.checkboxes_frame, variable=s.closeProgram, command=s.update_checkbox_state)
        s.merge_checkbox2.pack(side=tk.TOP)

        s.updateMeta = tk.IntVar()
        s.updateMeta.set(s.load_checkbox_state(3))
        s.merge_checkbox3 = ttk.Checkbutton(s.checkboxes_frame, variable=s.updateMeta, command=s.update_checkbox_state)
        s.merge_checkbox3.pack(side=tk.TOP)

        s.labels_frame = ttk.Frame(s.merge_frame)
        s.labels_frame.pack(side=tk.LEFT)

        label1 = ttk.Label(s.labels_frame, text="Open folder after merge", anchor=tk.W)
        label1.pack(side=tk.TOP, anchor=tk.W)

        label2 = ttk.Label(s.labels_frame, text="Exit program after merge", anchor=tk.W)
        label2.pack(side=tk.TOP, anchor=tk.W, pady=(7, 7))

        label3 = ttk.Label(s.labels_frame, text="Set dependencies to .latest", anchor=tk.W)
        label3.pack(side=tk.TOP, anchor=tk.W, pady=(0, 2))
        
        s.button_frame = ttk.Frame(s.merge_frame)
        s.button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        s.merge_button = ttk.Button(s.button_frame, text="Merge Files", command=s.start_merge, width=wide_button_width)
        s.merge_button.pack(padx=(0, 200))

        s.progress_label = ttk.Label(s.root, text="")
        s.progress_label.pack()

        s.progressbar = ttk.Progressbar(s.root, orient=tk.HORIZONTAL, mode='determinate')
        s.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        s.disable_buttons_init()
    
    def run(s):
        s.root.mainloop()

    def load_checkbox_state(s, checkbox_index):
        with open(s.settings_file, 'r') as f:
            try:
                settings = json.load(f)
                checkbox_state = settings.get(f"checkbox{checkbox_index}")
                if checkbox_state is not None:
                    return checkbox_state
            except (ValueError, json.JSONDecodeError):
                pass

        return 0
    
    def update_checkbox_state(s):
        openFolder_state = s.openFolder.get()
        closeProgram_state = s.closeProgram.get()
        updateMeta_state = s.updateMeta.get()

        with open(s.settings_file, 'r') as f:
            try:
                settings = json.load(f)
            except (ValueError, json.JSONDecodeError):
                settings = {}

        settings["checkbox1"] = openFolder_state
        settings["checkbox2"] = closeProgram_state
        settings["checkbox3"] = updateMeta_state

        with open(s.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def select_var_files(s):
        file_paths = filedialog.askopenfilenames(filetypes=[("VAR Files", "*.var")], initialdir=s.last_files_folder)
        if file_paths:
            s.var_files = list(file_paths)
            s.display_selected_files()
            s.enable_buttons_file()
            s.save_last_folder("last_files_folder", os.path.dirname(s.var_files[0]))
            s.update_artist_name()
            s.save_entry.delete(0, tk.END)
            s.output_file = ""

    def display_selected_files(s):
        s.file_listbox.delete(0, tk.END)
        for file in s.var_files:
            s.file_listbox.insert(tk.END, file)
        s.update_save_location()

    def choose_save_location(s):
        folder_path = filedialog.askdirectory(initialdir=s.last_save_folder)
        if folder_path:
            package_name = f"{s.artist_name}.{s.package_name}.{s.version_number}"
            s.output_file = os.path.normpath(os.path.join(folder_path, package_name + ".var"))
            s.save_entry.delete(0, tk.END)
            s.save_entry.insert(tk.END, s.output_file)
            s.SaveLocation = False
            s.enable_buttons()
            s.save_last_folder("last_save_folder", folder_path)
            s.update_artist_name()

    def update_artist_name(s):
        artist_name_counts = Counter()
        for file_path in s.var_files:
            file_name = os.path.basename(file_path)
            artist_name = file_name.split(".")[0]
            artist_name_counts[artist_name] += 1

        artist = artist_name_counts.most_common(1)
        s.artist_name = artist[0][0] if artist else ""
        s.update_save_location()
    
    def edit_artist_name(s):
        artist_name = s.get_user_input("Enter the new artist name:", default_text=s.artist_name)
        if artist_name:
            s.artist_name = artist_name.replace(" ", "_")
            s.update_save_location()

    def edit_package_name(s):
        package_name = s.get_user_input("Enter the new package name:", default_text=s.package_name)
        if package_name:
            s.package_name = package_name.replace(" ", "_")
            s.update_save_location()

    def edit_version_number(s):
        version_number = s.get_user_input("Enter the new version number:", default_text=s.version_number)
        if version_number:
            s.version_number = version_number
            s.update_save_location()

    def get_user_input(s, prompt, default_text=None):
        initial_value = default_text if default_text is not None else ""
        user_input = simpledialog.askstring("Input", prompt, initialvalue=initial_value)
        return user_input.strip() if user_input else None

    def save_last_folder(s, folder_name, folder_path):
        if not os.path.isfile(s.settings_file):
            settings = {}
        else:
            with open(s.settings_file, 'r') as f:
                try:
                    settings = json.load(f)
                except (ValueError, json.JSONDecodeError):
                    settings = {}
        
        settings[folder_name] = folder_path
        
        with open(s.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def load_last_folder(s, folder_name):
        if not os.path.isfile(s.settings_file):
            return ""
        
        with open(s.settings_file, 'r') as f:
            try:
                settings = json.load(f)
                return settings.get(folder_name, "")
            except (ValueError, json.JSONDecodeError):
                return ""
    
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

    def set_button_state(s, add_file_state, add_file_color, save_state, save_color, other_state, other_color):
        s.add_file_button.config(state=add_file_state, style=add_file_color)
        s.save_button.config(state=save_state, style=save_color)
        s.edit_artist_button.config(state=other_state, style=other_color)
        s.edit_version_button.config(state=other_state, style=other_color)
        s.edit_package_button.config(state=other_state, style=other_color)
        s.merge_button.config(state=other_state, style=other_color)
        s.merge_checkbox1.config(state=add_file_state)
        s.merge_checkbox2.config(state=add_file_state)
        s.merge_checkbox3.config(state=add_file_state)

    def disable_buttons_init(s):
        s.button_style.configure("White.TButton", foreground="white")
        s.button_style.configure("Grey.TButton", foreground="grey")
        s.button_style.map("Grey.TButton",
                        foreground=[("disabled", "grey")],
                        background=[("disabled", "!focus", "grey")])
        
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton")

    def disable_buttons(s):
        s.set_button_state(tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton",
                           tk.DISABLED, "Grey.TButton")

    def enable_buttons(s):
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton")

    def enable_buttons_file(s):
        s.set_button_state(tk.NORMAL, "White.TButton",
                           tk.NORMAL, "White.TButton",
                           tk.DISABLED, "Grey.TButton")
    
    def clean_window(s):
        s.file_listbox.delete(0, tk.END)
        s.var_files = []
        s.save_entry.delete(0, tk.END)
        s.output_file = ""
        s.progress_label.configure(text="")
        s.progressbar["value"] = 0

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
    
    def load_valid_json_file(s, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (ValueError, json.JSONDecodeError):
            print(f"Error with {file_path}, Attempting fix.")
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            index = content.find('contentList')
            if index != -1:
                content = content[:index] + content[index:].replace('\\', '/')
                content = content[:index] + content[index:].replace('//', '/')
            
            lines = content.split('\n')
            i = 0
            while i < len(lines) - 4:
                line = lines[i]
                next_line = lines[i + 1]
                third_line = lines[i + 2]
                fourth_line = lines[i + 3]

                if line.strip().startswith('"') and line.count('/') >= 2 and next_line.strip() == '},' and third_line.strip().startswith('"'):
                    lines[i + 1] = '],'

                if line.strip().startswith('"') and line.count('/') >= 2 and next_line.strip().startswith('"') and line.count('/') >= 2:
                    if not line.strip().endswith('",'):
                        if line.strip().endswith('"'):
                            lines[i] = line.rstrip() + ','
                        else:
                            lines[i] = line.rstrip() + '",'

                if line.strip().endswith(',') and next_line.strip() == '}' and third_line.strip() == '},' and fourth_line.strip().startswith('"customOptions'):
                    lines[i] = line.rstrip()[:-1]

                if line.strip().endswith('{') and next_line.strip() == '}' and third_line.strip() == '},' and fourth_line.strip().startswith('"customOptions'):
                    indentation = '\t' * (line.count('\t') - 1)
                    new_line = f'{indentation}}},'
                    third_line.rstrip(',')
                    lines.insert(i + 3, new_line)

                if line.strip().endswith('}') and next_line.strip() == '}' and third_line.strip() == '},' and fourth_line.strip().startswith('"customOptions'):
                    lines.pop(i + 1)

                if line.strip().endswith('"') and len(next_line.strip()) > 0 and next_line.strip()[0] == '"':
                    lines[i] = line.rstrip() + ','

                i += 1
            content = '\n'.join(lines)
            try:
                fixed_json = demjson3.decode(content)
                print(f"{file_path} has been successfully fixed.")
                return fixed_json
            except demjson3.JSONDecodeError as e:
                print("Unable to fix JSON:", e)
                return None

    def update_dependency_names(s, dependencies):
        updated_dependencies = {}
        for dep, dep_data in dependencies.items():
            if dep.endswith(".latest"):
                updated_dependencies[dep] = dep_data
            else:
                dep_components = dep.split(".")
                last_component = dep_components[-1]
                if last_component.isdigit():
                    updated_dep_name = dep[:dep.rfind(".")] + ".latest"
                    updated_dependencies[updated_dep_name] = dep_data
                else:
                    updated_dependencies[dep] = dep_data

            sub_dependencies = dep_data.get("dependencies")
            if sub_dependencies:
                updated_sub_dependencies = s.update_dependency_names(sub_dependencies)
                if updated_sub_dependencies:
                    if dep in updated_dependencies:
                        updated_dependencies[dep]["dependencies"] = updated_sub_dependencies
                    else:
                        updated_dependencies[dep] = {"dependencies": updated_sub_dependencies}

        return updated_dependencies

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
                response = messagebox.askquestion(
                    "Unable to process",
                    f"The following files are unable to be processed:\n\n{unusable_files}\n\nDo you want to continue without them?"
                )
                if response == 'no':
                    os._exit(0)

            output_drive = os.path.splitdrive(s.output_file)[0]
            with zipfile.ZipFile(s.output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(s.var_files):

                    if file_path in unusable_files:
                        continue

                    s.progress_label.configure(text=f"Merging files: {file_path}")

                    temp_dir = tempfile.mkdtemp(dir=output_drive)
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    meta_file = os.path.join(temp_dir, "meta.json")
                    meta_data = s.load_valid_json_file(meta_file)
                    if meta_data is None:
                        unusable_files.append(file_path)
                        continue

                    combined_content_list.update(meta_data.get("contentList", []))

                    dependencies = meta_data.get("dependencies")
                    if s.updateMeta.get() == 1:
                        if dependencies:
                            updated_dependencies = s.update_dependency_names(dependencies)
                            combined_dependencies.update(updated_dependencies)
                    else:
                        if dependencies:
                            for dep, dep_data in dependencies.items():
                                combined_dependencies.setdefault(dep, {}).setdefault("dependencies", {}).update(
                                    dep_data.get("dependencies", {}))

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

            with zipfile.ZipFile(s.output_file, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("meta.json", json.dumps(combined_meta_data, indent=3))

            s.progress_label.configure(text=f"Merging completed!")

            if unusable_files:
                messagebox.showinfo(
                    "Merge Complete",
                    f"The following files were unable to be processed and are not included in the final package:\n\n{unusable_files}"
                )
            else:
                messagebox.showinfo("Merge Complete", "All files merged successfully.")

            if s.openFolder.get() == 1:
                subprocess.Popen(f'explorer /select,"{s.output_file}"')

            if s.closeProgram.get() == 1:
                os._exit(0)
            else:
                s.clean_window()
                s.disable_buttons_init()
                return

        except Exception as e:
            error_message = f"Exception occurred during merge:\n{traceback.format_exc()}"

            current_file = s.var_files[s.progressbar["value"] - 1]
            error_message += f"\n\nError occurred in file: {current_file}"

            current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
            errorlog_filename = f"Error_{current_datetime}.txt"
            errorlog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), errorlog_filename)
            with open(errorlog_path, "w") as errorlog_file:
                errorlog_file.write(error_message)
            messagebox.showerror("Merge Error", f"An error occurred during the merge process. Error log saved to: {errorlog_path}")
            shutil.rmtree(temp_dir)
            os._exit(1)

    def update_progress(s, value):
        s.progressbar["value"] = value
        s.root.update_idletasks()

if __name__ == "__main__":
    merge_tool_gui = MergeToolGUI()
    merge_tool_gui.run()
