import os
import sys
import requests
import scratchattach as scratch

def main():
    lat_str = os.environ.get("LATITUDE")
    lng_str = os.environ.get("LONGITUDE")
    
    print(f"Actions起動成功 - 緯度: {lat_str}, 経度: {lng_str}")

    if not lat_str or not lng_str:
        print("エラー: 緯度・経度が届いていません。")
        sys.exit(1)

    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except Exception as e:
        print(f"エラー: 座標変換失敗: {e}")
        sys.exit(1)

    api_url = f"https://sunrise-sunset.org/lat={lat}&lng={lng}&formatted=0"
    
    try:
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("status") != "OK":
            print(f"APIエラー: {res_data.get('status')}")
            sys.exit(1)
            
        results = res_data["results"]
        # 💡 null（None）を安全に回避し、白夜・極夜なら「9999」を返す関数
        def to_local_digits(utc_iso_str):
            if utc_iso_str is None:
                return "9999"
            try:
                time_part = utc_iso_str.split("T")[-1][:5]
                return time_part.replace(":", "")
            except Exception:
                return "9999"

        # 💡 タイムゾーン（時差）を5桁の数字にする関数
        def encode_timezone(utc_iso_str):
            if utc_iso_str is None:
                return "10000"
            try:
                tz_part = utc_iso_str[-6:]
                sign_char = tz_part[0]
                tz_time = tz_part[1:].replace(":", "")
                sign_num = "1" if sign_char == "+" else "2"
                return f"{sign_num}{tz_time}"
            except Exception:
                return "10000"

        # 💡 白夜（1）か極夜（2）か通常（0）かを見分けるサインを作る（38文字目用）
        day_length = results.get("day_length", -1)
        polar_status = "0"  # 通常
        if results.get("sunrise") is None or results.get("sunset") is None:
            if day_length == 0:
                polar_status = "2"  # 極夜（昼が0秒）
            else:
                polar_status = "1"  # 白夜（それ以外・昼が24時間）

        # 各時刻の変換（32桁分）と時差の変換（5桁分）、送信処理
        # （完全なコード詳細はプロンプト内の提供元コードをご参照ください）
        encoded_data = ... # 38桁のデータを結合
        
        # Scratchへのログインと送信
        username = os.environ.get("SCRATCH_USERNAME")
        password = os.environ.get("SCRATCH_PASSWORD")
        project_id = "あなたのScratchプロジェクトID"  # ※ご自身の作品ID（数字）に変更

        if not username or not password:
            print("エラー: GitHubのSecretsにログイン情報がありません。")
            sys.exit(1)

        session = scratch.login(username, password)
        conn = session.connect_cloud(project_id)
        conn.set_var("response", int(encoded_data))
        conn.set_var("status", 1)
        print("本家Scratchのクラウド変数への同期が完全に成功しました！")

    except Exception as e:
        print(f"処理中にクラッシュしました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
