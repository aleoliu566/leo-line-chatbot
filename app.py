from flask import Flask, request, abort
import os
import urllib.request
import json
import random
import datetime

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

game_1A2B_status = False
game_1A2B_ans = ''
game_1A2B_count = 0

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    resume_url = "https://drive.google.com/file/d/1Q2ry3AevnYWmsRiO2i48203aDgdom5Ps/view?usp=sharing"
    resume_pic = "https://i.imgur.com/DQgSYuT.png"
    global game_1A2B_status, game_1A2B_ans, game_1A2B_count

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
    elif event.message.text == "NBA戰績":
      message = TextMessage(text=NBARank())
      line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == "1A2B":
      game_1A2B_status = True
      digit = ('0123456789')
      game_1A2B_ans = ''.join(random.sample(digit, 4))
      game_1A2B_count = 0
      content = "由電腦隨機生成不重複的四位數字，玩家猜，之後進行提示。\nA代表數字正確位置正確，B代表數字正確位置錯誤。如正確答案為9143，而猜的人猜9436，則是1A2B，其中有一個9的位置對了，記為1A，3和4這兩個數字對了，而位置錯誤，因此記為2B，合起來就是1A2B，接著猜的人再根據出題者的幾A幾B繼續猜，直到猜中（即4A0B）為止"
      message = TextMessage(text=content)
      line_bot_api.reply_message(event.reply_token, message)
      content = "遊戲開始，請開始作答"
      message = TextMessage(text=content)
      line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == "!1A2B":
      game_1A2Bstatus = False
    elif game_1A2B_status:
      game_1A2B_count+=1
      game_1A2B_status, content= game1A2B(game_1A2B_ans, event.message.text, game_1A2B_count)
      message = TextMessage(text=content)
      line_bot_api.reply_message(event.reply_token, message)
    else:
      message = TextMessage(text='無此功能')
      line_bot_api.reply_message(event.reply_token, message)

def NBARank():
  # 時差所以需要減一天
  today = (datetime.datetime.now()-datetime.timedelta(hours=24)).strftime("%Y%m%d")
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

def game1A2B(answer, reply, count):
  a, b = 0, 0
  if len(reply) != 4:
    return True, '格式錯誤，請重新輸入'
  else:
    for i in range(4):
      if reply[i] == answer[i]:
        a += 1
      elif reply[i] in answer:
        b += 1
    if a != 4:
      return True, str(a)+'A'+str(b)+'B '+answer
    elif reply == answer:
      return False, '恭喜你答對了，總共回答'+str(count)+'次'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
