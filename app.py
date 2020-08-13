from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import paho.mqtt.client as mqtt
import json
import os
import time
import socket


Connected = False  # global variable for the state of the connection


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    x = message.payload.decode("utf-8", "strict")
    data = json.loads(x)
    print(data)
    # if(len(data) == 3):
    #     print(data)
    # if(len(data) == 3):
    #     result = data
    #     return redirect(jsonify({"mac": result["mac"], "ch": result["ch"], "br": result["bright"]}))
    # return jsonify({"mac": result["mac"], "ch": result["ch"], "br": result["bright"]}))


broker_address = "mqttservices.obotrons.com"
port = 1883
user = "NDRSolution"
password = "obtBISrons81"

client = mqtt.Client()
client.username_pw_set(user, password=password)
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message
client.connect(broker_address, port=port)
client.loop_start()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/process", methods=['POST'])
def process():
    ch = request.form['channel']
    br = request.form['bright']
    mac = request.form['mac']
    client.subscribe("bis/dimvol/%s/monitor" % mac, 0)
    data = json.dumps({"command": int(ch), "value": br})
    client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)
    return 'OK'


@app.route("/onB", methods=['POST'])
def onB():
    onb = request.form['onb']
    mac = request.form['mac']
    ch = [1, 2, 3, 4]
    for a in ch:
        client.subscribe("bis/dimvol/%s/monitor" % mac, 0)
        data = json.dumps({"command": int(a), "value": "1000"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)
        time.sleep(0.5)
    if (mac == "30AEA49A15B0"):
        data = json.dumps({"command": 50, "value": "1000"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)
        data = json.dumps({"command": 51, "value": "1000"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)

    return 'OK'


@app.route("/offB", methods=['POST'])
def offB():
    offb = request.form['offb']
    mac = request.form['mac']
    ch = [1, 2, 3, 4]
    for a in ch:
        client.subscribe("bis/dimvol/%s/monitor" % mac)
        data = json.dumps({"command": int(a), "value": "0"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)
        time.sleep(0.5)
    if (mac == "30AEA49A15B0"):
        data = json.dumps({"command": 50, "value": "0"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)
        data = json.dumps({"command": 51, "value": "0"})
        client.publish("bis/dimvol/%s/ctrl" % mac, data, 0)

    return 'OK'


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
