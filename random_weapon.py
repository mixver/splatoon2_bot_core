import json
import random
from PIL import Image,ImageFont,ImageDraw
import os

font = ImageFont.truetype(os.path.abspath('..')+'\\splatoon2_bot_core'+'\\fonts\\HaiPaiQiangDiaoGunShiJian-2.otf', 36)
finalBackgroundImageWidth=384
finalBackgroundImageHeight=704
# 地图图片倍率
stageImageRate=14
stageImageWidth=16*stageImageRate
stageImageHeight=9*stageImageRate

# 获取splatoon2全部数据
def getSplatoon2Data():
    with open(os.path.abspath('..')+'\\splatoon2_bot_core'+'\\data\\splatoon2-data.json','r',encoding='UTF-8') as  splatoon2Data:
        data=json.load(splatoon2Data)
        return data

# 生成随机数
def getRandomNumber(start,end,length):
    randomNumbers=[random.randint(start,end) for _ in range(length)]
    return randomNumbers

# 生成单张武器详情图
def generateWeaponImage(weapon,sub,special,filename):
    weaponsImage=Image.open(weapon)
    subImage=Image.open(sub)
    specialImage=Image.open(special)

    weaponsImageNew=weaponsImage.resize((128,128),Image.ANTIALIAS)
    subImageNew=subImage.resize((44,44),Image.ANTIALIAS)
    specialImageNew=specialImage.resize((44,44),Image.ANTIALIAS)

    backgroundImage=Image.new('RGBA',(192,128),(0,0,0,0))
    backgroundImage.paste(weaponsImageNew,(0,0,128,128))
    backgroundImage.paste(subImageNew,(138,10,182,54))
    backgroundImage.paste(specialImageNew,(138,64,182,108))

    backgroundImage.save('./tmp/'+filename+'.png')

# 补全图片路径
def generateImagePath(path):
    return os.path.abspath('..')+'\\splatoon2_bot_core'+"\\data"+path

# 合成图片
def composeImage(imagesPath,imagesFormat,imagesWSize,imagesHSize,imagesRow,imagesColumn,imagesSavePath,imagesNames):
    toImage = Image.new('RGBA', (imagesColumn * imagesWSize, imagesRow * imagesHSize)) #创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    for y in range(1, imagesRow + 1):
        for x in range(1, imagesColumn + 1):
            from_image = Image.open(imagesPath + imagesNames[imagesColumn * (y - 1) + x - 1]).resize(
                (imagesWSize, imagesHSize),Image.ANTIALIAS)
            toImage.paste(from_image, ((x - 1) * imagesWSize, (y - 1) * imagesHSize))
    return toImage
 
# 图片添加文字 image: 图片  text：要添加的文本 font：字体
def addTextToImage(image, text, font=font):
  rgbaImage = image.convert('RGBA')
  textOverlay = Image.new('RGBA', rgbaImage.size, (255, 255, 255, 0))
  imageDraw = ImageDraw.Draw(textOverlay)
 
  textSizeX, textSizeY = imageDraw.textsize(text, font=font)
  # 设置文本文字位置
#   text_xy = (rgbaImage.size[0] - textSizeX, rgbaImage.size[1] - textSizeY)
  text_xy = (10, rgbaImage.size[1] - textSizeY-10)
  # 设置文本颜色和透明度
  imageDraw.text(text_xy, text, font=font, fill=(255, 255, 255, 255))
 
  imageWithText = Image.alpha_composite(rgbaImage, textOverlay)
 
  return imageWithText

# 生成随机武器图片头部
def generateRandomWeaponHeader(mode,stageImage):
    imageBefore = Image.new('RGBA',(384,192),'#444')
    imageAfter = addTextToImage(imageBefore, '模式：'+mode)
    stageImage=Image.open(stageImage)
    stageImageNew=stageImage.resize((stageImageWidth,stageImageHeight),Image.ANTIALIAS)
    imageAfter.paste(stageImageNew,(finalBackgroundImageWidth-stageImageWidth-10,10,finalBackgroundImageWidth-10,stageImageHeight+10))
    return imageAfter

def generateFinalRandomWeaponImage(mode,filename,isFestRandom=0):
    splatoon2Data=getSplatoon2Data()
    weaponsData=splatoon2Data['weapons']
    weaponsNumber=len(weaponsData)
    randomNumber=getRandomNumber(0,weaponsNumber-1,8)

    stagesData=splatoon2Data['stages']
    stagesNumber=len(stagesData)
    if isFestRandom==1:
        # 查询祭典随机
        stageRandomNumber=getRandomNumber(23,stagesNumber-1,1)
        mode="涂地"
    else:
        stageRandomNumber=getRandomNumber(0,stagesNumber-1-47,1)
    for k,i in enumerate(randomNumber):
        if(k%2==0):
                generateWeaponImage(generateImagePath(weaponsData[i]['image']),generateImagePath(weaponsData[i]['sub']['image_a']),generateImagePath(weaponsData[i]['special']['image_a']),str(k))
        else:
                generateWeaponImage(generateImagePath(weaponsData[i]['image']),generateImagePath(weaponsData[i]['sub']['image_b']),generateImagePath(weaponsData[i]['special']['image_b']),str(k))


    imagesNames = [name for name in os.listdir('./tmp/') for item in ['.png'] if
            os.path.splitext(name)[1] == item]
    tmpRandomWeaponImage=composeImage('./tmp/',['.png'],192,128,4,2,'./test.png',imagesNames)

    fianlBackgroundImage=Image.new('RGBA',(finalBackgroundImageWidth,finalBackgroundImageHeight),'black')
    headerImage=generateRandomWeaponHeader(mode,generateImagePath(stagesData[stageRandomNumber[0]]['image']))
    weaponsImage=tmpRandomWeaponImage
    fianlBackgroundImage.paste(headerImage,(0,0,384,192))
    fianlBackgroundImage.paste(weaponsImage,(0,192,finalBackgroundImageWidth,finalBackgroundImageHeight))
    fianlBackgroundImage.save(filename)