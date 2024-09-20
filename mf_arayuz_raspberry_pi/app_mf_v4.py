from flask import Flask, Response, render_template
import cv2
import random
import time
import serial
import csv
import datetime
import sys

elapsed_distance = 0.0
distance_covered = 0.0
previous_time = int(time.time())
voltage = 0
basinc = 0
yukseklik = 0
elapsed_time = 0
sure = 0
yaw = 0
pitch = 0
roll = 0
Longitude = 0
Latitude = 0
heading = 0
hiz =0
temp = 0
power = 0
app = Flask(__name__)

def update_elapsed_distance(current_speed, previous_time):
    global elapsed_distance
    global distance_covered
    current_time = int(time.time())
    time_interval = current_time - previous_time
    distance_covered = current_speed * time_interval
    elapsed_distance += float(distance_covered)
    return elapsed_distance, current_time

def update_elapsed_time():
    global elapsed_time
    global sure
    if 'start_time' not in globals():
        global start_time
        start_time = time.time()
    elapsed_time = time.time() - start_time
    sure = int(elapsed_time)

def generate_sensor_data():
    global voltage
    global basinc
    global yukseklik
    global Acc_X
    global Acc_Y
    global Acc_Z
    global Long
    global Lat
    global heading
    global hiz
    global previous_time
    global power
    #ser = serial.Serial("COM22",115200, timeout=0.01)
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)

    while True:
        update_elapsed_time()
        data = ser.readline()
        data = data.decode()
        if data:
            rows = [x for x in data.split(',')]
            voltage = float(rows[0])
            basinc = float(rows[1])
            yukseklik = float(rows[2])
            pitch = float(rows[3])
            roll = float(rows[4])
            yaw = float(rows[5])
            Longitude = float(rows[6])
            Latitude = float(rows[7])
            heading = float(rows[8])
            hiz = float(rows[9])
            temp = float(rows[10])
        else :
            voltage = 0
            basinc = 0
            yukseklik = 0
            Acc_X = 0
            Acc_Y = 0
            Acc_Z = 0
            Longitude = 0
            Latitude = 0
            heading = 0
            hiz = 0
            temp = 0
        print(rows)
        elapsed_distance, previous_time = update_elapsed_distance(hiz, previous_time)
        alinan_yol = int(elapsed_distance)
        
        # Simule la lecture des données de plusieurs capteurs
        #alinan_yol = round(random.uniform(20.0, 30.0), 2)  # Température en degrés Celsius
        #hiz = round(random.uniform(30.0, 70.0), 2)     # Humidité en pourcentage
        #heading = round(random.uniform(0.0, 100.0), 2)  # Pression en hPa
        #sure = round(random.uniform(0.0, 100.0), 2)  # Pression en pourcentage
        #basinc = round(random.uniform(950.0, 1050.0), 2)  # Température en degrés Celsius
        #yukseklik = round(random.uniform(30.0, 70.0), 2)     # Humidité en pourcentage
        #voltage = round(random.uniform(0.0, 100.0), 2)  # Pression en pourcentage
        #amper = round(random.uniform(0.0, 100.0), 2)  # Pression en pourcentage
        #power = round(random.uniform(0.0, 100.0), 2)  # Pression en pourcentage
        
        power = int((100*voltage)/25)
        # Format des données en JSON
        data = f"data: {{\"alinan_yol\": {alinan_yol}, \"hiz\": {hiz}, \"heading\": {heading}, \"sure\": {sure}, \"basinc\": {basinc}, \"yukseklik\": {yukseklik}, \"voltage\": {voltage}, \"power\": {power}, \"Longitude\": {Longitude}, \"Latitude\": {Latitude}, \"temp\": {temp}, \"yaw\": {yaw}, \"pitch\": {pitch}, \"roll\": {roll}}}\n\n"
        
        # Yield les données formatées
        yield data
        
        # Attendre avant de générer une nouvelle donnée
        time.sleep(0.1)
        update_elapsed_time()

def generate_video():
    cap = cv2.VideoCapture(resource)
    rval, frame = cap.read()
    while rval:
        #cv2.imshow("Stream: " + resource_name, frame)
        rval, frame = cap.read()
        if not rval:
            break
        else:
            rval, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/sensor_data')
def sensor_data():
    return Response(generate_sensor_data(), content_type='text/event-stream')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), content_type='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

#if __name__ == '__main__':
#    app.run(debug=True, threaded=True)

if __name__ == '__main__':
    resource = sys.argv[1]
    app.run(host='0.0.0.0', port=80, debug=True, threaded = True)
