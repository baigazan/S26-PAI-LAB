from flask import Flask, render_template, request, jsonify
import hotelbot

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    if not user_message.strip():
        return jsonify({'response': 'Please enter a valid message.'})
    response = hotelbot.get_answer(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)