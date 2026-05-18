from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime

app = Flask(__name__)

OWNER_EMAIL = "pinhighprops@gmail.com"
SMTP_USER = "pinhighprops@gmail.com"
SMTP_PASS = ""  # fill in Gmail app password

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/br-blues")
def br_blues():
    return render_template("br_blues.html")

@app.route("/oleander")
def oleander():
    return render_template("oleander.html")

@app.route("/surf-shack")
def surf_shack():
    return render_template("surf_shack.html")

@app.route("/gameroom-paradise")
def gameroom_paradise():
    return render_template("gameroom_paradise.html")

EXPENSE_LOG = os.path.expanduser("~/rental-tracker/expenses.log")

@app.route("/expenses")
def expenses():
    rows = []
    if os.path.exists(EXPENSE_LOG):
        with open(EXPENSE_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
    rows.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return render_template("expenses.html", rows=rows)

@app.route("/inquire", methods=["POST"])
def inquire():
    data = request.get_json()
    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    property_name = data.get("property", "")
    checkin = data.get("checkin", "")
    checkout = data.get("checkout", "")
    guests = data.get("guests", "")
    message = data.get("message", "")
    signature = data.get("signature", "")

    inquiry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "property": property_name, "name": name, "email": email,
        "phone": phone, "checkin": checkin, "checkout": checkout,
        "guests": guests, "message": message,
        "waiver_signed": signature, "waiver_signed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("inquiries.log", "a") as f:
        f.write(json.dumps(inquiry) + "\n")

    try:
        body = f"""
New Booking Inquiry — Pin High Properties

Property: {property_name}
Name: {name}
Email: {email}
Phone: {phone}
Check-in: {checkin}
Check-out: {checkout}
Guests: {guests}

Message:
{message}

--- RENTAL AGREEMENT ---
Waiver Signed By: {signature}
Signed At: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = OWNER_EMAIL
        msg["Subject"] = f"New Inquiry | {property_name} | {name}"
        msg.attach(MIMEText(body, "plain"))

        if SMTP_PASS:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=False)
