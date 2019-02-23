from flask import Flask, request, abort
import urllib.request
import json
from datetime import date

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('do2t7mTAD2C4jxfXtdmKx/mP4rHp03EKENmtKlW47qyjKTI8eKxR3pc4FLC5ID4sArkNNgynV13waxIGaX657EMLuM2plWXrGfgM76hzZzUi4QiT2zbRdbXKQ/KC4vKojfJa0mbEuVOWfpIeeuuVwAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('cfbe7778c338b8b2e46e179ced010969')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    resume_url = "https://drive.google.com/file/d/1Q2ry3AevnYWmsRiO2i48203aDgdom5Ps/view?usp=sharing"
    resume_pic = "https://i.imgur.com/DQgSYuT.png"

    if event.message.text == "履歷":
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url=resume_pic,
                title='Resume',
                text='點擊看履歷',
                actions=[
                    URITemplateAction(
                        label='See more',
                        uri=resume_url
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == "NBA排名":
        # message = NBARank()
        message = 'cool'
        line_bot_api.reply_message(event.reply_token, message)

def NBARank():
  today = str(date.today().strftime("%Y%m%d"))

  url = 'https://data.nba.net/prod/v2/'+today+'/scoreboard.json'
  nbaTeamNameUrl = 'https://data.nba.net/prod/v1/2018/teams.json'

  team_data={}
  return_data='NBA今日戰績'

  with urllib.request.urlopen(nbaTeamNameUrl) as response:
    data = json.load(response)
    data = data['league']['standard']
    for i in data:
      team_data[i['tricode']] = i['nickname']

  with urllib.request.urlopen(url) as response:
      data = json.load(response)
      for i in data['games']:
        hTeam = team_data[i['hTeam']['triCode']]
        vTeam = team_data[i['vTeam']['triCode']]
        hTeam_score = i['hTeam']['score'] if i['hTeam']['score'] != '' else '0'
        vTeam_score = i['vTeam']['score'] if i['vTeam']['score'] != '' else '0'
        return_data+= '\n'+ hTeam+' '+hTeam_score+' : '+vTeam_score+' '+vTeam
  return return_data

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
