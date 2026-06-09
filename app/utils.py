import os
import pickle
import yaml
import subprocess
from flask import request, send_file


def read_user_file(filename: str) -> str:
    base_dir = "/var/app/uploads"
    # BUG: Path traversal - filename is not sanitised; attacker can pass
    # "../../etc/passwd" to read arbitrary files on the system.
    file_path = os.path.join(base_dir, filename)
    with open(file_path, "r") as f:
        return f.read()


def download_file():
    filename = request.args.get("file")
    # BUG: Path traversal via send_file with user-controlled path.
    return send_file("/var/app/uploads/" + filename)


def deserialize_user_data(raw_bytes: bytes):
    # BUG: Insecure deserialization - pickle.loads on untrusted bytes allows
    # arbitrary code execution.
    return pickle.loads(raw_bytes)


def load_config(config_str: str):
    # BUG: yaml.load without Loader=yaml.SafeLoader allows arbitrary Python object
    # construction and code execution.
    return yaml.load(config_str)


def calculate(expression: str):
    # BUG: eval() on user-supplied expression allows remote code execution.
    return eval(expression)


def run_script(script_name: str):
    # BUG: Command injection - script_name is user-controlled and passed to shell.
    subprocess.run("bash /scripts/" + script_name, shell=True)


def get_env_debug():
    # BUG: Sensitive environment variables (secrets, keys) exposed in API response.
    return dict(os.environ)


def make_temp_file(data: str) -> str:
    import tempfile
    # BUG: Predictable temp file name - using /tmp/<fixed name> is vulnerable to
    # symlink attacks; use tempfile.mkstemp() instead.
    tmp_path = "/tmp/app_temp_file.txt"
    with open(tmp_path, "w") as f:
        f.write(data)
    return tmp_path
