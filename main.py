# main.py
import os,random,sys,glob
import json
import errno
import tempfile
#import psycopg2
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage, FollowEvent
)
from tensorflow.keras.models import Sequential, load_model

from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd


app = Flask(__name__)

ABS_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
with open(ABS_PATH+'/conf.json', 'r') as f:
    CONF_DATA = json.load(f)

CHANNEL_SECRET = CONF_DATA['CHANNEL_SECRET']
CHANNEL_ACCESS_TOKEN = CONF_DATA['CHANNEL_ACCESS_TOKEN']
DEVELOPER_ID = CONF_DATA['DEVELOPER_ID']
REMOTE_HOST = CONF_DATA['REMOTE_HOST']
REMOTE_DB_NAME = CONF_DATA['REMOTE_DB_NAME']
REMOTE_DB_USER = CONF_DATA['REMOTE_DB_USER']
REMOTE_DB_PASS = CONF_DATA['REMOTE_DB_PASS']
REMOTE_DB_TB = CONF_DATA['REMOTE_DB_TB']


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)  # アクセストークンを入れてください
handler = WebhookHandler(CHANNEL_SECRET)  # Channel Secretを入れてください
developer_id = DEVELOPER_ID  # あなたのUser IDを入れてください

sawabe_list = glob.glob("sawabe/*")
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

    """
    #reply_token = event.reply_token
    user_id = event.source.user_id
    profiles = line_bot_api.get_profile(user_id=user_id)
    display_name = profiles.display_name
    picture_url = profiles.picture_url
    status_message = profiles.status_message
    # DBへの保存
    try:
        conn = MySQLdb.connect(user=REMOTE_DB_USER, passwd=REMOTE_DB_PASS, host=REMOTE_HOST, db=REMOTE_DB_NAME)
        c = conn.cursor()
        sql = "SELECT `id` FROM`"+REMOTE_DB_TB+"` WHERE `user_id` = '"+user_id+"';"
        c.execute(sql)
        ret = c.fetchall()
        if len(ret) == 0:
            sql = "INSERT INTO `"+REMOTE_DB_TB+"` (`user_id`, `display_name`, `picture_url`, `status_message`, `status`)\
              VALUES ('"+user_id+"', '"+str(display_name)+"', '"+str(picture_url)+"', '"+str(status_message)+"', 1);"
        elif len(ret) == 1:
            sql = "UPDATE `"+REMOTE_DB_TB+"` SET `display_name` = '"+str(display_name)+"', `picture_url` = '"+str(picture_url)+"',\
            `status_message` = '"+str(status_message)+"', `status` = '1' WHERE `user_id` = '"+user_id+"';"
        c.execute(sql)
        conn.commit()
    finally:
        conn.close()
        c.close()
    """



    text = event.message.text
    line_bot_api.push_message(developer_id,
        TextSendMessage(text=text))

    df = pd.read_csv("text.csv")
    ### 言葉を覚える ###
    if text == '言葉覚えて':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='完全一致の時は1、部分一致の時は2を入力してねぇ'))
        df2 = pd.DataFrame([[text ,'text', [1],  "aa"]],columns=['input', 'type', 'option','output'])
        df3 = df.append(df2)
        df3.to_csv("text.csv")
        print(df)

    print("######",text)
    # 完全一致調査
    df_out = df[(df["input"]==text)]
    ## 完全一致があったら
    if not df_out.empty:
        print("###0###")
        print(df_out)
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
            print("###1###")
            print(text_list)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=random.choice(text_list)))
            #print(random.choice(text_list))
        else:
            sawabe_image = random.choice(sawabe_list)
            print("###2###")
            print(sawabe_image)
            df_out = df[(df["option"]==0)]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=list(df_out.sample()["output"])[0]))
            print(sawabe_image)
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url = sawabe_image,
                    preview_image_url = sawabe_image))
            
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