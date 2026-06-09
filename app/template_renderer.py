from flask import Flask, request, render_template_string, jsonify
from jinja2 import Environment

app = Flask(__name__)

GREETING_TEMPLATE = "Hello, {name}! Your role is {role}."


@app.route("/greet")
def greet():
    name = request.args.get("name", "Guest")

    # BUG: Server-Side Template Injection (SSTI) - user input is interpolated
    # directly into a Jinja2 template string. Attacker can send:
    #   ?name={{7*7}}              → renders "49"
    #   ?name={{config.items()}}   → dumps Flask config including SECRET_KEY
    #   ?name={{''.__class__.__mro__[1].__subclasses__()}}  → RCE
    template = "Hello, " + name + "! Welcome to the app."
    return render_template_string(template)


@app.route("/render-email")
def render_email():
    username = request.args.get("username", "user")
    subject = request.args.get("subject", "Notification")

    # BUG: SSTI - both user-supplied values are injected into the template string.
    html = f"<html><body><h1>{subject}</h1><p>Hi {username},</p></body></html>"
    return render_template_string(html)


@app.route("/custom-report")
def custom_report():
    template_str = request.args.get("template", "Report: {{data}}")

    # BUG: SSTI - attacker fully controls the Jinja2 template string.
    env = Environment()
    tmpl = env.from_string(template_str)
    return tmpl.render(data="sample")


@app.route("/format-message")
def format_message():
    msg_template = request.form.get("template", "")
    user_data = request.form.to_dict()

    # BUG: Python str.format_map with user-controlled template allows attribute
    # access on objects - attacker can exfiltrate secret keys via:
    #   template={secret.__class__.__init__.__globals__[SECRET_KEY]}
    result = msg_template.format_map(user_data)
    return jsonify({"message": result})
