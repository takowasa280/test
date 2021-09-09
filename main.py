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
import pandas as pd


app = Flask(__name__)

line_bot_api = LineBotApi('DxMFTio1R1+nVJajDNbnqYFUl7KyRHySWX6WKCOmsw9DUe9LqMkqR0tbfn4YXKn8JmuaHYw5WkwJKTg4aOhXoCN3IfxqaDKOo8C2iegnlcrIah6BRIcczrJGEjiarq+WTzaGJlKHoz4wEPjWrUX5GAdB04t89/1O/w1cDnyilFU=')  # アクセストークンを入れてください
handler = WebhookHandler('767b4a9770bbca370dfe01e10ddbd274')  # Channel Secretを入れてください
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
    profile = line_bot_api.get_profile(event.source.user_id)
    line_bot_api.push_message(developer_id,
        TextSendMessage(text="表示名:{}\nユーザID:{}\n画像のURL:{}\nステータスメッセージ:{}"\
        .format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)))
    text = event.message.text
    line_bot_api.push_message(developer_id,
        TextSendMessage(text=text))

    df = pd.read_csv("text.csv")
    ### 言葉を覚える ###
    if text == '言葉覚えて':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='完全一致の時は1、部分一致の時は2を入力してねぇ'))
            df.append({'input' : 'text' , 'type' : 'text', 'option' : 1, 'output' : "aa"} , ignore_index=True)
            df.to_csv("text.csv")
            print(df)
        @handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):
            text2 = event.message.text
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text2))
            text3 = event.message.text
            print(text2,text3)

    # 完全一致調査
    df_out = df[(df["input"]==text)]
    ## 完全一致があったら
    if not df_out.empty:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=list(df_out.sample()["output"])[0]))
        #print(list(df_out.sample()["output"])[0])
    ## 完全一致がなかったら
    else:
        df_out = df[(df["option"]==2)]
        #print(df_out)
        text_list = []
        for index, row in df_out.iterrows():
            if row.input in text:
                text_list.append(row.output)
        if text_list:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=random.choice(text_list)))
            #print(random.choice(text_list))
        else:
            df_out = df[(df["option"]==0)]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=list(df_out.sample()["output"])[0]))
            #print(list(df_out.sample()["output"])[0])
    
    """
    if text == 'おはよう':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='おはよ〜'))
    elif text == 'こんにちは':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='疲れたね〜')) 
    elif ('さわさわ' in text) | ('澤部' in text):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='呼んだぁ？？')) 
    elif ('マイクロマジック' in text) :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='マイクロマジックなんかないんだよ!!')) 
    elif ('ターン' in text) :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='楽しみにしててねぇ')) 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='なんでぇ??')) 
    """

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
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix="jpg" + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
            tempfile_path = tf.name

    dist_path = tempfile_path + '.' + "jpg"
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    filepath = os.path.join('static', 'tmp', dist_name) # ユーザから送信された画像のパスが格納されている

    print(filepath)

    # 送信された画像をモデルで判別する
    img = image.load_img(filepath, target_size=(32,32)) # 送信された画像を読み込み、リサイズする
    img = image.img_to_array(img) # 画像データをndarrayに変換する
    data = np.array([img])
    result = model.predict(data) # 分類する
    predicted = result.argmax()

    class_label = ["飛行機","自動車","鳥","猫","鹿","犬","蛙","馬","船","トラック"]
    pred_answer = "これは" + class_label[predicted] + "だねぇ"

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
        event.reply_token, TextSendMessage(text='友だち追加ありがとねぇ'))
        
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host ='0.0.0.0',port = port)