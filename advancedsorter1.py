import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from tkinter import ttk  # Import ttk for Progressbar

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Documents": [".pdf", ".docx", ".txt", ".csv", ".xlsx", ".pptx"],
    "Music": [".mp3", ".wav", ".aac"],
    "Others": []
}

def get_file_category(filename):
    """Determine the category of a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"

def get_file_date(file_path):
    """Extract file creation date from EXIF metadata if available; otherwise, use the modification date."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "DateTimeOriginal":  # Extract original creation date
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m")
        except Exception as e:
            print(f"EXIF error for {file_path}: {e}")
    
    modification_time = os.path.getmtime(file_path)
    return datetime.fromtimestamp(modification_time).strftime("%Y-%m")

def organize_files(folder_path):
    """Sort files into category-based folders and subfolders by date, updating progress bar."""
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder does not exist!")
        return

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    total_files = len(files)

    if total_files == 0:
        messagebox.showinfo("Info", "No files to sort.")
        return

    files_moved = 0
    progress_bar["maximum"] = total_files  # Set progress bar max value

    for i, file in enumerate(files, start=1):
        file_path = os.path.join(folder_path, file)
        category = get_file_category(file)
        date_folder = get_file_date(file_path)
        
        category_folder = os.path.join(folder_path, category)
        os.makedirs(category_folder, exist_ok=True)
        
        date_subfolder = os.path.join(category_folder, date_folder)
        os.makedirs(date_subfolder, exist_ok=True)
        
        destination_path = os.path.join(date_subfolder, file)
        shutil.move(file_path, destination_path)
        files_moved += 1

        # Update Progress Bar
        progress_bar["value"] = i
        percentage_label.config(text=f"{int((i / total_files) * 100)}%")
        root.update_idletasks()  # Force update UI
    
    messagebox.showinfo("Success", f"File sorting completed! {files_moved} files moved.")
    progress_bar["value"] = 0  # Reset progress bar
    percentage_label.config(text="")  # Clear percentage text

def browse_folder():
    """Open file dialog for user to select folder."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def start_sorting():
    """Start file sorting process."""
    selected_folder = folder_path.get()
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first!")
    else:
        organize_files(selected_folder)

# Create GUI application
root = tk.Tk()
root.title("File Sorter")
root.geometry("400x250")
root.resizable(False, False)

folder_path = tk.StringVar()

# Folder Selection
tk.Label(root, text="Select Folder to Sort:").pack(pady=10)
folder_entry = tk.Entry(root, textvariable=folder_path, width=50, state='readonly')
folder_entry.pack()
tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Percentage Label
percentage_label = tk.Label(root, text="", font=("Arial", 10))
percentage_label.pack()

# Sort Button
tk.Button(root, text="Sort Files", command=start_sorting, bg="green", fg="white").pack(pady=10)

if __name__ == "__main__":
    root.mainloop()
