from werkzeug.utils import secure_filename

class FileUploader:
    def __init__(self, upload_folder='uploads/'):
        self.upload_folder = upload_folder

    def save_file(self, file, filename=None):
        if not filename:
            filename = secure_filename(file.filename)
        file_path = f"{self.upload_folder}/{filename}"
        file.save(file_path)
        return file_path
