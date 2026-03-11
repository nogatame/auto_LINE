import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# --- 1. 初期設定 (LINE & Firebase) ---
LINE_CHANNEL_ACCESS_TOKEN = 'JvIz6XX++UJ3HNUDcXTSRULrnFaHTpa8TX+mU5gQL4tti8UPSnQmkYdxkMtDlZ4aL0Zp9kXIDvDZRiVVq1lRG/4vGThJ47+FLYEvk2wBr3IQiu4xFo8Dip64rtrP3/EUtz74xwXvZi0w/lczdU6ovAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '099faed8c8a5c6f262fc68fee81bbac3'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# JSONファイルのパスを確実に指定（絶対パスを使うとエラーを防げます）
json_path = os.path.join(os.path.dirname(__file__), "service-account.json")
cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kousoku-6477e-default-rtdb.firebaseio.com/'
})

# --- 2. Webhookの口 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# --- 3. 友だち追加(follow)イベントの処理 ---
@handler.add(FollowEvent)
def handle_follow(event):
    # Firebaseから最新メッセージを取得
    ref = db.reference('latest_broadcast')
    snapshot = ref.get()
    
    greeting = "Hello。このbotは毎月、教室予約のシートを送信します。"
    
    # 配信内容がある場合はそれを追加、ない場合は挨拶のみ
    messages = [TextSendMessage(text=greeting)]
    
    if snapshot and 'text' in snapshot:
        last_msg = snapshot['text']
        messages.append(TextSendMessage(text=last_msg[0]))
        messages.append(TextSendMessage(text=last_msg[1]))

    # LINEに返信
    line_bot_api.reply_message(event.reply_token, messages)

if __name__ == "__main__":
    app.run(port=5000)