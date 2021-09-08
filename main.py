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

line_bot_api = LineBotApi('s7sejbAa5Qb66to6oDKwABjhqJ29MkLaU33S8XxUqGOLqd6DUOU6lqdjqXcDLkbRJmuaHYw5WkwJKTg4aOhXoCN3IfxqaDKOo8C2iegnlcoI5GTT9GJxedtXMDHdFTB3JGMcBKN2taNZfdz4bQ6/KgdB04t89/1O/w1cDnyilFU=')  # アクセストークンを入れてください
handler = WebhookHandler('b9e6104f3fd792eff458e036aa23540c')  # Channel Secretを入れてください


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
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='メッセージを受信しました。'))
    text = event.message.text
    if text == 'こんにちは':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='こんにちは'))
    elif text == 'こんばんは':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='こんばんは'))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='わからない..'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)