import os
import sys
import requests
import scratchattach as scratch

def main():
    # 1. GitHub Actionsが自動で渡してくれる「Issueのタイトル」を取得
    # 想定するタイトルの形: "35.67,139.65" (緯度,経度)
    issue_title = os.environ.get("ISSUE_TITLE", "").strip()
    print(f"受信したIssueタイトル: {issue_title}")

    if not issue_title:
        print("エラー: Issueのタイトルが空です。")
        sys.exit(1)

    try:
        # カンマで分割して緯度と経度を浮動小数点数（float）にする
        lat_str, lng_str = issue_title.split(",")
        lat = float(lat_str)
        lng = float(lng_str)
        print(f"解析成功 - 緯度: {lat}, 経度: {lng}")
    except Exception as e:
        print(f"エラー: タイトルの形式が正しくありません。'緯度,経度' の形で送ってください。({e})")
        sys.exit(1)

    # 2. sunrise-sunset.orgのAPIのURLを組み立て
    # formatted=0 に設定することで、現地時間のタイムゾーン情報を含んだISO 8601形式でデータを取得します
    api_url = f"https://sunrise-sunset.org{lat}&lng={lng}&formatted=0"
    
    try:
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("status") != "OK":
            print(f"APIエラー: {res_data.get('status')}")
            sys.exit(1)
            
        results = res_data["results"]
        
        # 💡 現地時間の「時:分」をそのまま安全に抜き出す関数
        def to_local_digits(utc_iso_str):
            # 例: "2026-10-23T05:54:12-05:00" のような文字列から、
            # Tの後ろにある「時:分」部分（05:54）だけを純粋に型抜きします。
            # これにより、APIが自動判定してくれた現地時間のままで処理できます。
            time_part = utc_iso_str.split("T")[-1][:5] # "05:54"
            return time_part.replace(":", "") # "0554"

        # 3. 各時刻を現地時間の4桁の数字に変換
        sunrise     = to_local_digits(results["sunrise"])                  # 日の出
        sunset      = to_local_digits(results["sunset"])                   # 日の入り
        civil_s     = to_local_digits(results["civil_twilight_begin"])     # 常用薄明 始まり
        civil_e     = to_local_digits(results["civil_twilight_end"])       # 常用薄明 終わり
        nautical_s  = to_local_digits(results["nautical_twilight_begin"])  # 航海薄明 始まり
        nautical_e  = to_local_digits(results["nautical_twilight_end"])    # 航海薄明 終わり
        astro_s     = to_local_digits(results["astronomical_twilight_begin"]) # 天文薄明 始まり
        astro_e     = to_local_digits(results["astronomical_twilight_end"])   # 天文薄明 終わり

        # 4. すべてを順番通りに繋げて、合計32桁の数字列に合体させる
        encoded_data = sunrise + sunset + civil_s + civil_e + nautical_s + nautical_e + astro_s + astro_e
        print(f"作成した32桁のデータ (現地時間): {encoded_data}")

        # 5. GitHub環境変数からScratchのログイン情報を読み込み
        username = os.environ["SCRATCH_USERNAME"]
        password = os.environ["SCRATCH_PASSWORD"]
        project_id = "あなたのScratchプロジェクトID" # ※ここをご自身の作品ID（数字）に書き換えてください

        # 6. Scratchのクラウド変数「☁ response」に書き込む
        session = scratch.login(username, password)
        conn = session.connect_cloud(project_id)
        conn.set_var("response", int(encoded_data))
        
        # 完了の合図として status を 1 にする
        conn.set_var("status", 1)
        print("Scratchのクラウド変数へ正常にデータを送信しました！")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
