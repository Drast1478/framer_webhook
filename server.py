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
    SHEET_ID = "1QHGT75HnTiqjjdK0SImS9kx_rim3Di-gNKPhBAEFfVo"
    sheet = client.open_by_key(SHEET_ID).sheet1

    print("✅ Successfully connected to Google Sheets!")

except Exception as e:
    print(f"❌ Google Sheets authentication error: {e}")

# ✅ Email Configuration (Using Gmail SMTP & App Password)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "mihaibuzila1478@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

@app.route('/contact', methods=['POST'])
def receive_form():
    try:
        data = request.json if request.is_json else request.form.to_dict()
        print(f"📩 Full raw data from Framer: {data}")

        # Normalize input with fallback defaults
        name = data.get("name") or data.get("Name", "there")
        email = data.get("email") or data.get("Email", "No email provided")
        phone = data.get("phone") or data.get("Phone", "")
        date = data.get("date") or data.get("Date", "")
        service = data.get("service") or data.get("Service", "")
        message = data.get("message") or data.get("Message", "No message")

        print(f"📩 Processed data:\nName={name}, Email={email}, Phone={phone}, Date={date}, Service={service}, Message={message}")

        # Append to Google Sheet
        try:
            sheet.append_row([name, email, phone, date, service, message])
            print("✅ Successfully saved to Google Sheets!")
        except Exception as e:
            print(f"❌ Google Sheets Error: {e}")

        # Send email if email is valid
        if "@" in email:
            send_email(email, name)

        return jsonify({"status": "received", "message": "Thank you for reaching out!"}), 200

    except Exception as e:
        print(f"❌ General Error: {e}")
        return jsonify({"error": str(e)}), 500

def send_email(to_email, sender_name):
    try:
        print(f"📧 Attempting to send email to {to_email}...")

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USERNAME
        msg["To"] = to_email
        msg["Subject"] = "Thank You for Reaching Out!"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px; color: #333;">
            <h2 style="color: #222;">Hey {sender_name},</h2>
            <p style="font-size: 16px; line-height: 1.5;">
                I just got your message -- thank you for reaching out!<br>
                I’ll get back to you as soon as I can (usually pretty quick).
            </p>
            <p style="font-size: 16px; margin-top: 30px;">
                Until then, stay happy!<br><br>
                <strong>- Mihai from BMihai Studio</strong>
            </p>
            <hr style="margin: 40px auto; width: 60%; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #888;">This is an automated message — no need to reply.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, to_email, msg.as_string())
        server.quit()

        print("✅ HTML Email sent successfully!")

    except Exception as e:
        print(f"❌ Email Sending Error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
