import shutil
import os

source_file = "generated/merged_tagged.json"

destination_folder = "C:/Users/poudy/Desktop/Py/GEMINI"

os.makedirs(destination_folder, exist_ok=True)

try:
    shutil.copy2(source_file, destination_folder)
    print(f"Successfully copied {source_file} to {destination_folder}")
except FileNotFoundError:
    print("Source file not found.")
except Exception as e:
    print(f"An error occurred: {e}")