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

@app.route('/tracking', methods=['GET'])
def tracking():
    data = request.args.get('tracking_id')
    status = get_tracking(data)
    if status == None:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    else:
        message = {
            "messages": [
                {"text": u"ตอนนี้ของอยู่ที่ " + status['place'] + u" เมื่อตอน " + status['date'] + " " + status['time'] }
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
        return None
    recent = recent[-1]
    place = recent.find('div',{'class':'checkpoint__content'}).find('div',{'class':'hint'}).get_text()
    datetime = recent.find('div',{'class':'checkpoint__time'})
    date = datetime.find('strong').get_text()
    time = datetime.find('div',{'class':'hint'}).get_text()
    return {"place": place, "date":date, "time":time}

if __name__ == '__main__':
    app.run(debug=True)
