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

app = Flask(__name__, static_url_path='')

@app.route('/tracking_kerry', methods=['GET'])
def tracking_kerry():
    data = request.args.get('tracking_id')
    get_tracking_kerry(data)
    status = get_tracking_kerry(data)
    print status
    if status == None or status == 1:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    elif status == 0:
        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ Tracky กำลังติดต่อให้อยู่ รออีกสักพัก กลับมาเช็คใหม่นะครับ"}
            ]
        }
    else:
        if status['tag'] == "Delivered":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
              ]
          }
        else:
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag'] + " (" + status['tag_th'] + ")" },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
            ]
          }
    print message
    return jsonify(message)

def get_tracking_kerry(tracking_id):
    url = "https://track.aftership.com/kerry-logistics/"+tracking_id
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
        tag_th = u"กำลังส่ง"
    elif tag == "Delivered":
        tag_th = u"ถึงที่หมาย"
    elif tag == "Out For Delivery":
        tag_th = u"กำลังจำหน่าย ตามบ้าน"
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}

@app.route('/tracking', methods=['GET'])
def tracking():
    data = request.args.get('tracking_id')
    get_tracking(data)
    status = get_tracking(data)
    print status
    if status == None or status == 1:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    elif status == 0:
        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ Tracky กำลังติดต่อให้อยู่ รออีกสักพัก กลับมาเช็คใหม่นะครับ"}
            ]
        }
    else:
        if status['tag'] == "Delivered":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
              ]
          }
        else:
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag'] + " (" + status['tag_th'] + ")" },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
              ]
          }
    print message
    return jsonify(message)

def get_tracking(tracking_id):
    url = "https://track.aftership.com/thailand-post/"+tracking_id
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
        tag_th = u"กำลังส่ง"
    elif tag == "Delivered":
        tag_th = u"ถึงที่หมาย"
    elif tag == "Out For Delivery":
        tag_th = u"กำลังจำหน่าย ตามบ้าน"
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}

@app.route('/tracking_by_courier', methods=["GET"])
def tracking_by_courier():
    courier_link = request.args.get('courier_link')
    status = get_tracking_by_courier(courier_link)
    print status
    if status == None or status == 1:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    elif status == 0:
        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ Tracky กำลังติดต่อให้อยู่ รออีกสักพัก กลับมาเช็คใหม่นะครับ"}
            ]
        }
    else:
        if status['tag'] == "Delivered":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
              ]
          }
        else:
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag'] + " (" + status['tag_th'] + ")" },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
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
        tag_th = u"กำลังส่ง"
    elif tag == "Delivered":
        tag_th = u"ถึงที่หมาย"
    elif tag == "Out For Delivery":
        tag_th = u"กำลังจำหน่าย ตามบ้าน"
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}


@app.route('/tracking_all', methods=["GET"])
def tracking_all():
    data = request.args.get('tracking_id')
    # fb_id = request.args.get('fb_id')
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
                  "text": u"เอ... Tracky เจอ" + str(len(status)) + u" เจ้า ไม่ค่อยแน่ใจว่าเป็นของเจ้าไหน"
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
        message = {
            "messages": [
                {"text": u"พัสดุอยู่ในสถานะ Pending นะ ตอนนี้ Tracky กำลังติดต่อให้อยู่ รออีกสักพัก กลับมาเช็คใหม่นะครับ"}
            ]
        }
    else:
        if status['tag'] == "Delivered":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
              ]
          }
        else:
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag'] + " (" + status['tag_th'] + ")" },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date'] + " " + status['time']}
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
    
    courier = soup.find('div',{'class':'courier-info'}).find('h2').get_text()
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
    if tag == "In Transit":
        tag_th = u"กำลังส่ง"
    elif tag == "Delivered":
        tag_th = u"ถึงที่หมาย"
    elif tag == "Out For Delivery":
        tag_th = u"กำลังจำหน่าย ส่งตามบ้าน"
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"courier": courier, "place": place, "date":date, "time":time, "tag":tag, "tag_th" :tag_th}

if __name__ == '__main__':
    app.run(debug=True)
