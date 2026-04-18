import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, abort

app = Flask(__name__)

# --- 初期化設定 ---
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
origin_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
# Firebaseの初期化ああ
if not firebase_admin._apps:
    try:
        if origin_key:
            clean_key = origin_key.strip()
            cert_dict = json.loads(clean_key)
            if "private_key" in cert_dict:
                cert_dict["private_key"] = cert_dict["private_key"].replace('\\n', '\n')
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        else:
            print("FIREBASE_SERVICE_ACCOUNT is not set.")
    except Exception as e:
        print(f"Firebase Init Error: {e}")
    # 秘密鍵の改行コード（\n）を正しく処理するようにします
db = firestore.client() if firebase_admin._apps else None

@app.route("/api/index", methods=['POST'])
def callback():
    try:
        body = request.get_json()
        events = body.get('events', [])

        if not events:
            return 'No events', 200

        event = events[0]
        event_type = event.get('type')
        reply_token = event.get('replyToken')
        user_message = ""
        if event_type == 'message' and 'message' in event:
            user_message = event.get('message').get('text', '')

        # --- ここから修正の重要ポイント ---
        
        # 1. 変数をあらかじめ初期化しておく（if文の外に出す）
        message_array = []
        user_message_clean = user_message.strip() # 前後の空白を取り除く
        
        target_event = (
            event_type == 'follow' or 
            '杉本' in user_message_clean or 
            '森ノ宮' in user_message_clean
        )

        # 2. 条件に合致する場合のみFirestoreからデータを取得
        if target_event and db:
            doc_ref = db.collection('latest_broadcast').document('text')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                print(f"DEBUG: User Message is [{user_message_clean}]")
                print(f"DEBUG: Target Event is {target_event}")
                # キーの振り分け
                if event_type == 'follow':
                    keys = ["0", "1", "2", "3"]
                elif '杉本' in user_message_clean:
                    keys = ["0", "1"]
                elif '森ノ宮' in user_message_clean:
                    keys = ["2", "3"]
                else:
                    print("DEBUG: No keys matched!") # ここを通るなら文字が一致していません
                    keys = []

                # メッセージ配列を作成
                for key in keys:
                    if data.get(key):
                        # メッセージの先頭に付いている改行（\n）等を取り除いてから送る
                        clean_text = data[key].strip()
                        message_array.append({'type': 'text', 'text': clean_text})

        # データが見つからなかった場合のフォールバック
        if target_event and not message_array:
            message_array.append({'type': 'text', 'text': "データが見つかりませんでした"})

        # LINEに送信
        if message_array and reply_token:
            line_url = 'https://api.line.me/v2/bot/message/reply'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
            }
            payload = {
                'replyToken': reply_token,
                'messages': message_array
            }
            res = requests.post(line_url, headers=headers, data=json.dumps(payload))
            print(f"LINE API Response: {res.status_code} - {res.text}") # エラー原因が見えるようにログを出力

        return 'OK', 200

    except Exception as e:
        print(f"Error Detail: {e}")
        return 'Internal Error', 500

app=app

if __name__ == "__main__":
    app.run(port=5000)
