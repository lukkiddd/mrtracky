# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify
import random
import urllib
from firebase import Firebase
import datetime

app = Flask(__name__, static_url_path='')

@app.route('/users_sub', methods=["GET"])
def subscribe_user():
    tracking_id = request.args.get('tracking_id')
    fb_id = request.args.get('fb_id')

    user = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id)
    tracks = user.get()
    print tracks
    found = False
    found_track = ""
    if tracks:
        for track in tracks:
            print track, tracking_id
            if track == tracking_id:
                found = True
                found_track = track
    if not found:
        user.set({tracking_id: {'tag': 'NOT FOUND','subscribe': 'true','created_at':str(datetime.datetime.now())}})
    else:
        track_status = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id + '/'+tracking_id).get()
        user.set({tracking_id: {'tag': track_status['tag'] , 'subscribe': 'true','updated_at':str(datetime.datetime.now()) }})
    message = {
        "messages": [
            {"text": u"ได้เลยครับ ถ้ามีอัพเดท ผมจะติดต่อไปทันที"}
        ]
    }
    return jsonify(message)


@app.route('/tracking_by_courier', methods=["GET"])
def tracking_by_courier():
    courier_link = request.args.get('courier_link')
    fb_id = request.args.get('fb_id')
    status = get_tracking_by_courier(courier_link)
    print status
    if status == None or status == 1:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    elif status == 0:
        user = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id)
        user.set({courier_link.split('/')[-1]: {'tag': 'NOT FOUND', 'courier_link': courier_link,'created_at':str(datetime.datetime.now())}})

        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ ผมกำลังติดต่อให้อยู่"},
                {"text": u"ถ้าผมติดต่อได้แล้วจะทักไปหานะครับ"},
                {
                    "attachment": {
                      "type": "template",
                      "payload": {
                        "template_type": "button",
                        "text": "ต้องการให้ผมคอยอัพเดทสถานะพัสดุด้วยไหมครับ",
                        "buttons": [{
                            "set_attributes": {
                              "tracking_id": courier_link.split('/')[-1]
                            },
                            "type": "show_block",
                            "block_name": "item sub",
                            "title": "อัพเดทด้วย"
                          },
                          {
                            "type": "show_block",
                            "block_name": "nothing",
                            "title": "ไม่เป็นไร"
                          }
                        ]
                      }
                    }
                  }
            ]
        }
    else:
        if status['tag'] == "Delivered":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": u"สถานที่: " + status['place'] },
                  {"text": u"เวลา: " + status['date'] + " | " + status['time'],
                  "quick_replies": [
                    {
                      "title": u"โอเค",
                      "block_names":[u"เมนู"]
                    }
                  ]}
              ]
          }
        else:
          user = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id)
          user.set({data: {'tag': status['tag'],'created_at':str(datetime.datetime.now())}})
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag_th'] },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']},
                  {
                    "attachment": {
                      "type": "template",
                      "payload": {
                        "template_type": "button",
                        "text": "ต้องการให้ผมคอยอัพเดทสถานะพัสดุไหมครับ",
                        "buttons": [{
                            "set_attributes": {
                              "tracking_id": courier_link.split('/')[-1]
                            },
                            "type": "show_block",
                            "block_name": "item sub",
                            "title": "อัพเดทด้วย"
                          },
                          {
                            "type": "show_block",
                            "block_name": "nothing",
                            "title": "ไม่เป็นไร"
                          }
                        ]
                      }
                    }
                  }
              ]
          }
    print message
    return jsonify(message)

def get_tracking_by_courier(courier_link):
    url = courier_link
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    recent = soup.find_all('li',{'class':'checkpoint'})
    if len(recent) <= 0:
        status_text = soup.find('p',{'id':'status-text'})
        print status_text
        if status_text:
            return 0
        return None
    recent = recent[0]
    place = recent.find('div',{'class':'checkpoint__content'}).find('div',{'class':'hint'}).get_text()
    datetime = recent.find('div',{'class':'checkpoint__time'})
    date = datetime.find('strong').get_text()
    tag = soup.find('p',{'class':'tag'}).get_text()
    time = datetime.find('div',{'class':'hint'}).get_text()
    if tag == "In Transit":
        tag_th = u"กำลังจัดส่ง"
    elif tag == "Delivered":
        tag_th = u"ผู้รับได้รับเรียบร้อย"
    elif tag == "Out For Delivery":
        tag_th = u"เตรียมการนำจ่าย"
    elif tag == "Info Received":
        tag_th = u"รับเข้าระบบ"
    else:
        tag_th = u""
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}


@app.route('/tracking_all', methods=["GET"])
def tracking_all():
    data = request.args.get('tracking_id')
    fb_id = request.args.get('fb_id')
    if data.startswith(u'SP'):
        status = get_tracking_shippop(data)
    else:
        status = get_tracking_all(data)
    if isinstance(status, list):
        el = []
        for courier in status:
            el.append(
                {
                  "title": courier['name'],
                  "subtitle": u"ติดตามพัสดุจาก " + courier['name'],
                  "buttons":[
                    {
                      "set_attributes": 
                        {
                          "courier": courier['name'],
                          "courier_link": courier['link']
                        },
                      "type": "show_block",
                      "block_name": "TrackByCourier",
                      "title": "ติดตามพัสดุ"
                    },
                    {
                      "type": "show_block",
                      "block_name": "nothing",
                      "title": "ไม่มีอะไร"
                    }
                  ]
                })

        message = {
             "messages": [
                {
                  "text": u"เอ... Tracky เจอ " + str(len(status)) + u" เจ้า ไม่ค่อยแน่ใจว่าเป็นของเจ้าไหน"
                },
                {
                  "text": u"ไม่ทราบว่าเป็นของผู้บริการเจ้าไหนครับ?"
                },
                {
                  "attachment":{
                    "type":"template",
                    "payload":{
                      "template_type":"generic",
                      "elements": el
                    }
                  }
                }
              ]
            }
        return jsonify(message)
    if status == None or status == 1:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    elif status == 0:
        user = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id)
        user.set({data: {'tag': 'NOT FOUND','created_at':str(datetime.datetime.now())}})
        
        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ ผมกำลังติดต่อให้อยู่"},
                {"text": u"ถ้าผมติดต่อได้แล้วจะทักไปหานะครับ"},
                {
                    "attachment": {
                      "type": "template",
                      "payload": {
                        "template_type": "button",
                        "text": "ต้องการให้ผมคอยอัพเดทสถานะพัสดุด้วยไหมครับ",
                        "buttons": [{
                            "type": "show_block",
                            "block_name": "item sub",
                            "title": "อัพเดทด้วย"
                          },
                          {
                            "type": "show_block",
                            "block_name": "nothing",
                            "title": "ไม่เป็นไร"
                          }
                        ]
                      }
                    }
                  }
            ]
        }
    else:
        if status['tag'] == "Delivered" or u"ผู้รับได้รับเรียบร้อย" in status['tag']:
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": u"สถานที่: " + status['place'] },
                  {"text": u"เวลา: " + status['date'] + " | " + status['time'],
                  "quick_replies": [
                    {
                      "title": u"โอเค",
                      "block_names":[u"เมนู"]
                    }
                  ]
                }
              ]
          }
        else:
          user = Firebase('https://bott-a9c49.firebaseio.com/users/' + fb_id)
          user.set({data: {'tag': status['tag'],'created_at':str(datetime.datetime.now())}})
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag_th'] },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']},
                  {
                    "attachment": {
                      "type": "template",
                      "payload": {
                        "template_type": "button",
                        "text": "ต้องการให้ผมคอยอัพเดทสถานะพัสดุไหมครับ",
                        "buttons": [
                          {
                            "type": "show_block",
                            "block_name": "item sub",
                            "title": "อัพเดทด้วย"
                          },
                          {
                            "type": "show_block",
                            "block_name": "nothing",
                            "title": "ไม่เป็นไร"
                          }
                        ]
                      }
                    }
                  }
              ]
          }
    print message
    return jsonify(message)

def get_tracking_all(tracking_id):
    url = "https://track.aftership.com/"+tracking_id
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    multi_courier = soup.find_all('a',{'class':'courier-detection__courier-link'});
    multi_courier_return = []
    if multi_courier:
        for courier in multi_courier:
            multi_courier_return.append({"name":courier.get_text(),"link": "https://track.aftership.com"+courier['href']})
        return multi_courier_return

    recent = soup.find_all('li',{'class':'checkpoint'})
    if len(recent) <= 0:
        status_text = soup.find('p',{'id':'status-text'})
        print status_text
        if status_text:
            return 0
        return None
    print tracking_id
    courier = soup.find('div',{'class':'courier-info'}).find('h2').get_text()
    recent = recent[0]
    place = recent.find('div',{'class':'checkpoint__content'}).find('div',{'class':'hint'}).get_text()
    datetime = recent.find('div',{'class':'checkpoint__time'})
    date = datetime.find('strong').get_text()
    tag = soup.find('p',{'class':'tag'}).get_text()
    if tag == "In Transit":
        tag_th = u"กำลังจัดส่ง"
    elif tag == "Delivered":
        tag_th = u"ผู้รับได้รับเรียบร้อย"
    elif tag == "Out For Delivery":
        tag_th = u"เตรียมการนำจ่าย"
    elif tag == "Info Received":
        tag_th = u"รับเข้าระบบ"
    else:
        tag_th = u""
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"courier": courier, "place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}

def get_tracking_shippop(tracking_id):
    url = "https://www.shippop.com/tracking/?tracking_code=" + tracking_id
    r = requests.get(url)
    data = r.content
    soup = BeautifulSoup(data)
    current = soup.find_all('div', {'class':'state'})
    if current:
        current = current[-1]
        date = current.find('div',{'class':'date'}).get_text()
        time = current.find('div',{'class':'time'}).get_text()
        tag = current.find('div',{'class':'line-1'}).get_text()
        tag_th = current.find('div',{'class':'line-1'}).get_text()
        place = current.find('div',{'class':'line-2'}).get_text()
        return {"courier": u"shippop", "place": place, "time":time, "date":date, "tag": tag, "tag_th" :tag_th}
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
