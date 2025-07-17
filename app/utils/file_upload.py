import os
import shutil
from fastapi import UploadFile

def save_upload_file(upload_file: UploadFile, destination_dir: str) -> str:
    """
    Saves an uploaded file to a specified directory.

    Args:
        upload_file: The file to be saved.
        destination_dir: The directory where the file will be stored.

    Returns:
        The filename of the saved file.
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    filename = upload_file.filename.replace(" ", "_")
    file_path = os.path.join(destination_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return os.path.basename(file_path)