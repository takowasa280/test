# main.py
import os
import errno
import tempfile
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
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)

line_bot_api = LineBotApi('8WQEJIC6sGY0SBOiU6mpU3WgKs+7XBaXUQEp//VPVjhz/LujJ1islG0y+YkrFqgFJmuaHYw5WkwJKTg4aOhXoCN3IfxqaDKOo8C2iegnlcp20d3ziOi0NdrBKXjK6p0q0DbbF5FKyyk8fTcyNK62vAdB04t89/1O/w1cDnyilFU=')  # アクセストークンを入れてください
handler = WebhookHandler('6a6cfe47dab52f783d04316aa4c4a68d')  # Channel Secretを入れてください
developer_id = "Ub803fb2469db4906a1f50f045576dfaf"  # あなたのUser IDを入れてください


# ユーザから送信された画像を保存するディレクトリを作成
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
try:
    os.makedirs(static_tmp_path)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
        pass
    else:
        raise


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['x-line-signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("----1----")
    print(body)
    print(static_tmp_path)
    print("----2----")
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
model = load_model('my_model.h5') # 学習済みモデルをロードする
@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    print("----3----")
    print(event.message.id)
    print(event.message.type)
    print(event.message)
    print(static_tmp_path)
    print("----4----")
    line_bot_api.push_message(developer_id,
        TextSendMessage(text=static_tmp_path+"/"))
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix="jpg" + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
            tempfile_path = tf.name
            print(tempfile_path)

    dist_path = tempfile_path + '.' + "jpg"
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    filepath = os.path.join('static', 'tmp', dist_name) # ユーザから送信された画像のパスが格納されている
    line_bot_api.push_message(developer_id,
        TextSendMessage(text=filepath))

    # 送信された画像をモデルで判別する
    img = image.load_img(filepath, target_size=(32,32)) # 送信された画像を読み込み、リサイズする
    img = image.img_to_array(img) # 画像データをndarrayに変換する
    data = np.array([img])
    result = model.predict(data) # 分類する
    predicted = result.argmax()

    class_label = ["飛行機","自動車","鳥","猫","鹿","犬","蛙","馬","船","トラック"]
    pred_answer = "これは" + class_label[predicted] + "です"

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text= pred_answer))

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
    port = int(os.environ.get('PORT', 8000))
    app.run(host ='0.0.0.0',port = port)