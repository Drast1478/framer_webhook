import os
import json
import smtplib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ✅ Load Google Sheets credentials from Render Environment Variables
try:
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

    if GOOGLE_CREDENTIALS is None:
        raise ValueError("GOOGLE_CREDENTIALS is missing from environment variables!")

    creds_json = json.loads(GOOGLE_CREDENTIALS)
    print("✅ Successfully loaded Google Sheets credentials!")

    # Authenticate with Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    SHEET_ID = "1QHGT75HnTiqjjdK0SImS9kx_rim3Di-gNKPhBAEFfVo"  # Replace with actual Sheet ID
    sheet = client.open_by_key(SHEET_ID).sheet1

    print("✅ Successfully connected to Google Sheets!")

except Exception as e:
    print(f"❌ Google Sheets authentication error: {e}")

# ✅ Email Configuration (Using Gmail SMTP & App Password)
EMAIL_HOST = "smtp.gmail.com"  # Gmail SMTP server
EMAIL_PORT = 587  # Secure SMTP port
EMAIL_USERNAME = "mihaibuzila1478@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Loaded securely from Render

@app.route('/contact', methods=['POST'])
def receive_form():
    try:
        # ✅ Print the full raw request for debugging
        data = request.json if request.is_json else request.form.to_dict()
        print(f"📩 Full raw data from Framer: {data}")

        # ✅ Extract form values properly
        name = data.get("name", "Unknown").strip()
        email = data.get("email", "No email provided").strip()
        message = data.get("message", "No message").strip()

        print(f"📩 Processed data: Name={name}, Email={email}, Message={message}")

        # ✅ Save to Google Sheets
        try:
            sheet.append_row([name, email, message])
            print("✅ Successfully saved to Google Sheets!")
        except Exception as e:
            print(f"❌ Google Sheets Error: {e}")

        # ✅ Send Email (Only if Email is Valid)
        if "@" in email:
            send_email(email, name)

        return jsonify({"status": "received", "message": "Thank you for reaching out!"}), 200

    except Exception as e:
        print(f"❌ General Error: {e}")
        return jsonify({"error": str(e)}), 500

def send_email(to_email, name):
    try:
        print(f"📧 Attempting to send email to {to_email}...")

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = to_email
        msg["Subject"] = "Thank You for Reaching Out!"
        
        body = f"""
        Hi {name},

        Thank you for contacting me! I received your message and will get back to you as soon as possible.

        Best,
        Mihai
        """
        msg.attach(MIMEText(body, "plain"))

        # ✅ Connect to SMTP server and send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, to_email, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Email Sending Error: {e}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
