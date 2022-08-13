from flask import Flask, jsonify, request, abort, session, render_template, url_for, redirect, flash, json, Response
import sys
from linebot import (
            LineBotApi, WebhookHandler

        )
from linebot.exceptions import (
            InvalidSignatureError

        )
from linebot.models import (
            MessageEvent, TextMessage, TextSendMessage,ImageSendMessage, ImageMessage

        )

from bson.objectid import ObjectId

from botengine import BotEngine
from lotman.db import MongoConnector
from lotman.lotman import LotMan, OrderMan
from lotman.models import AdminUser, LotConfig
from datetime import datetime, timedelta
import uuid
from bson.json_util import dumps
from filters import play_opt

app = Flask(__name__)
app.secret_key = "sb;-hk;"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.add_template_filter(play_opt)


#login_manager = flask_login.LoginManager()
#login_manager.init_app(app)

line_bot_api = LineBotApi('<KEY>')
handler = WebhookHandler('<KEY>')


botEngine = BotEngine("Tum")
lm = LotMan(datetime(2021, 1, 15))


def setupBot():
    botEngine.setLotman(lm)

    #lm.resetAll()
    '''
    lm.setSpecialNo(["12", "21", "22"], 40)
    lm.setPrize("3hi", 450)
    lm.setPrize("3lo", 100)
    lm.setPrize("2hilo", 65)
    lm.setPrize("swap", 100)
    lm.setPrize("runhi", 3)
    lm.setPrize("runlo", 3)


    lm.setNo("943647", ["239", "864"], ["006", "375"], "86")
    lm.printNo()
    lm.printPrize()

    lm.calNumbers()
    '''

setupBot()

def isLogin():
    if 'user' in session:
        return session['user']
    else:
        return False

@app.route("/")
def hello_world():
    session['token'] = uuid.uuid4().hex
    return jsonify(msg="I love u")

@app.route("/abc")
def abc():
    return jsonify(msg=session['token'])

@app.route("/testbot")
def testbot():
    pass

@app.route('/dashboard/orders', methods=["GET", "POST"])
def dashboard_order():
    if not isLogin():
        return redirect(url_for('login'))

    orders = lm.listOrders()
    if request.method == "POST":

        if 'saveBtn' in request.form:
            confirms = request.form.getlist("order[]")
            for o in orders:
                #print(o._id in confirms, file=sys.stderr)
                if str(o._id) in confirms:
                    o.isConfirm = True
                else:
                    o.isConfirm = False
                o.commit()
            return redirect(url_for("dashboard_order"))

        if 'searchBtn' in request.form:
            buyerName = request.form['buyerName']
            orders  = lm.searchOrder(buyerName)
            return render_template('dashboard_order.html', orders=orders, lm=lm)

    else:
        return render_template('dashboard_order.html', orders = orders, lm=lm)

@app.route('/dashboard/stats')
def dashboard_stats():
    if not isLogin():
        return redirect(url_for('login'))

    stats =  lm.stats()
    return render_template('dashboard_stats.html', stats = stats)

@app.route('/dashboard/config', methods=["POST", "GET"])
def dashboard_config():
    if not isLogin():
        return redirect(url_for('login'))

    configs = lm.listConfig()
    if request.method == "POST":
        if "searchBtn" in request.form:
            pass

    return render_template('dashboard_config.html', configs = configs)

@app.route('/dashboard/config/create', methods=["POST", "GET"])
def dashboard_config_create():

    if not isLogin():
        return redirect(url_for('login'))

    config = LotConfig()
    if request.method == "POST":
        if "saveBtn" in request.form:
            period = datetime.strptime(request.form['period'], "%Y-%m-%d")
            hi = request.form['hi']
            front3 = [request.form['front3_1'], request.form['front3_2']]
            tail3 = [request.form['tail3_1'], request.form['tail3_2']]
            tail2 = request.form['tail2']
            o = lm.setNoPeriod(period, hi, front3, tail3, tail2)
            return redirect(url_for('dashboard_config_edit',cid=o.id))

    return render_template('dashboard_config_form.html', config = config)


@app.route('/dashboard/config/active/<cid>')
def dashboard_config_active(cid):
    if not isLogin():
        return redirect(url_for('login'))

    MongoConnector.db['LotConfig'].update_many({}, {'$set': {'isActive': False}}, upsert=True)
    MongoConnector.db['LotConfig'].update_one({'_id': ObjectId(cid)}, {'$set': {'isActive': True}}, upsert=True)
    #lc = LotConfig.findById(cid)
    lm.restoreLotConfigActive()
    #lm.setLotConfig(lc)


    return redirect(url_for('dashboard_config'))

@app.route('/dashboard/config/edit/<cid>', methods=["POST", "GET"])
def dashboard_config_edit(cid):
    if not isLogin():
        return redirect(url_for('login'))

    config = LotConfig.findById(cid)

    if request.method == "POST":
        #jsdata = request.get_json(force=True)
        #print(request.form.to_dict(), file=sys.stderr)
        #print(request.form.getlist('te'), file=sys.stderr)
        hi = request.form['hi']
        front3 = [request.form['front3_1'], request.form['front3_2']]
        tail3 = [request.form['tail3_1'], request.form['tail3_2']]
        tail2 = request.form['tail2']
        print(request.form, file=sys.stderr)

        config.hi = hi
        config.front3 = front3
        config.tail3 = tail3
        config.tail2 = tail2
        config.prize  = {
                '3hi': request.form['prize_3hi'],
                '3lo': request.form['prize_3lo'],
                '2hilo': request.form['prize_2hilo'],
                'swap': request.form['prize_swap'],
                'runhi': request.form['prize_runhi'],
                'runlo': request.form['prize_runlo'],
                }

        if "saveBtn" in request.form:
            config.commit()
            config.calNumbers()
            #o = lm.setNoPeriod(period, hi, front3, tail3, tail2)
            return redirect(url_for('dashboard_config_edit',cid=config.id))

        if 'calNumberBtn' in request.form:
            config.calNumbers()
            return redirect(url_for('dashboard_config_edit',cid=config.id))

    return render_template('dashboard_config_form.html', config=config)

@app.route('/dashboard/line_events')
def dashboard_lineevent():
    if not isLogin():
        return redirect(url_for('login'))

    events = botEngine.listEvents()
    res = []
    for e in events:
        res.append(e.to_dict())
    #return jsonify(res)

    return render_template('dashboard_lineevent.html', events=events, res=res)

@app.route('/dashboard/messagePhotos')
def dashboard_message_photos():
    if not isLogin():
        return redirect(url_for('login'))

    photos = botEngine.photoMessages()
    photoChecks = list(MongoConnector.db['photoCheckes'].find())
    pcs = {}
    for x in photoChecks:
        pcs[x['messageId']] = x['isCheck']
    return render_template('dashboard_message_photos.html', photos = photos, photoChecks = photoChecks, pcs = pcs)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not isLogin():
        return redirect(url_for('login'))

    report = lm.riskReport()
    #report = None
    return render_template('dashboard.html', report=report)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        email = request.form['email']
        passWd = request.form['password']

        u = lm.login(email, passWd)
        if u is not None:
            session['user']  = u.to_dict()
            print(u.to_dict(), file=sys.stderr)
            #print(dumps(vars(u)), file=sys.stderr)
            flash('Login success', 'success')
            return redirect(url_for("dashboard"))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for("login"))

    return render_template('login.html')

@app.route('/logout', methods=["GET", "POST"])
def checkPhoto():
    if not isLogin():
        return redirect(url_for('login'))

    if request.method == "POST":
        pid = request.form.get('id')
        check = request.form.get('isCheck')
        print_msg(pid)
        print_msg(check)

        if check == "true":
            check = True
        else:
            check = False

        MongoConnector.db['photoCheckes'].find_one_and_update({'messageId': pid}, {'$set': {'isCheck': check}}, upsert=True)
        return jsonify(msg='ok')

@app.route('/logout')
def logout():
    session.pop('user', default=None)
    return redirect(url_for('login'))
'''
@app.route('/webhook')
def webhook():
    return jsonify(msg="ok")
'''

def print_msg(msg):
    app.logger.info(msg)

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    print_msg("handle_image_message")
    print_msg(event)
    message_content = line_bot_api.get_message_content(event.message.id)
    print_msg(message_content)
    profile = line_bot_api.get_profile(event.source.user_id)
    botEngine.recordEvent(event, profile)
    '''
    for chunk in message_content.iter_content():
        fs.putFile(chunk)
    '''
    MongoConnector.putFile(event.message.id, message_content.content, event.message.id, {'display_name': profile.display_name, 'user_id': profile.user_id, 'picture_url': profile.picture_url, 'status_message': profile.status_message}, False)

    MongoConnector.db['photoCheckes'].insert_one({'messageId': event.message.id, 'isCheck': False })

    return line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text="รับภาพแล้ว"),
                    #ImageSendMessage(image_url, image_url),
                ])

@app.route('/gridfs/<messageId>')
def gridfs_img(messageId):
    if not isLogin():
        return redirect(url_for('login'))

    thing = MongoConnector.getFile(messageId)

    #thing = fs.get_last_version(filename=messageId)
    #response.content_type = 'image/jpeg'
    return Response(thing, mimetype='image/jpeg')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    app.logger.info(event)

    profile = line_bot_api.get_profile(event.source.user_id)

    print_msg(profile.display_name)
    print_msg(profile.user_id)
    print_msg(profile.picture_url)
    print_msg(profile.status_message)

    image_url = "https://simplico.net/wp-content/uploads/2022/01/jonny-clow-xZa4JUE7EdM-unsplash-scaled.jpeg"

    botEngine.recordEvent(event, profile)
    print_msg(event)
    reply = botEngine.processLotCommand(event.message.text, profile.display_name,event.message.id )
    line_bot_api.reply_message(
            event.reply_token,[
                    TextSendMessage(text=reply),
                    #ImageSendMessage(image_url, image_url),
                ])



if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
