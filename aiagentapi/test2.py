from aiagent.googleapis.drive import get_file_id_and_mime_type, upload_file


name, id, mimeType = get_file_id_and_mime_type("MyAiAgent")

print(upload_file("README.md", "./README.md", "text/plain", id))