import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_actions():
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    GITHUB_REPO = os.environ.get("GITHUB_REPO")
    
    lat = None
    lng = None
    if request.method == 'POST':
        raw_text = request.data.decode('utf-8') if request.data else ""
        print(f"Render受信(生のテキスト): {raw_text}")
        
        if raw_text:
            try:
                data = json.loads(raw_text)
                lat = data.get("lat")
                lng = data.get("lng")
            except Exception as e:
                print(f"JSONパースエラー: {e}")
                
        if not lat or not lng:
            try:
                data = request.get_json(silent=True) or request.form or {}
                lat = data.get("lat")
                lng = data.get("lng")
            except Exception:
                pass
    else:
        lat = request.args.get("lat")
        lng = request.args.get("lng")

    print(f"Render解析結果 - 緯度: {lat}, 経度: {lng}")
    if not lat or not lng:
        return jsonify({"status": "error", "message": "lat or lng is missing"}), 400

    if not GITHUB_TOKEN or not GITHUB_REPO:
        return jsonify({"status": "error", "message": "Server configuration missing from Render"}), 500
    github_url = f"https://github.com{GITHUB_REPO}/dispatches"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "scratch_request",
        "client_payload": {
            "lat": str(lat),
            "lng": str(lng)
        }
    }
    try:
        response = requests.post(github_url, json=payload, headers=headers)
        if 200 <= response.status_code < 300:
            return jsonify({"status": "success", "message": "Actions triggered successfully"}), 200
        else:
            return jsonify({"status": "error", "message": f"GitHub API rejected with status: {response.status_code}", "detail": response.text}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to connect to GitHub: {str(e)}"}), 500
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
