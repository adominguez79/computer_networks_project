import argparse
import json
from collections import defaultdict
from flask import Flask, request, jsonify
PORT = 54079 #Ports from 54000 to 54150
INPUTJSON = "/escnfs/home/adoming5/computer_networks_project/cp2/data/set1/data-250.json"

app = Flask(__name__)
app = Flask(__name__)
app.secret_key = "secret-key"


def filterData (entry, Day, Month, Year, Direction, Interface):
    # Filter the data based on the Month, Year, and Interface
    if entry['interface'] != Interface and Interface is not None:
        return False

    if entry['direction'] != Direction and Direction is not None :
        return False

    if entry['type'] != 'iperf':
        return False

#    print('Checking the timestamp')
#    print('  Entry: ', entry['timestamp'])
#    print('  Month: ', Month, ' vs. ', entry['timestamp'].split('-')[1])

    if entry['timestamp'].split('-')[1] != str(Month) and Month is not None:
        return False

    if entry['timestamp'].split('-')[0] != str(Year) and Year is not None:
        return False
    
    if entry['timestamp'].split('-')[2][0:2] != str(Day) and Day is not None :
        return False

#    print('Do not filter')
    return True

def getMultidayTests(direction):
    theData = json.loads(open(INPUTJSON).read())
    newJSON = []

    for m in range(1,13):
        month = f"{m:02}"
        for day in range(1,32):
            filteredData = list(filter(lambda entry: filterData(entry, day,month,None,direction,None), theData))
            if len(filteredData) > 1:
                newJSON += filteredData
    newJSON.sort(key=lambda entry: entry['timestamp'])
    return newJSON



@app.route("/data")
def send_data():
    theData = json.loads(open(INPUTJSON).read())
    try:
       month  = request.args["m"]
    except KeyError:
        month = None
    try:
        day = request.args["d"]
    except KeyError:
        day = None
    try:
        year = request.args["y"]
    except KeyError:
        year = None
    try:
        direction = request.args["dir"]
    except KeyError:
        direction = None
    try:
        interface = request.args["if"]
    except KeyError:
        interface = None
    
    filteredData = list(filter(lambda entry: filterData(entry, day, month, year, direction, interface), theData))

    filteredData.sort(key=lambda entry: entry['timestamp'])

    return jsonify(filteredData)

#Get downlink means
@app.route("/dl/stat/mean")
def dl_mean():
    direction = 'downlink'
    theData = getMultidayTests(direction)
    results = {}
    results = defaultdict(lambda:[0,0,0],results)
    for data in theData:
        
        results[data["timestamp"][0:10]][0] += data["tput_mbps"]
        results[data["timestamp"][0:10]][1] += 1
        results[data["timestamp"][0:10]][2] = results[data["timestamp"][0:10]][0] / results[data["timestamp"][0:10]][1]
        print(data["timestamp"][0:10],results[data["timestamp"][0:10]])

    return jsonify(results)

#Send downlink peaks
@app.route("/dl/stat/peak")
def dl_peak():
    direction = 'downlink'
    theData = getMultidayTests(direction)
    results = {}
    results = defaultdict(lambda:[0,0,],results)
    for data in theData:
        
        results[data["timestamp"][0:10]][0] = max(results[data["timestamp"][0:10]][0],data["tput_mbps"])
        results[data["timestamp"][0:10]][1] += 1
        print(data["timestamp"][0:10],results[data["timestamp"][0:10]])

    return jsonify(results)


#Get uplink means
@app.route("/ul/stat/mean")
def ul_mean():
    direction = 'uplink'
    theData = getMultidayTests(direction)
    results = {}
    results = defaultdict(lambda:[0,0,0],results)
    for data in theData:
        
        results[data["timestamp"][0:10]][0] += data["tput_mbps"]
        results[data["timestamp"][0:10]][1] += 1
        results[data["timestamp"][0:10]][2] = results[data["timestamp"][0:10]][0] / results[data["timestamp"][0:10]][1]
        print(data["timestamp"][0:10],results[data["timestamp"][0:10]])

    return jsonify(results)

#Send uplink peaks
@app.route("/ul/stat/peak")
def ul_peak():
    direction = 'uplink'
    theData = getMultidayTests(direction)
    results = {}
    results = defaultdict(lambda:[0,0,],results)
    for data in theData:
        
        results[data["timestamp"][0:10]][0] = max(results[data["timestamp"][0:10]][0],data["tput_mbps"])
        results[data["timestamp"][0:10]][1] += 1
        print(data["timestamp"][0:10],results[data["timestamp"][0:10]])

    return jsonify(results)


if __name__ == '__main__':
    app.debug=True
    app.run(host= '0.0.0.0', port=PORT)