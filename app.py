from palworld_admin import commands
from flask import Flask, render_template, jsonify
from flask import request

app = Flask(__name__)

@app.route("/")
def home():
    ## Homepage for Monitor 
    return render_template('home.html', showplayers=commands.showonlineplayers(), player_count=commands.showplayercount())

@app.route("/getdata")
def get_data():
    ## Data that is refreshed every sec to homepage
    data = {
        'showplayers':commands.getplayerlist(), 
        'onlineplayers':commands.showonlineplayers(), 
        'bannedplayers':commands.get_ban_list(),
        'ram':commands.get_ram(),
        'cpu':commands.get_cpu(),
        'player_count': commands.showplayercount(),
        }
    message = {
            'status' : 200,
            'message' : 'OK',
            'data' : data
            }
    resp = jsonify(message)
    return resp

@app.route('/sendbroadcast', methods=['POST'])
def post_message():
    ## HTTP method to grab broadcast message
    return commands.send_broadcast(request.form.get('message').replace(' ','_'))

@app.route("/saveserver")
def push_save():
    ## HTTP method to save world
    return commands.save_world()

@app.route("/shutdown")
def push_shutdown():
    ## HTTP method to shutdown/restart server
    return commands.shutdown()

@app.route('/kickplayer', methods=['POST'])
def kick_player():
    ## HTTP method to kick player
    return commands.kickplayer(request.form.get('id'))

@app.route('/banplayer', methods=['POST'])
def ban_player():
    ## HTTP method to ban player
    return commands.banplayer(request.form.get('id'))

@app.route('/unbanplayer', methods=['POST'])
def unban_player():
    ## HTTP method to unban player
    return commands.unbanplayer(request.form.get('id'))