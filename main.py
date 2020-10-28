# LIBRARY IMPORTS
from flask import Flask, jsonify, request, make_response, redirect, send_file
from flask_cors import CORS, cross_origin
from multiprocessing import Process, Value
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
from datetime import datetime
import pyscreenshot as ImageGrab
import RPi.GPIO as gpio
import telepot
import json
import psutil

import time
import os
import random
import socket
import requests

# FILE IMPORTS
from programs.sendman import sendman
from programs.room import room

##### FLASK SERVER

app = Flask("API's")
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

######## CONFIGS FOR PROGRAMS #########
# Bot for portifolio
bot = telepot.Bot("TELEGRAM_KEY")

####### SETUP
### CONFIGURE PINS ON RASPBERRY
servopin = 17
# set each pin output mode


# INITIALIZE SERVO WITH PWM IN 50 Hz
servo = room.setupServo(servopin, 60, 5)

##############################
#### FOR FLASK FUNCTIONS ####
def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


#############################
#### ROUTES ######
#  DEFAULT ROUTE #
@app.errorhandler(404)
def page_not_found(error):

    ip = request.remote_addr
    path = request.path
    message = f"New redirected IP: {ip}.\nWas trying to access: {path}"
    if path != "/favicon.ico":
        sendman.send(sendman.chatIds.felipe, message, bot)

    return redirect("https://photricity.com/flw/ajax/", code=302)


##################


@cross_origin()
@app.route("/allow", methods=["GET", "POST", "OPTIONS"])
def register_app_to_notification():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()

    if request.method == "GET":  # CORS preflight
        return _corsify_actual_response(jsonify({"Allowed to connect": "200"}))

    if request.method == "POST":  # CORS preflight
        return jsonify({"Allowed": "200"})


@cross_origin()
@app.route("/get_screen", methods=["GET"])
def get_screen():

    shotNumber = random.randint(0, 99999)

    shot = ImageGrab.grab()
    shot.save(f"/tmp/shot{shotNumber}.png")
    with open(f"/tmp/shot{shotNumber}.png", "rb") as image:
        bot.sendPhoto(sendman.chatIds.felipe, image)
        image.close()

    return send_file(f"/tmp/shot{shotNumber}.png", mimetype="image/png")


#  Portifolio routes
@app.route("/portfolio", methods=["POST", "OPTIONS"])
@cross_origin()
def telegram():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        response = portfolio.sendMessage(
            request.json["name"], request.json["email"], request.json["text"], bot
        )
        return response


#### AUTOMATIC ROOM


@app.route("/room/chart-data")
def chart_data():
    def generate_random_data():
        while True:
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "value": random.random() * 100,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype="text/event-stream")


@app.route("/room/equipments/info", methods=["GET", "POST"])
@cross_origin()
def r():
    if request.method == "GET":
        return jsonify(room.getEquipments())
    else:
        return _corsify_actual_response(jsonify(room.getUniqueEquipment(request)))


@app.route("/room/equipments/add", methods=["POST"])
@cross_origin()
def add():
    return room.addEquipments(request)


@app.route("/room/codegenerate", methods=["GET"])
@cross_origin()
def sendCode():
    code = room.randomCode()
    bot.sendMessage(chat_id=277634087, text=f"New generated code: {code}")
    return {"code": code}


@app.route("/room/validate", methods=["POST"])
@cross_origin()
def codeValidate():
    if room.validateCode(request.json["code"]):
        return _corsify_actual_response(jsonify({"status": 202}))
    else:
        return _corsify_actual_response(jsonify({"status": 401}))


@app.route("/room/signin", methods=["POST"])
@cross_origin()
def signIn():
    return _corsify_actual_response(jsonify(room.signIn(request)))


@app.route("/room/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        return jsonify(room.login(request))


@app.route("/room/changeState", methods=["POST", "OPTIONS"])
@cross_origin()
def changeState():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        state, response = room.changePowerState(request, servo)

        # sendman.send(
        #    sendman.chatIds.ana,
        #    f"Estado alterado {response}. Novo estado: {state}",
        #    bot,
        # )
        # sendman.send(
        #    sendman.chatIds.felipe,
        #    f"Estado alterado {response}. Novo estado: {state}",
        #    bot,
        # )
        return jsonify({"status": 202})


@app.route("/room/color")
@cross_origin()
def c():
    return jsonify({"color": room.currentColor()})


@app.route("/room/info", methods=["GET"])
@cross_origin()
def bi():
    info = {}
    info["payment"] = room.getPaymentBill()
    info["datasets"] = room.getEquipsDailyInfoForChart()

    return jsonify({"info": info})


#### ANIMES ROUTES
@app.route("/last_updates", methods=["GET"])
@cross_origin()
def lastUps():
    goyabu.getLastEpisodes()


# system information
def dateDiffInSeconds(date1, date2):
    timedelta = date1 - date2
    return timedelta.days * 24 * 3600 + timedelta.seconds


def daysHoursMinutesSecondsFromSeconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return (hours, minutes, seconds)


def uptime(boot_time):

    req = datetime.strptime(boot_time, "%d-%m-%Y %H:%M:%S")
    now = datetime.now()

    return "%d:%d:%d" % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, req))


@app.route("/sysinfo", methods=["GET"])
@cross_origin()
def systeminfo():
    try:
        battery_percent = round(float(psutil.sensors_battery().percent), 3)
    except:
        battery_percent = 100.00
    cpu_percent = float(psutil.cpu_percent())

    CPU_frequency_dict = {}
    CPU_frequency = psutil.cpu_freq(percpu=True)

    for i in range(psutil.cpu_count()):
        CPU_frequency_dict["CPU{}".format(i + 1)] = {
            "current": CPU_frequency[i].current,
            "min": CPU_frequency[i].min,
            "max": CPU_frequency[i].max,
        }

    temperatures = {}
    fans_speed = {}

    # sensors_temperatures = psutil.sensors_temperatures()
    sensors_fans = psutil.sensors_fans()

    # print("getting sensors temperature")
    # for keys in sensors_temperatures.keys():
    #     for sensor in sensors_temperatures[keys]:
    #         temperatures[sensor.label + "_celsius"] = sensor.current

    for keys in sensors_fans.keys():
        for i, sensor in enumerate(sensors_fans[keys]):
            fans_speed["fan{}_RPM".format(i)] = sensor.current

    data = {
        "SysTime": time.ctime(),
        "Battery": battery_percent,
        "CPU": {
            "CPU_cores_count": psutil.cpu_count(),
            "CPU_usage": cpu_percent,
            "CPU_IDLE_percent": psutil.cpu_times_percent().idle,
            # "CPU_user_process_time_spent": psutil.cpu_times_percent().user,
            # "CPU_system_process_time_spent": psutil.cpu_times_percent().system,
            "CPU_frequency": CPU_frequency_dict,
        },
        "RAM_usage": {
            "percent": psutil.virtual_memory().percent,
            "active_GB": round(psutil.virtual_memory().active / 1000000000, 3),
            "inactive_GB": round(psutil.virtual_memory().inactive / 1000000000, 3),
        },
        "Disk ussage": {
            "percent": psutil.disk_usage("/").percent,
            "total_GB": psutil.disk_usage("/").total / 1000000000,
            "free_GB": psutil.disk_usage("/").free / 1000000000,
            "used_GB": psutil.disk_usage("/").used / 1000000000,
        },
        "Network": {
            "MB_sent": round(psutil.net_io_counters().bytes_sent / 1000000, 3),
            "MB_recv": round(psutil.net_io_counters().bytes_recv / 1000000, 3),
            "current_IP": getIp(),
            "current_PORT": psutil.net_connections()[-1].laddr.port,
        },
        "temperature_sensors": temperatures,
        "fan_speed_sensors": fans_speed,
        "Boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%d-%m-%Y %H:%M:%S"
        ),
        "uptime": uptime(
            datetime.fromtimestamp(psutil.boot_time()).strftime("%d-%m-%Y %H:%M:%S")
        ),
    }

    return jsonify(data)


@app.route("/sysinfo/process", methods=["GET"])
@cross_origin()
def get_processes():
    data = []
    for process_index, process in enumerate(psutil.process_iter()):
        data.append({"process_name": process.name(), "process_PID": process.pid})

    return jsonify({"Processes": data})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 34939))
    # Process(target=someFunction, args=(x,)).start()
    app.run(host=getIp(), port=port, debug=True, threaded=True)
    # app.run(host=getIp(), port=port, debug=True, threaded=True, ssl_context="adhoc")
    # last_update()
