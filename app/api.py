import os
import subprocess
import urllib.request
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)


@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    # BUG: Command injection - user-controlled input passed to shell command without sanitisation.
    result = os.popen("ping -c 1 " + host).read()
    return result


@app.route("/convert")
def convert_file():
    filename = request.args.get("file")
    # BUG: Command injection via subprocess with shell=True and user-supplied filename.
    output = subprocess.check_output("convert " + filename + " output.png", shell=True)
    return output


@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    # BUG: SSRF - no validation of the URL; attacker can reach internal services,
    # metadata endpoints (169.254.169.254), or localhost.
    response = urllib.request.urlopen(url)
    return response.read()


@app.route("/proxy")
def proxy():
    import requests
    target = request.args.get("target")
    # BUG: SSRF - attacker controls the full target URL including scheme and host.
    resp = requests.get(target, timeout=5)
    return resp.text


@app.route("/redirect")
def open_redirect():
    next_url = request.args.get("next", "/")
    # BUG: Open redirect - user-supplied URL used directly; attacker can redirect to
    # a phishing page after login.
    return redirect(next_url)


@app.route("/exec")
def remote_exec():
    code = request.args.get("code")
    # BUG: Remote code execution - eval() on unvalidated user input.
    result = eval(code)
    return jsonify({"result": result})


@app.route("/log")
def log_user_input():
    user_input = request.args.get("msg", "")
    # BUG: Log injection - unescaped user input written to log file, allowing fake log entries.
    with open("app.log", "a") as f:
        f.write("[INFO] User message: " + user_input + "\n")
    return "logged"
