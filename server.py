from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/contact', methods=['POST'])
def receive_form():
    data = request.json
    print(f"New inquiry from {data['name']} - {data['email']}: {data['message']}")
    
    # You can later store this in a database or send an email notification
    return jsonify({"status": "received", "message": "Thank you for reaching out!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)