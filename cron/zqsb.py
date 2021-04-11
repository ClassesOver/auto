# -*- coding: utf-8 -*-
import io
from bs4 import BeautifulSoup
from models.zqsb import Zqsb, ZqsbNews
import re
from flask import Blueprint
from main import scheduler, db, app
import requests
import json
import datetime

zqsb = Blueprint('zqsb', __name__)
url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9c54da14-030f-4d21-a56c-a382e2b28e21'
upload_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=9c54da14-030f-4d21-a56c-a382e2b28e21&type=file'

@scheduler.task('interval',  id='zqsb', hours=1)
@zqsb.route('/send/<ym>/<d>')
def task(ym=None, d=None):
    with app.app_context():
        if not ym or not d :
            now = datetime.datetime.now()
            ym = now.strftime('%Y-%m')
            d = now.strftime('%d')
        base_url = 'http://epaper.stcn.com/paper/zqsb/html/%s/%s/' % (ym, d)
        r = requests.get('%s/node_2.htm' % base_url )
        if r.status_code == 200:
            soup = BeautifulSoup(r.content,"html.parser")
            node = soup.find(id="webtree")
            if node:
                pattern = re.compile(r'今日(\d+)版')
                h = node.find(id="A001")
                l = pattern.findall(h.get_text())
                if not l:
                    return
                np = int(l[0])
                exists =  Zqsb.query.filter_by(np=np).all()
                dls = node.find_all('dl')
    
                for dl in dls:
                    dt = dl.dt
                    title = dt.get_text()
                    re.findall(title, 'A')
                    avp = re.compile(r'第(A\d+)版')
                    ats = avp.findall(title)
                    href = dl.find(class_="pdf").a.attrs.get('href', False)
                    pdf_url = "http://epaper.stcn.com/paper/zqsb/%s" % '/'.join(href.split('/')[3:])
                    print(pdf_url)
                    o = Zqsb(title=title, np=np, pdf_url=pdf_url)
                    news_list = dl.find_all('li')
                    lines = []
                    for new in news_list:
                        l_href = new.a.attrs['href']
                        body = '- [%s](%s)' % (new.get_text(), '%s%s' % (base_url, l_href))
                        lines.append(' > %s' % body)
                        n = ZqsbNews(body=str(new))
                        o.news.append(n)
                    if not exists:
                        db.session.add(o)
                        db.session.commit()
                        
                    content = '''# %s  \n\n\n%s
                    ''' % (title, '\n'.join(lines))
                    data = {
                        "msgtype" : "markdown",
                        "markdown": {
                            "content": content,
                        }}
                    if ats:
                        requests.post(url, json.dumps(data))
                        resp_pdf = requests.get(pdf_url)
                        ur = requests.post(upload_url, files={
                            'files': ('%s.pdf' % title, io.BytesIO(resp_pdf.content), 'application/pdf')
                        })
                        media_id = ur.json()['media_id']
                        send_pdf(media_id)
                        
    return 'ok'



def send_pdf(mid):
    data = {
        "msgtype": "file",
        "file"   : {
            "media_id": mid
        }
    }
    
    requests.post(url, json.dumps(data))
