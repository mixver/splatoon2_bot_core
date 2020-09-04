import requests
from PIL import Image,ImageFont,ImageDraw 
from io import BytesIO
import time
import os
import shutil

from base_config import TMP_SALMONRUN_DIR,TMP_SALMONRUN_FILE_NAME

# 地图图片倍率
stageImageRate=14
stageImageWidth=16*stageImageRate
stageImageHeight=9*stageImageRate

fontHeight=44
font = ImageFont.truetype(os.path.abspath('..')+'/splatoon2_bot_core'+'/fonts/Paintball_Beta_4a.otf', 24)
fontHaiPai=ImageFont.truetype(os.path.abspath('..')+'/splatoon2_bot_core'+'/fonts/HaiPaiQiangDiaoGunShiJian-2.otf',24)

MINUTES_EPOCH = 60
HOURS_EPOCH = 60 * MINUTES_EPOCH

tmpSalmonRunDir=TMP_SALMONRUN_DIR
tmpSalmonRunFilename=TMP_SALMONRUN_FILE_NAME

# 请求打工数据
def reqSalmonRun():
    apiUrl = "https://splatoon2.ink/data/coop-schedules.json"
    salmonRunData = requests.get(apiUrl).json()
    return salmonRunData

# 补全图片路径
def generateImagePath(path):
    return "https://splatoon2.ink/assets/splatnet"+path

# 获取网络图片数据
def getWebImageData(path):
    response = requests.get(path)
    return Image.open(BytesIO(response.content))

# 生成打工图主体
def generateSalmonRunImage(stage,weapon1,weapon2,weapon3,weapon4):
    stageImage=getWebImageData(stage)
    weapon1Image=getWebImageData(weapon1)
    weapon2Image=getWebImageData(weapon2)
    weapon3Image=getWebImageData(weapon3)
    weapon4Image=getWebImageData(weapon4)
    stageImageNew=stageImage.resize((stageImageWidth,stageImageHeight),Image.ANTIALIAS)
    weapon1ImageNew=weapon1Image.resize((stageImageHeight//2,stageImageHeight//2),Image.ANTIALIAS)
    weapon2ImageNew=weapon2Image.resize((stageImageHeight//2,stageImageHeight//2),Image.ANTIALIAS)
    weapon3ImageNew=weapon3Image.resize((stageImageHeight//2,stageImageHeight//2),Image.ANTIALIAS)
    weapon4ImageNew=weapon4Image.resize((stageImageHeight//2,stageImageHeight//2),Image.ANTIALIAS)
    
    backgroundImage=Image.new('RGBA',(stageImageWidth+stageImageHeight,stageImageHeight),(0,0,0,0))
    backgroundImage.paste(stageImageNew,(0,0,stageImageWidth,stageImageHeight))
    backgroundImage.paste(weapon1ImageNew,(stageImageWidth,0,stageImageWidth+stageImageHeight//2,stageImageHeight//2))
    backgroundImage.paste(weapon2ImageNew,(stageImageWidth+stageImageHeight//2,0,stageImageWidth+stageImageHeight,stageImageHeight//2))
    backgroundImage.paste(weapon3ImageNew,(stageImageWidth,stageImageHeight//2,stageImageWidth+stageImageHeight//2,stageImageHeight))
    backgroundImage.paste(weapon4ImageNew,(stageImageWidth+stageImageHeight//2,stageImageHeight//2,stageImageWidth+stageImageHeight,stageImageHeight))
    return backgroundImage

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

salmonRunData=reqSalmonRun()

# 生成打工图片头部
def generateSalmonRunHeader(time,salmonRunImage,startTimestamp):
    imageBefore = Image.new('RGBA',(stageImageWidth+stageImageHeight,stageImageHeight+fontHeight),'#444')
    imageAfter = addTextToImage(imageBefore, time)
    imageAfter.paste(salmonRunImage,(0,fontHeight,stageImageWidth+stageImageHeight,stageImageHeight+fontHeight))
    imageAfter.save(tmpSalmonRunDir+str(startTimestamp)+'.png')
    return imageAfter

# 合成时间差头部
def generateFinalSalmonRunHeader(time,salmonRun1Image,salmonRun2Image):
    imageBefore = Image.new('RGBA',(stageImageWidth+stageImageHeight,(stageImageHeight+fontHeight)*2+fontHeight),'#444')
    imageAfter = addTextToImage(imageBefore, time,fontHaiPai)
    imageAfter.paste(salmonRun1Image,(
        0,
        fontHeight,
        stageImageWidth+stageImageHeight,
        stageImageHeight+fontHeight*2))
    imageAfter.paste(salmonRun2Image,(
        0,
        fontHeight*2+stageImageHeight,
        stageImageWidth+stageImageHeight,
        (stageImageHeight+fontHeight)*2+fontHeight))
    # imageAfter.save(tmpSalmonRunDir+str(salmonRunData['schedules'][0]['start_time'])+'.png')
    imageAfter.save(tmpSalmonRunDir+tmpSalmonRunFilename)

# 格式化时间戳
def formatTime(timestamp):
    timeArray = time.localtime(timestamp)
    timeStr = time.strftime("%m/%d %H:%M", timeArray)
    return timeStr

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

def formatSalmonRunTime(timestamp):
    if(salmonRunData['schedules'][0]['start_time']<=timestamp and timestamp<=salmonRunData['schedules'][0]['end_time']):
        msg="剩余{}结束".format(
                    diffHoursMinutes(timestamp, salmonRunData['schedules'][0]['end_time']))
    else:
        msg = "还有{}开始".format(
                    diffHoursMinutes(timestamp, salmonRunData['schedules'][0]['start_time']))
    return msg

# 获取文件夹下文件
def getSalmonRunFile(dir):
    salmonRunImageFile=""
    for root, dirs, files in os.walk(dir):
        salmonRunImageFile=files
    return salmonRunImageFile

# 删除已存在文件
def removeIfExist(file: str):
    if os.path.exists(file):
        os.remove(file)

# 获取差集 在a中但是不在b中的元素
def getDiffA(arrA,arrB):
    return list(set(arrA).difference(set(arrB)))

def getSalmonRunData(timestamp):
        if not os.path.exists(tmpSalmonRunDir):
            os.mkdir(tmpSalmonRunDir)
        diffA=getDiffA(getSalmonRunFile(tmpSalmonRunDir),[str(salmonRunData['schedules'][0]['start_time'])+'.png',str(salmonRunData['schedules'][1]['start_time'])+'.png'])
        for v in diffA:
            removeIfExist(tmpSalmonRunDir+v)
        realSalmonRunFile=getSalmonRunFile(tmpSalmonRunDir)
        salmonRunFile=[str(salmonRunData['schedules'][0]['start_time'])+'.png',str(salmonRunData['schedules'][1]['start_time'])+'.png']
        diffSalmonRunFile=getDiffA(salmonRunFile,realSalmonRunFile)
        for k,v in enumerate(diffSalmonRunFile): 
            diffTimestampName=v.split('.')[0]
            for k,v in enumerate(salmonRunData['schedules']):
                if int(diffTimestampName)==v['start_time']:
                    if salmonRunData['details'][k]['weapons'][0]['id'] == "-1" or salmonRunData['details'][k]['weapons'][0]['id'] == "-2":
                        randomWeapon1=salmonRunData['details'][k]['weapons'][0]['coop_special_weapon']['image']
                    else:
                        randomWeapon1=salmonRunData['details'][k]['weapons'][0]['weapon']['image']
                    if salmonRunData['details'][k]['weapons'][1]['id'] == "-1" or salmonRunData['details'][k]['weapons'][0]['id'] == "-2":
                        randomWeapon2=salmonRunData['details'][k]['weapons'][1]['coop_special_weapon']['image']
                    else:
                        randomWeapon2=salmonRunData['details'][k]['weapons'][1]['weapon']['image']

                    if salmonRunData['details'][k]['weapons'][2]['id'] == "-1" or salmonRunData['details'][k]['weapons'][0]['id'] == "-2":
                        randomWeapon3=salmonRunData['details'][k]['weapons'][2]['coop_special_weapon']['image']
                    else:
                        randomWeapon3=salmonRunData['details'][k]['weapons'][2]['weapon']['image']

                    if salmonRunData['details'][k]['weapons'][3]['id'] == "-1" or salmonRunData['details'][k]['weapons'][0]['id'] == "-2":
                        randomWeapon4=salmonRunData['details'][k]['weapons'][3]['coop_special_weapon']['image']
                    else:
                        randomWeapon4=salmonRunData['details'][k]['weapons'][3]['weapon']['image']
                    if 'weapon' in salmonRunData['details'][k]['weapons'][0]:
                        generateSalmonRunHeader(
                        formatTime(salmonRunData['schedules'][k]['start_time'])+'--'+formatTime(salmonRunData['schedules'][k]['end_time']),
                        generateSalmonRunImage(
                        generateImagePath(salmonRunData['details'][k]['stage']['image']),
                        generateImagePath(randomWeapon1),
                        generateImagePath(randomWeapon2),
                        generateImagePath(randomWeapon3),
                        generateImagePath(randomWeapon4)),
                        salmonRunData['schedules'][k]['start_time'])
                    else:
                        generateSalmonRunHeader(
                        formatTime(salmonRunData['schedules'][k]['start_time'])+'--'+formatTime(salmonRunData['schedules'][k]['end_time']),
                        generateSalmonRunImage(
                        generateImagePath(salmonRunData['details'][k]['stage']['image']),
                        generateImagePath(randomWeapon1),
                        generateImagePath(randomWeapon2),
                        generateImagePath(randomWeapon3),
                        generateImagePath(randomWeapon4)),
                        salmonRunData['schedules'][k]['start_time'])
        generateFinalSalmonRunHeader(formatSalmonRunTime(timestamp),Image.open(tmpSalmonRunDir+salmonRunFile[0]),Image.open(tmpSalmonRunDir+salmonRunFile[1]))
        return tmpSalmonRunDir+tmpSalmonRunFilename

t=time.time()
getSalmonRunData(int(t))