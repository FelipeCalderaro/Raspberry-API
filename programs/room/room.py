from random import random, randint, uniform
from datetime import datetime
<<<<<<< HEAD
from time import sleep
import board
import pulseio
import json
import array
import RPi.GPIO as io

=======
import RPi.GPIO as io

## LED INFRARED CLASS CODES
# class IR():
#     IR_BPLUS  0xF700FF
#     IR_BMINUS 0xF7807F
#     IR_OFF 	  0xF740BF
#     IR_ON 	  0xF7C03F
#     IR_R 	  0xF720DF
#     IR_G 	  0xF7A05F
#     IR_B 	  0xF7609F
#     IR_W 	  0xF7E01F
#     IR_B1	  0xF710EF
#     IR_B2	  0xF7906F
#     IR_B3	  0xF750AF
#     IR_FLASH  0xF7D02F
#     IR_B4	  0xF730CF
#     IR_B5	  0xF7B04F
#     IR_B6	  0xF7708F
#     IR_STROBE 0xF7F00F
#     IR_B7	  0xF708F7
#     IR_B8	  0xF78877
#     IR_B9	  0xF748B7
#     IR_FADE   0xF7C837
#     IR_B10	  0xF728D7
#     IR_B11	  0xF7A857
#     IR_B12	  0xF76897
#     IR_SMOOTH 0xF7E817

>>>>>>> b64bb72... hid keys
##### RASPBERRY CONFIGURATION FUNCTIONS ###


def setupPort(pin, mode):
    io.setmode(io.BCM)
    if mode == "out":
        io.setup(pin, io.OUT)
    if mode == "in":
        io.setup(pin, io.IN)
    io.setwarnings(False)


def setupServo(pin, Hz, start):
    setupPort(pin, "out")
    servo = io.PWM(pin, Hz)
    servo.start(start)
    return servo


<<<<<<< HEAD
def setOutHigh(pin):
    io.output(pin, io.HIGH)


def setOutLow(pin):
    io.output(pin, io.LOW)


=======
>>>>>>> b64bb72... hid keys
def svChange(servo, pos):
    servo.ChangeDutyCycle(pos)


def stopIOs():
    io.cleanup()


#######################

equipList = [
    {
        "name": "Ventilador",
        "id": 1,
        "watts": 200,
        "voltage": 220,
        "estimated_A": 0.909,
    },
    {"name": "Televisão", "id": 2, "watts": 50, "voltage": 127, "estimated_A": 0.394,},
    {"name": "Geladeira", "id": 3, "watts": 104, "voltage": 127, "estimated_A": 0.819,},
    {
        "name": "ArCondicionado",
        "id": 4,
        "watts": 697,
        "voltage": 220,
        "estimated_A": 3.168,
    },
]
<<<<<<< HEAD

LED_CONFIG = {}
# to login
credentials = {"felipe": "calderaro", "ana": "galende"}

################ LED STRIPE FUNCTIONS


def readConfigFile():
    with open("programs/room/buttons.json", "r") as file:
        data = json.load(file)
        file.close()
    # tranform each os this values in array

    for key, value in data.items():
        LED_CONFIG[key.upper()] = array.array(
            "L", [value[i] for i in range(len(value))]
        )
    setupPort(4, "out")
    IR_SENDER = io.PWM(4, 38000)
    IR_SENDER.start(0)

    SIGNAL_PERIOD = 1 / 38000

    for time in LED_CONFIG["ON"]:
        # calculate duty cycle
        # DutyCycle = round(((time * (10 ** -6)) / SIGNAL_PERIOD) / 10)
        IR_SENDER.ChangeDutyCycle(25)
        print(time)
        sleep(time * (10 ** -4))
        IR_SENDER.ChangeDutyCycle(0)

    IR_SENDER.ChangeDutyCycle(0)
    io.cleanup()

    # send signal


#####################################

=======
# to login
credentials = {"felipe": "calderaro", "ana": "galende"}

>>>>>>> b64bb72... hid keys

def addEquipments(request):
    try:
        equipList.append(
            {
                "name": request.json["name"],
                "id": len(equipList) + 1,
                "watts": request.json["watts"],
                "voltage": request.json["voltage"],
                "estimated_A": round(
                    request.json["watts"] / request.json["voltage"], 3
                ),
            }
        )
        return {"status": 201}
    except:
        return {"status": 403}


def getEquipments():
    returnDict = {
        "totalWatts": sum([i["watts"] for i in equipList]),
        "equipmentList": equipList,
    }

    return returnDict


def changePowerState(request, servo):
    fromRequest = request.json

    # get id of equip and identify the port of raspberry
    # set that port to low to close the relay
    # id = fromRequest["id"]
    # port = fromRequest["port"]
    current_state = fromRequest["state"]
    if current_state == True:
        current_state = 1
        svChange(servo, 5)

    if current_state == False:
        current_state = 0
        svChange(servo, 1)

    # read the previous state of that port and save
    # change the state
    # read the state of port and if is the oposite of the previous state return true, else return false
    return current_state, True


<<<<<<< HEAD
def changeOnOff(request, pin):
    fromRequest = request.json

    setupPort(pin, "out")

    current_state = fromRequest["state"]
    if current_state == True:
        # set to low
        setOutLow(pin)

    if current_state == False:
        # set to high
        setOutHigh(pin)


=======
>>>>>>> b64bb72... hid keys
def getUniqueEquipment(request):
    try:
        equipmentIndex = None
        for equip in equipList:
            if equip["id"] == request.json["id"]:
                return equip
        return {"status": 204}
    except:
        return {"status": 400}


def currentColor():
    return [randint(0, 255), randint(0, 255), randint(0, 255)]


def randomCode():
    tp = datetime.today().strftime("%d %m %y %H %M")
    print(datetime.today().strftime("%H %M"))
    code = ""
    for i in tp.split(" "):
        if 48 + int(i) > 57:
            vl = 65 + int(i)
        if 65 + int(i) > 90:
            vl = 97 + int(i)
        if 97 + int(i) > 122:
            vl = 122 - int(i)

        code += chr(vl)

    return code


def validateCode(code):
    tp = datetime.today().strftime("%d %m %y %H %M")
    code_value = ""
    for letter in code:
        code_value += str(ord(letter))

    genCode_value = ""
    for letter in randomCode():
        genCode_value += str(ord(letter))

    difference = int(code_value) - int(genCode_value)
    print(difference)
    if difference < 5 and difference >= 0:
        return True
    else:
        return False


def login(request):
    fromRequest = request.json
    if fromRequest["login"] in credentials:
        if fromRequest["pwd"] == credentials[fromRequest["login"]]:
            return {"status": 202}
        else:
            return {"status": 401}
    else:
        return {"status": 204}


def signIn(request):
    fromRequest = request.json

    if validateCode(fromRequest["code"]):
        credentials[fromRequest["login"]] = fromRequest["pwd"]
        return {"status": 202}
    else:
        return {"status": 401}


def getEquipsDailyInfoForChart():
    datasets = []

    for equip in equipList:
        data = []
        totalInfo = {}
        totalInfo["label"] = equip["name"]

        for i in range(1, 24):
            data.append({"x": i, "y": uniform(10.0, 20.0)})

        totalInfo["data"] = data
        totalInfo[
            "backgroundColor"
        ] = f"rgba(249, {randint(62,200)}, {randint(44,150)}, 1)"

        datasets.append(totalInfo)

    return datasets


def getPaymentBill():
    return {"bill": randint(150, 1000)}
