import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Renderの環境変数（Environment Variables）から設定を読み込む
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # 例: "ユーザー名/リポジトリ名"

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_actions():
    # 1. Scratchやユーザーから送られてきた緯度・経度を取得
    # GET通信（URLパラメータ）とPOST通信の両方に対応させます
    if request.method == 'POST':
        data = request.get_json() or {}
        lat = data.get("lat")
        lng = data.get("lng")
    else:
        lat = request.args.get("lat")
        lng = request.args.get("lng")

    print(f"Renderがリクエストを受信 - 緯度: {lat}, 経度: {lng}")

    if not lat or not lng:
        return jsonify({"status": "error", "message": "lat or lng is missing"}), 400

    if not GITHUB_TOKEN or not GITHUB_REPO:
        return jsonify({"status": "error", "message": "Server configuration missing"}), 500

    # 2. GitHub Actionsを叩き起こすための設定（APIリクエスト）
github_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"


    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 先ほど作成したymlの「types: [scratch_request]」と連動させます
    payload = {
        "event_type": "scratch_request",
        "client_payload": {
            "lat": str(lat),
            "lng": str(lng)
        }
    }

    # 3. GitHubへPOST送信してActionsを起動（キック）する
    try:
        response = requests.post(github_url, json=payload, headers=headers)
        if response.status_code == 24: # 204 No Content が成功の合図です
            print("GitHub Actionsの起動に成功しました！")
            return jsonify({"status": "success", "message": "Actions triggered"}), 200
        else:
            print(f"GitHubエラー: {response.status_code} - {response.text}")
            return jsonify({"status": "error", "message": "Failed to trigger GitHub"}), response.status_code
            
    except Exception as e:
        print(f"通信エラー: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Renderが指定するポート番号で起動させる設定
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
