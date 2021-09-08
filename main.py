# main.py
import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('LlOfmzKytr33yX6paKp7RTq0sh7Z2ZMnKukJ+HrtWzgHoCA3aAyl12n+5A1nFpk3JmuaHYw5WkwJKTg4aOhXoCN3IfxqaDKOo8C2iegnlcoSANGBV3lGsexNMSICcNRfuqSeqTM5Zhw/XQ1HgavZrwdB04t89/1O/w1cDnyilFU=')  # アクセストークンを入れてください
handler = WebhookHandler('1639949a449f38d08cacc3adffc468d6')  # Channel Secretを入れてください


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
    if text == 'こんにちは':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='こんにちは'))
    elif text == 'こんばんは':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='こんばんは'))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='わからない..'))


# 画像メッセージが送信されたときの処理
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
     line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text='画像を受信しました。')) 

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)