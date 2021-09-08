import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, FollowEvent
)

app = Flask(__name__)

line_bot_api = LineBotApi('LlOfmzKytr33yX6paKp7RTq0sh7Z2ZMnKukJ+HrtWzgHoCA3aAyl12n+5A1nFpk3JmuaHYw5WkwJKTg4aOhXoCN3IfxqaDKOo8C2iegnlcoSANGBV3lGsexNMSICcNRfuqSeqTM5Zhw/XQ1HgavZrwdB04t89/1O/w1cDnyilFU=')  # アクセストークンを入れてください
handler = WebhookHandler('1639949a449f38d08cacc3adffc468d6')  # Channel Secretを入れてください
developer_id = "Ub803fb2469db4906a1f50f045576dfaf"  # あなたのUser IDを入れてください

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['x-line-signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# テキストメッセージが送信されたときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text == 'おはよう':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='おはよう！'))
    elif text == 'こんにちは':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='こんにちは！')) 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='メッセージを受信しました。')) 

# 画像メッセージが送信されたときの処理
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='画像を受信しました。')) 

# フォローイベント時の処理
@handler.add(FollowEvent)
def handle_follow(event):
    # 誰が追加したかわかるように機能追加
    profile = line_bot_api.get_profile(event.source.user_id)
    line_bot_api.push_message(developer_id,
        TextSendMessage(text="表示名:{}\nユーザID:{}\n画像のURL:{}\nステータスメッセージ:{}"\
        .format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)))
    
    # 友だち追加したユーザにメッセージを送信
    line_bot_api.reply_message(      
        event.reply_token, TextSendMessage(text='友だち追加ありがとうございます'))
        
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)