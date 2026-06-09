import os
import shutil
from flask import Flask, request, jsonify

app = Flask(__name__)

UPLOAD_DIR = "/var/app/uploads"


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")

    # BUG: No file extension validation - attacker can upload .php, .py, .sh
    # and execute arbitrary code on the server.
    filename = uploaded_file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)
    uploaded_file.save(save_path)
    return jsonify({"saved": save_path})


@app.route("/upload-image", methods=["POST"])
def upload_image():
    uploaded_file = request.files.get("image")
    filename = uploaded_file.filename

    # BUG: MIME type check is based on the Content-Type header supplied by the
    # client, not the actual file content - trivially bypassed.
    content_type = request.content_type
    if "image" not in content_type:
        return jsonify({"error": "Only images allowed"}), 400

    # BUG: Path traversal - filename is not sanitised before joining with base dir.
    save_path = os.path.join(UPLOAD_DIR, filename)
    uploaded_file.save(save_path)
    return jsonify({"saved": save_path})


@app.route("/upload-zip", methods=["POST"])
def upload_zip():
    import zipfile, io

    uploaded_file = request.files.get("zip")
    data = io.BytesIO(uploaded_file.read())
    zf = zipfile.ZipFile(data)

    # BUG: Zip Slip - extracting without checking for "../" in member names lets
    # an attacker overwrite arbitrary files outside the target directory.
    zf.extractall(UPLOAD_DIR)
    return jsonify({"extracted": UPLOAD_DIR})


@app.route("/serve", methods=["GET"])
def serve_file():
    filename = request.args.get("name")

    # BUG: Path traversal - user-controlled filename allows reading files outside
    # the upload directory (e.g. /etc/passwd via "../../etc/passwd").
    full_path = UPLOAD_DIR + "/" + filename
    with open(full_path, "rb") as f:
        return f.read()


@app.route("/delete", methods=["POST"])
def delete_file():
    filename = request.json.get("filename")

    # BUG: No authentication check before deleting files.
    # BUG: Path traversal allows deleting arbitrary files on the filesystem.
    os.remove(os.path.join(UPLOAD_DIR, filename))
    return jsonify({"deleted": filename})
