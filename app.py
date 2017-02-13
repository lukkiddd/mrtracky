# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import random
import urllib

app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["FB_VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "ok", 200

@app.route('/', methods=['POST'])
def webhook():

    data = request.get_json()
    log(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if(not messaging_event["message"].has_key('text')):
                        return "ok", 200

                    status = get_tracking(message_text)
                    if status == None:
                        send_message(sender_id, "เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า")
                        return "ok",200
                    else:
                        send_message(sender_id, u"ตอนนี้ของอยู่ที่ " + status.place + " เมื่อตอน " + status.date + " " + status.time )
                        return "ok", 200
                    return "ok", 200
                        
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                    if(not messaging_event["postback"].has_key('payload')):
                        return "ok", 200

    return "ok", 200

def get_tracking(tracking_id):
    url = "https://track.aftership.com/thailand-post/"+tracking_id
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    recent = soup.find_all('li',{'class':'checkpoint'})
    if len(recent) <= 0:
        return None
    recent = recent[-1]
    place = recent.find('div',{'class':'checkpoint__content'}).find('div',{'class':'hint'}).get_text()
    datetime = recent.find('div',{'class':'checkpoint__time'})
    date = datetime.find('strong').get_text()
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time}

def send_image(recipient_id, image):
    params = {
        "access_token": os.environ["FB_PAGE_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "attachment":{
              "type":"image",
              "payload":{
                "url": image
              }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message(recipient_id, message_text):
    params = {
        "access_token": os.environ["FB_PAGE_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_elements(recipient_id, elements, buttons):
    params = {
        "access_token": os.environ["FB_PAGE_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "top_element_style": "compact",
                    "elements": elements,
                    "buttons": buttons
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_generic(recipient_id, elements):
    params = {
        "access_token": os.environ["FB_PAGE_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
            "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements,
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def log(message):  
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
