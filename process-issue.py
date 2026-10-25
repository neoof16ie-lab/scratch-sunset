import os
import sys
import requests
import scratchattach as scratch

def main():
    lat_str = os.environ.get("LATITUDE")
    lng_str = os.environ.get("LONGITUDE")
    
    print(f"Actions起動成功(秒対応) - 緯度: {lat_str}, 経度: {lng_str}")

    if not lat_str or not lng_str:
        print("エラー: 緯度・経度が届いていません。")
        sys.exit(1)

    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except Exception as e:
        print(f"エラー: 座標変換失敗: {e}")
        sys.exit(1)

    api_url = f"https://sunrise-sunset.org{lat}&lng={lng}&formatted=0"
    
    try:
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("status") != "OK":
            print(f"APIエラー: {res_data.get('status')}")
            sys.exit(1)
            
        results = res_data["results"]
        # 💡 秒（6桁）まで安全に切り出すようにプログラムを拡張しました！
        def to_local_digits(utc_iso_str):
            if utc_iso_str is None:
                return "999999"  # 秒まで含めてデータがない時は9が6つ
            try:
                # "05:54:23" のように「秒」までをそのまま抜き出します
                time_part = utc_iso_str.split("T")[-1][:8]
                return time_part.replace(":", "")  # "055423" になります
            except Exception:
                return "999999"

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
        day_length = results.get("day_length", -1)
        polar_status = "0"
        if results.get("sunrise") is None or results.get("sunset") is None:
            if day_length == 0:
                polar_status = "2"  # 極夜
            else:
                polar_status = "1"  # 白夜

        # 6桁×8種類（48桁）＋時差（5桁）＋極地サイン（1桁）＝合計54桁にします
        sunrise     = to_local_digits(results["sunrise"])
        sunset      = to_local_digits(results["sunset"])
        civil_s     = to_local_digits(results["civil_twilight_begin"])
        civil_e     = to_local_digits(results["civil_twilight_end"])
        nautical_s  = to_local_digits(results["nautical_twilight_begin"])
        nautical_e  = to_local_digits(results["nautical_twilight_end"])
        astro_s     = to_local_digits(results["astronomical_twilight_begin"])
        astro_e     = to_local_digits(results["astronomical_twilight_end"])
        tz_encoded  = encode_timezone(results["sunrise"])

        encoded_data = sunrise + sunset + civil_s + civil_e + nautical_s + nautical_e + astro_s + astro_e + tz_encoded + polar_status
        print(f"Scratch送信データ(54桁): {encoded_data}")
        # 🔒 秘密金庫（Secrets）からログイン情報を安全に引っ張ってきます
        username = os.environ.get("SCRATCH_USERNAME")
        password = os.environ.get("SCRATCH_PASSWORD")
        project_id = "あなたのScratchプロジェクトID"  # ※ここをご自身の作品ID（数字）に変えてください

        if not username or not password:
            print("エラー: GitHubのSecretsにログイン情報が登録されていません。")
            sys.exit(1)

        # 本家Scratchにログインして54桁のデータを変数に流し込みます
        session = scratch.login(username, password)
        conn = session.connect_cloud(project_id)
        conn.set_var("response", int(encoded_data))
        conn.set_var("status", 1)
        print("本家Scratchのクラウド変数への54桁同期が完全に成功しました！")

    except Exception as e:
        print(f"処理中にクラッシュしました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
