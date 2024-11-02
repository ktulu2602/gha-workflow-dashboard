from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/workflow_runs_results.json')
def serve_json():
    return send_file('workflow_runs_results.json')

if __name__ == '__main__':
    # Check if required files exist
    required_files = ['index.html', 'workflow_runs_results.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: {file} not found in current directory")
            exit(1)
    
    # Run the app on all IPs (0.0.0.0) and port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)