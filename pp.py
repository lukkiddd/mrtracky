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


def send_broadcast():
    users = Firebase('https://bott-a9c49.firebaseio.com/users/').get()
    for user in users:
        trackings = Firebase('https://bott-a9c49.firebaseio.com/users/'+user).get()
        for track in trackings:
            status = Firebase('https://bott-a9c49.firebaseio.com/users/'+user+'/'+track).get()
            if status.has_key('courier_link'):
                retval = get_tracking_by_courier(status['courier_link'])
            else:
                retval = get_tracking(track)
            print retval
            if retval != 0 and retval != None:
                print retval['tag']
                print status['tag']
                if retval['tag'] != status['tag']:
                    print retval

def get_tracking(tracking_id):
    url = "https://track.aftership.com/"+tracking_id
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    recent = soup.find_all('li',{'class':'checkpoint'})
    if len(recent) <= 0:
        status_text = soup.find('p',{'id':'status-text'})
        if status_text:
            return 0
        return None
    recent = recent[0]
    print tracking_id
    print soup.find('div',{'class':'courier-info'}).find('h2')
    courier = soup.find('div',{'class':'courier-info'}).find('h2').get_text()
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


def get_tracking_by_courier(courier_link):
    url = courier_link
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    recent = soup.find_all('li',{'class':'checkpoint'})
    if len(recent) <= 0:
        status_text = soup.find('p',{'id':'status-text'})
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


def send_message(recipient_id, message_text):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


if __name__ == '__main__':
    send_broadcast()