import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import shutil
import re

def parse_sln(file_path):
    projects = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    project_pattern = r'Project\(".*?"\) = "(.+?)", "(.+?)", "(.+?)"'
    for line in lines:
        match = re.match(project_pattern, line)
        if match:
            project_name = match.group(1)
            project_path = match.group(2)
            projects.append((project_name, os.path.abspath(os.path.join(os.path.dirname(file_path), os.path.dirname(project_path)))))
    return projects

def load_sln():
    file_path = filedialog.askopenfilename(filetypes=[("Solution Files", "*.sln")])
    if not file_path:
        return
    global sln_directory
    sln_directory = os.path.dirname(file_path)  # Store the .sln directory
    projects = parse_sln(file_path)
    for item in tree.get_children():
        tree.delete(item)
    for idx, (name, location) in enumerate(projects):
        tree.insert('', 'end', text=f"{idx+1}", values=(name, location))

def clear_cache():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "No projects selected.")
        return

    failed_paths = []

    # Attempt to delete cache folders for each selected project
    for item in selected_items:
        project_location = tree.item(item, "values")[1]
        for folder in ["bin", "obj", ".vs"]:
            folder_path = os.path.join(project_location, folder)
            if not remove_folder(folder_path):
                failed_paths.append(folder_path)

    # Remove the .vs folder from the .sln directory
    if sln_directory:
        sln_vs_folder = os.path.join(sln_directory, ".vs")
        if not remove_folder(sln_vs_folder):
            failed_paths.append(sln_vs_folder)

    if failed_paths:
        messagebox.showwarning(
            "Partial Success",
            "Cache cleared for some folders, but the following paths could not be deleted:\n" +
            "\n".join(failed_paths)
        )
    else:
        messagebox.showinfo("Success", "Cache cleared for all selected projects!")

def remove_folder(folder_path):
    """
    Tries to remove the folder at the given path.
    Returns True if successful, False if an exception is encountered.
    """
    try:
        if os.path.exists(folder_path):
            print(f"Removing folder: {folder_path}")
            shutil.rmtree(folder_path)
        return True
    except PermissionError:
        print(f"PermissionError: Could not delete {folder_path} because it is in use.")
        return False
    except Exception as e:
        print(f"Error: Could not delete {folder_path}: {e}")
        return False

def show_location(event):
    selected_item = tree.selection()
    if selected_item:
        project_location = tree.item(selected_item, "values")[1]
        location_label.config(text=f"Location: {project_location}")

def select_all():
    for item in tree.get_children():
        tree.selection_add(item)

def select_none():
    tree.selection_remove(tree.selection())

app = tk.Tk()
app.title("Solution Project Viewer")
app.geometry("700x500")

frame = tk.Frame(app)
frame.pack(fill=tk.BOTH, expand=True)

btn_load = tk.Button(frame, text="Load .sln File", command=load_sln)
btn_load.pack(pady=10)

tree = ttk.Treeview(frame, columns=("Name", "Location"), show="headings", selectmode="extended")
tree.heading("Name", text="Project Name")
tree.heading("Location", text="Physical Location")
tree.pack(fill=tk.BOTH, expand=True)

tree.bind("<Motion>", show_location)

btn_frame = tk.Frame(frame)
btn_frame.pack(pady=10)

btn_clear_cache = tk.Button(btn_frame, text="Clear Entire Cache", command=clear_cache)
btn_clear_cache.grid(row=0, column=0, padx=5)

btn_select_all = tk.Button(btn_frame, text="Select All", command=select_all)
btn_select_all.grid(row=0, column=1, padx=5)

btn_select_none = tk.Button(btn_frame, text="Select None", command=select_none)
btn_select_none.grid(row=0, column=2, padx=5)

location_label = tk.Label(frame, text="Location: ", wraplength=600, anchor="w", justify="left")
location_label.pack(fill=tk.X, pady=10)

sln_directory = None  # Global variable to store the solution directory

app.mainloop()
