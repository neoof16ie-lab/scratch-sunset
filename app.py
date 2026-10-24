import os
import sys
import requests
import scratchattach as scratch

def main():
    lat_str = os.environ.get("LATITUDE")
    lng_str = os.environ.get("LONGITUDE")
    
    print(f"Actions受信 - 緯度: {lat_str}, 経度: {lng_str}")

    if not lat_str or not lng_str:
        print("エラー: 緯度・経度が不足しています。")
        sys.exit(1)

    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except Exception as e:
        print(f"エラー: 座標変換失敗: {e}")
        sys.exit(1)

    # formatted=0 で現地時間のタイムゾーン付きISO 8601形式を取得します
    api_url = f"https://sunrise-sunset.org{lat}&lng={lng}&formatted=0"
    
    try:
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("status") != "OK":
            print(f"APIエラー: {res_data.get('status')}")
            sys.exit(1)
            
        results = res_data["results"]
        
        # 💡 現地時間の「時:分」をそのまま安全に抜き出す関数（4桁の文字列にする）
        def to_local_digits(utc_iso_str):
            time_part = utc_iso_str.split("T")[-1][:5] # "05:54"
            return time_part.replace(":", "") # "0554"

        # 💡 タイムゾーン情報を数字5桁にエンコードする関数
        # 例: "+09:00" -> プラスなので頭に「1」をつけて "10900"
        # 例: "-05:00" -> マイナスなので頭に「2」をつけて "20500"
        def encode_timezone(utc_iso_str):
            try:
                # 文字列の後ろからタイムゾーン部分（例: "+09:00" や "-05:00"）を抜き出す
                tz_part = utc_iso_str[-6:] # "+09:00"
                sign_char = tz_part[0] # "+" または "-"
                tz_time = tz_part[1:].replace(":", "") # "0900"
                
                sign_num = "1" if sign_char == "+" else "2"
                return f"{sign_num}{tz_time}"
            except Exception:
                # 万が一解析できない場合は、デフォルトとして時差なし「10000」を返す安全装置
                return "10000"

        # 1. 各時刻を現地時間の4桁の数字に変換（計32桁分）
        sunrise     = to_local_digits(results["sunrise"])
        sunset      = to_local_digits(results["sunset"])
        civil_s     = to_local_digits(results["civil_twilight_begin"])
        civil_e     = to_local_digits(results["civil_twilight_end"])
        nautical_s  = to_local_digits(results["nautical_twilight_begin"])
        nautical_e  = to_local_digits(results["nautical_twilight_end"])
        astro_s     = to_local_digits(results["astronomical_twilight_begin"])
        astro_e     = to_local_digits(results["astronomical_twilight_end"])

        # 2. タイムゾーン（時差）を5桁の数字に変形（「sunrise」から代表して取得）
        tz_encoded  = encode_timezone(results["sunrise"])

        # 3. すべてをガッチャンコして、合計37桁の巨大な数字の列を完成させる
        encoded_data = sunrise + sunset + civil_s + civil_e + nautical_s + nautical_e + astro_s + astro_e + tz_encoded
        print(f"作成した37桁のデータ (現地時間 + 時差): {encoded_data}")

        # 4. GitHub環境変数からScratchのログイン情報を読み込み
        username = os.environ["SCRATCH_USERNAME"]
        password = os.environ["SCRATCH_PASSWORD"]
        project_id = "あなたのScratchプロジェクトID"  # ※ここだけご自身の作品ID（数字）に変えてください

        # 5. Scratchのクラウド変数に送信
        session = scratch.login(username, password)
        conn = session.connect_cloud(project_id)
        conn.set_var("response", int(encoded_data))
        conn.set_var("status", 1)
        print("Scratchへの37桁送信が正常に完了しました！")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
