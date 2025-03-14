from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/contact', methods=['POST'])
def receive_form():
    try:
        # Check if the request is JSON
        if request.is_json:
            data = request.json
        else:
            # If it's not JSON, read the form data from request.form
            data = {
                "name": request.form.get("name", "Unknown"),
                "email": request.form.get("email", "No email provided"),
                "message": request.form.get("message", "No message")
            }
        
        print(f"New inquiry from {data['name']} - {data['email']}: {data['message']}")
        
        return jsonify({"status": "received", "message": "Thank you for reaching out!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
