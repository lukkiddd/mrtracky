@app.route('/tracking_kerry', methods=["GET"])
def tracking_kerry():
    tracking_id = request.args.get('tracking_id')
    fb_id = request.args.get('fb_id')
    status = get_tracking_kerry(tracking_id)

    track = Firebase('https://bott-a9c49.firebaseio.com/users/'+fb_id+'/'+tracking_id)
    track.set('status': status['tag'])
    
    if status == None:
        message = {
            "messages": [
                {"text": u"เอ หาไม่เจอเลย บอกผิดรึเปล่าน้า?"}
            ]
        }
    else:
        if status['tag'] == u"Delivery":
          message = {
              "messages": [
                  {"text": u"พัสดุถึงที่หมายแล้ว"},
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date']}
              ]
          }
        else:
          message = {
              "messages": [
                  {"text": u"สถานะ: " + status['tag_th'] },
                  {"text": status['place']},
                  {"text": u"เวลา: " + status['date']}
              ]
          }
    print message
    return jsonify(message)

def get_tracking_kerry(tracking_id):
    url = "https://th.kerryexpress.com/en/track/?track="+tracking_id
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    colStatus = soup.find('div',{'class':'colStatus'})
    current = colStatus.find_all('div',{'class':'status'})[0]
    date = current.find('div', {'class':'date'}).get_text().replace('  ','').replace('\n',' ')
    status = current.find('div', {'class':'d1'}).get_text().replace('  ','')
    place = current.find('div', {'class':'d2'}).get_text().replace('  ','')
    if len(place) <= 1:
        place = ""
        
    if u"Delivery Successful" in status:
        tag_th = u"ถึงที่หมาย"
    elif u"Out for delivery" in status:
        tag_th = u"กำลังจำหน่าย ส่งตามบ้าน"
    elif u"Arrived at Hub/Transit station" in status:
        tag_th = u"ถึงจุดเตรียมจำหน่าย"
    else:
        tag_th = u"กำลังจัดส่ง"
    if len(status) <= 1:
        return None
    return {"courier": u"kerry", "place": place, "date":date, "tag_th" :tag_th}
