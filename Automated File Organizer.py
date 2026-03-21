import os
import shutil

# 1. Define the target folder
folder_path = "/content/my_messy_folder"

# 2. Map extensions to folder names (The "Brain" of your script)
file_types = {
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".docx": "Documents",
    ".pdf": "Documents",
    ".jpg": "Images",
    ".png": "Images",
    ".csv": "Data",
    ".pptx": "Presentations" # Added .pptx for the sample file
}

# 3. Process the files
for file in os.listdir(folder_path):
    source = os.path.join(folder_path, file)

    # Skip if it's a folder, we only want files
    if os.path.isdir(source):
        continue

    # Get the file extension
    name, extension = os.path.splitext(file)

    # 4. Check if the extension is in our dictionary
    if extension.lower() in file_types:
        dest_folder_name = file_types[extension.lower()]
        dest_path = os.path.join(folder_path, dest_folder_name)

        os.makedirs(dest_path, exist_ok=True)
        shutil.move(source, os.path.join(dest_path, file))
        print(f"Moved {file} to {dest_folder_name}")
    else:
        print(f"Skipped {file}: Unknown file type.") # Handle unknown extensions
