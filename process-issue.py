import os
import sys
import requests
import scratchattach as scratch

def main():
    # Renderから送られてきた環境変数（緯度経度）を安全に読み込みます
    lat_str = os.environ.get("LATITUDE")
    lng_str = os.environ.get("LONGITUDE")
    
    print(f"Actions起動成功 - 緯度: {lat_str}, 経度: {lng_str}")

    if not lat_str or not lng_str:
        print("エラー: 緯度・経度のデータが届いていません。")
        sys.exit(1)

    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except Exception as e:
        print(f"エラー: 座標変換失敗: {e}")
        sys.exit(1)

    # formatted=0 で現地時間のタイムゾーン付き形式を取得します
    api_url = f"https://sunrise-sunset.org{lat}&lng={lng}&formatted=0"
    
    try:
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("status") != "OK":
            print(f"APIエラー: {res_data.get('status')}")
            sys.exit(1)
            
        results = res_data["results"]
        
        def to_local_digits(utc_iso_str):
            time_part = utc_iso_str.split("T")[-1][:5]
            return time_part.replace(":", "")

        def encode_timezone(utc_iso_str):
            try:
                tz_part = utc_iso_str[-6:]
                sign_char = tz_part
                tz_time = tz_part[1:].replace(":", "")
                sign_num = "1" if sign_char == "+" else "2"
                return f"{sign_num}{tz_time}"
            except Exception:
                return "10000"

        sunrise     = to_local_digits(results["sunrise"])
        sunset      = to_local_digits(results["sunset"])
        civil_s     = to_local_digits(results["civil_twilight_begin"])
        civil_e     = to_local_digits(results["civil_twilight_end"])
        nautical_s  = to_local_digits(results["nautical_twilight_begin"])
        nautical_e  = to_local_digits(results["nautical_twilight_end"])
        astro_s     = to_local_digits(results["astronomical_twilight_begin"])
        astro_e     = to_local_digits(results["astronomical_twilight_end"])
        tz_encoded  = encode_timezone(results["sunrise"])

        # 計37桁の数字にします
        encoded_data = sunrise + sunset + civil_s + civil_e + nautical_s + nautical_e + astro_s + astro_e + tz_encoded
        print(f"Scratch送信データ(37桁): {encoded_data}")

        username = os.environ.get("SCRATCH_USERNAME")
        password = os.environ.get("SCRATCH_PASSWORD")
        
        # ⭕ ここにご自身の本家Scratchの作品ID（数字）を入力してください！
        project_id = "あなたのScratchプロジェクトID"

        if not username or not password:
            print("エラー: GitHubのSecretsにログイン情報が登録されていません。")
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
