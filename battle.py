import requests
from PIL import Image,ImageFont,ImageDraw
from translation import STAGES,BATTLE_TYPES,TIME
import time
import os
# 地图图片倍率
stageImageRate=20
stageImageWidth=16*stageImageRate
stageImageHeight=9*stageImageRate

fontHeight=44
print(os.path.abspath('..')+'/splatoon2_bot_core')
font = ImageFont.truetype(os.path.abspath('..')+'/splatoon2_bot_core'+'/fonts/Paintball_Beta_4a.otf', 24)
fontHaiPai=ImageFont.truetype(os.path.abspath('..')+'/splatoon2_bot_core'+'/fonts/HaiPaiQiangDiaoGunShiJian-2.otf',24)
MINUTES_EPOCH = 60
HOURS_EPOCH = 60 * MINUTES_EPOCH
# 图片添加文字 image: 图片  text：要添加的文本 font：字体
def addTextToImage(image, text, font=font):
  rgbaImage = image.convert('RGBA')
  textOverlay = Image.new('RGBA', rgbaImage.size, (255, 255, 255, 0))
  imageDraw = ImageDraw.Draw(textOverlay)
 
  textSizeX, textSizeY = imageDraw.textsize(text, font=font)
  # 设置文本文字位置
#   text_xy = (rgbaImage.size[0] - textSizeX, rgbaImage.size[1] - textSizeY)
  text_xy = (10, 10)
  # 设置文本颜色和透明度
  imageDraw.text(text_xy, text, font=font, fill=(255, 255, 255, 255))
 
  imageWithText = Image.alpha_composite(rgbaImage, textOverlay)
 
  return imageWithText

API_LEAGUE = "league"
API_RANKED = "gachi"
API_REGULAR = "regular"
CN_LEAGUE = "组排"
CN_RANKED = "单排"
CN_REGULAR = "涂地"

MODES = {API_LEAGUE: CN_LEAGUE, API_RANKED: CN_RANKED, API_REGULAR: CN_REGULAR}
def reqSchedule(mode,reqTime):
    apiUrl="https://splatoon2.ink/data/schedules.json"
    scheduleData=requests.get(apiUrl).json()
    for schedule in scheduleData.get(mode, []):
        startTime = schedule["start_time"]
        endTime = schedule["end_time"]
        if startTime <= reqTime <= endTime:
            return schedule

def generateBattleImage(remainingTime,mode,mapAName,mapA,mapBName,mapB,filename):
    remainingTimeImage=addTextToImage(Image.new('RGBA',(stageImageWidth,fontHeight),'#444'),remainingTime,fontHaiPai)
    modeImage=addTextToImage(Image.new('RGBA',(stageImageWidth,fontHeight),'#444'),mode,fontHaiPai)
    mapANameImage=addTextToImage(Image.new('RGBA',(stageImageWidth,fontHeight),'#444'),mapAName,fontHaiPai)
    mapAImage=Image.open(mapA)
    mapAImageNew=mapAImage.resize((stageImageWidth,stageImageHeight),Image.ANTIALIAS)
    mapBNameImage=addTextToImage(Image.new('RGBA',(stageImageWidth,fontHeight),'#444'),mapBName,fontHaiPai)
    mapBImage=Image.open(mapB)
    mapBImageNew=mapBImage.resize((stageImageWidth,stageImageHeight),Image.ANTIALIAS)
    
    backgroundImage=Image.new('RGBA',(stageImageWidth,stageImageHeight*2+fontHeight*4),'#444')
    backgroundImage.paste(remainingTimeImage,(0,0,stageImageWidth,fontHeight))
    backgroundImage.paste(modeImage,(0,fontHeight,stageImageWidth,fontHeight*2))
    backgroundImage.paste(mapANameImage,(0,fontHeight*2,stageImageWidth,fontHeight*3))
    backgroundImage.paste(mapAImageNew,(0,fontHeight*3,stageImageWidth,fontHeight*3+stageImageHeight))
    backgroundImage.paste(mapBNameImage,(0,fontHeight*3+stageImageHeight,stageImageWidth,fontHeight*4+stageImageHeight))
    backgroundImage.paste(mapBImageNew,(0,fontHeight*4+stageImageHeight,stageImageWidth,fontHeight*4+stageImageHeight*2))
    backgroundImage.save(filename)

# 计算时间差
def diffHoursMinutes(epoch1: float, epoch2: float):
    diffTime=abs(epoch1 - epoch2) / HOURS_EPOCH
    if diffTime<1:
        minutes=int(diffTime*MINUTES_EPOCH)
        return "%s分钟"%(minutes)
    else:
        hours=int(diffTime)
        minutes=int(abs(diffTime-hours)*MINUTES_EPOCH)
        return "%s小时%s分钟"%(hours,minutes)

def formatRemainingTime(start,end,now):
    if(start<=now<=end):
        msg="剩余{}结束".format(
                    diffHoursMinutes(now, end))
    else:
        msg = "还有{}开始".format(
                    diffHoursMinutes(now, start))
    return msg
# 补全图片路径
def generateImagePath(path):
    return os.path.abspath('..')+'/splatoon2_bot_core'+"/data"+path

def dictGet(d: dict, key: str):
    return d.get(key, key)

def getBattleImage(mode,reqTime,filename):
    t=time.time()
    battleInfoData=reqSchedule(mode,reqTime)
    remainingTime=formatRemainingTime(battleInfoData['start_time'],battleInfoData['end_time'],int(t))
    generateBattleImage(
        remainingTime,
        '模式：'+dictGet(BATTLE_TYPES,battleInfoData['rule']['name']),
        dictGet(STAGES,battleInfoData['stage_a']['name']),
        generateImagePath(battleInfoData['stage_a']['image']),
        dictGet(STAGES,battleInfoData['stage_b']['name']),
        generateImagePath(battleInfoData['stage_b']['image']),
        filename
    )
    return filename