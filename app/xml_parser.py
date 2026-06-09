import xml.etree.ElementTree as ET
from lxml import etree
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/parse-xml", methods=["POST"])
def parse_xml():
    xml_data = request.data

    # BUG: XXE (XML External Entity) - xml.etree.ElementTree does not disable
    # external entity processing; attacker can read local files or trigger SSRF.
    # e.g. payload: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    root = ET.fromstring(xml_data)
    return jsonify({"tag": root.tag, "text": root.text})


@app.route("/parse-lxml", methods=["POST"])
def parse_lxml():
    xml_data = request.data

    # BUG: lxml parser created without resolve_entities=False or no_network=True;
    # external entity attacks and billion-laughs DoS are both possible.
    parser = etree.XMLParser()
    root = etree.fromstring(xml_data, parser)
    return jsonify({"tag": root.tag})


@app.route("/parse-config", methods=["POST"])
def parse_config():
    xml_str = request.form.get("config", "")

    # BUG: DTD processing is not disabled - billion-laughs attack can exhaust
    # memory and crash the server (XML DoS).
    parser = etree.XMLParser(load_dtd=True, no_network=False)
    doc = etree.fromstring(xml_str.encode(), parser)
    return jsonify({"root": doc.tag})


@app.route("/user-profile", methods=["POST"])
def user_profile():
    # BUG: Attacker-controlled XML merged directly into a document that is later
    # rendered - can be combined with XXE to exfiltrate data.
    user_xml = request.data.decode()
    template = f"<profile>{user_xml}</profile>"
    root = ET.fromstring(template)
    name = root.findtext("name")
    return jsonify({"name": name})
