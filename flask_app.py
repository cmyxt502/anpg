
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os, sys, json
import splitText

app = Flask(__name__)

#msgAlt not implemented yet
def addContent(currentPlate, msgMain, msgAlt, plateConfig, countryConfig, badgeChoice):

    #Prepopulate config
    plateWidth = plateConfig["width"]
    plateHeight = plateConfig["height"]
    fontSize = plateConfig["fontSize"]
    badgeAreaWidth = plateConfig["badgeWidth"]
    badgeAreaHeight = plateConfig["badgeHeight"]
    verticalOffset = plateConfig["verticalOffset"]

    fontFile = countryConfig["fontFile"]

    font = ImageFont.truetype(os.path.join(sys.path[0], fontFile), fontSize)
    draw = ImageDraw.Draw(currentPlate)

    #Check if single row or double row
    if plateConfig['split']:
        msgFirst, msgNext = splitText.splitText(msgMain)
        msgFirstSize = font.getsize(msgFirst)
        msgNextSize = font.getsize(msgNext)

        if badgeChoice == "none":
            x1 = (plateWidth - msgFirstSize[0]) / 2
            x2 = (plateWidth - msgNextSize[0]) / 2
        else:
            x1 = (plateWidth + badgeAreaWidth - msgFirstSize[0]) / 2
            x2 = (plateWidth + badgeAreaWidth - msgNextSize[0]) / 2
            badgeFile = os.path.join(os.path.join(sys.path[0], "badge"), badgeChoice) + ".png"
            badge = Image.open(badgeFile, 'r')
            #Resize badge
            badgeTrueWidth = badgeAreaWidth
            badgeTrueHeight = int(badge.size[1]*(badgeAreaWidth / float(badge.size[0])))
            badge = badge.resize((badgeTrueWidth, badgeTrueHeight))
            #Get badge background colour
            badgeBGColour = badge.getpixel((5,5))
            #Draw background
            draw.rectangle((0, 0, badgeAreaWidth, badgeAreaHeight), fill=badgeBGColour)
            #Paste badge
            currentPlate.paste(badge, (0, int((badgeAreaHeight - badgeTrueHeight) / 2)))

        y1 = (plateHeight - msgFirstSize[1]) / 2 - verticalOffset
        y2 = (plateHeight - msgNextSize[1]) / 2 + verticalOffset
        #Add text
        draw.text((x1, y1), msgFirst, font=font, fill=(0, 0, 0))
        draw.text((x2, y2), msgNext, font=font, fill=(0, 0, 0))

    else:
        msgSize = font.getsize(msgMain)

        #Check and add badge
        if badgeChoice == "none":
            x = (plateWidth - msgSize[0]) / 2
        else:
            x = (plateWidth + badgeAreaWidth - msgSize[0]) / 2
            badgeFile = os.path.join(os.path.join(sys.path[0], "badge"), badgeChoice) + ".png"
            badge = Image.open(badgeFile, 'r')
            #Resize badge
            badgeTrueWidth = badgeAreaWidth
            badgeTrueHeight = int(badge.size[1]*(badgeAreaWidth / float(badge.size[0])))
            badge = badge.resize((badgeTrueWidth, badgeTrueHeight))
            #Get badge background colour
            badgeBGColour = badge.getpixel((5,5))
            #Draw background
            draw.rectangle((0, 0, badgeAreaWidth, badgeAreaHeight), fill=badgeBGColour)
            #Paste badge
            currentPlate.paste(badge, (0, int((badgeAreaHeight - badgeTrueHeight) / 2)))

        y = (plateHeight - msgSize[1]) / 2
        #Add text
        draw.text((x, y), msgMain, font=font, fill=(0, 0, 0))

def newPlate(msgMain, msgAlt, plateChoice, countryChoice, badgeChoice):

    #Prepopulate config
    plateJSON = os.path.join(os.path.join(sys.path[0], "plate"), plateChoice) + ".json"
    with open(plateJSON) as pjFile:
            plateConfig = json.load(pjFile)

    countryJSON = os.path.join(os.path.join(sys.path[0], "country"), countryChoice) + ".json"
    with open(countryJSON) as cjFile:
            countryConfig = json.load(cjFile)

    frontBGColour = (int(countryConfig["frontBGColourR"]), int(countryConfig["frontBGColourG"]), int(countryConfig["frontBGColourB"]), int(countryConfig["frontBGColourA"]))
    rearBGColour = (int(countryConfig["rearBGColourR"]), int(countryConfig["rearBGColourG"]), int(countryConfig["rearBGColourB"]), int(countryConfig["rearBGColourA"]))

    frontPlate = Image.new('RGBA', (int(plateConfig["width"]), int(plateConfig["height"])), frontBGColour)
    rearPlate = Image.new('RGBA', (int(plateConfig["width"]), int(plateConfig["height"])), rearBGColour)

    #Add content
    addContent(frontPlate, msgMain, msgAlt, plateConfig, countryConfig, badgeChoice)
    addContent(rearPlate, msgMain, msgAlt, plateConfig, countryConfig, badgeChoice)

    #Save File Path
    platePath = os.path.join(sys.path[0], "output")
    platePath = os.path.join(platePath, msgMain)
    frontPlatePath = platePath + " Front.png"
    rearPlatePath = platePath + " Rear.png"

    #Save File
    frontPlate.save(frontPlatePath)
    rearPlate.save(rearPlatePath)
    del frontPlate
    del rearPlate

@app.route('/generate', methods=['GET'])
def generate():
    args = request.args
    msgMain = args.get("msgMain")
    msgAlt = args.get("msgAlt")
    plate = args.get("plate")
    country = args.get("country")
    badge = args.get("badge")
    newPlate(msgMain, msgAlt, plate, country, badge)
    return msgMain


@app.route('/retrieve', methods=['GET'])
def retrieve():
    args = request.args
    msg = args.get("msg")
    side = args.get("side")

    #Retrieve File Path
    platePath = os.path.join(sys.path[0], "output")
    platePath = os.path.join(platePath, msg)
    frontPlatePath = platePath + " Front.png"
    rearPlatePath = platePath + " Rear.png"

    if side == "rear":
        finalPlatePath = rearPlatePath
    else:
        finalPlatePath = frontPlatePath

    return send_file(finalPlatePath)