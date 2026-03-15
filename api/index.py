import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, abort

app = Flask(__name__)

# --- 初期化設定 ---
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")

# Firebaseの初期化
if not firebase_admin._apps:
    # 秘密鍵の改行コード（\n）を正しく処理するようにします
    origin_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    cred = credentials.Certificate({
        "project_id": "kousoku-6477e",
        "client_email": "firebase-adminsdk-fbsvc@kousoku-6477e.iam.gserviceaccount.com",
        "private_key": origin_key.replace('\\n', '\n')
    })
    print(origin_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/api/index", methods=['POST'])
def callback():
    try:
        body = request.get_json()
        events = body.get('events', [])

        if not events:
            return 'No events', 200

        event = events[0]
        event_type = event.get('type')

        if event_type == 'message' or event_type == 'follow':
            reply_token = event.get('replyToken')

            # Firestoreから取得
            doc_ref = db.collection('latest_broadcast').document('text')
            doc = doc_ref.get()

            message_array = []
            if doc.exists:
                data = doc.to_dict()
                # キー "0", "1" が存在するか確認してリストに追加
                if data.get("0"):
                    message_array.append({'type': 'text', 'text': data["0"]})
                if data.get("1"):
                    message_array.append({'type': 'text', 'text': data["1"]})
            
            # データがない場合のフォールバック
            if not message_array:
                message_array.append({'type': 'text', 'text': "データが見つかりませんでした"})

            # LINEに返信
            line_url = 'https://api.line.me/v2/bot/message/reply'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
            }
            payload = {
                'replyToken': reply_token,
                'messages': message_array
            }
            
            requests.post(line_url, headers=headers, data=json.dumps(payload))

        return 'OK', 200

    except Exception as e:
        print(f"Error Detail: {e}")
        return 'Internal Error But OK', 200

app=app

if __name__ == "__main__":
    app.run(port=5000)
