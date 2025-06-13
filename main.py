"""
Simple Flask app for Replit compatibility
The actual deployment uses lambda_handler.py for AWS Lambda serverless architecture
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'IELTS GenAI Prep - AWS Lambda Serverless Architecture',
        'status': 'Ready for deployment',
        'architecture': 'Pure AWS Lambda + DynamoDB + Nova Sonic Bi-directional Streaming',
        'deployment': 'Use serverless framework: sls deploy',
        'features': [
            'Nova Sonic bi-directional speech streaming',
            'DynamoDB Global Tables',
            'Apple/Google in-app purchase verification',
            'Multi-region deployment (us-east-1, eu-west-1, ap-southeast-1)',
            'WebSocket support for real-time conversations'
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'architecture': 'AWS Lambda Serverless',
        'nova_sonic': 'Bi-directional streaming enabled',
        'regions': ['us-east-1', 'eu-west-1', 'ap-southeast-1']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)