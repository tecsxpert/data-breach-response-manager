from flask import Flask, request, jsonify
from services.groq_client import GroqClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
groq_client = GroqClient(api_key=os.getenv('GROQ_API_KEY'))

@app.route('/describe', methods=['POST'])
def describe_breach():
    data = request.json
    response = groq_client.describe_breach(data['breach_data'])
    return jsonify({'analysis': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

