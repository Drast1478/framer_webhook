from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/contact', methods=['POST'])
def receive_form():
    try:
        print("Received a request!")
        print("Headers:", request.headers)
        print("Raw Data:", request.data)  # Print the raw data to see Framer's format

        # Check if the request is JSON
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()  # Convert form data to a dictionary
        
        print("Parsed Data:", data)  # Log parsed data

        return jsonify({"status": "received", "message": "Thank you for reaching out!"}), 200

    except Exception as e:
        print("Error:", str(e))  # Log any errors
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
