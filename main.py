import cv2
import os
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading

email_update_interval = 600  # sends an email only once in this time interval
video_camera = VideoCamera(flip=True)  # creates a camera object, flip vertically
# object_classifier = cv2.CascadeClassifier("models/facial_recognition_model.xml")  # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'jon'
app.config['BASIC_AUTH_PASSWORD'] = os.environ['AUTH_PASS']
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_epoch = 0

def check_for_objects():
	global last_epoch
	while True:
		try:
			frame, found_obj = video_camera.get_object(object_classifier)
			if found_obj and (time.time() - last_epoch) > email_update_interval:
				last_epoch = time.time()
				print("Sending email...")
				sendEmail(frame)
				print("done!")
		except Exception:
			print("Error sending email: ", sys.exc_info()[0])


def get_temp():
	temp_sensor = '/sys/bus/w1/devices/28-011452c4fbaa/w1_slave'
	with open(temp_sensor, 'r') as file:
		lines = file.readlines()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos + 2:]
			temp_c = float(temp_string) / 1000.0
			return temp_c
		return 100.0


@app.route('/')
@basic_auth.required
def index():
	temparature = get_temp()
	return render_template('index.html', temparature=temparature)


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
	return Response(gen(video_camera),
					mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
	# t = threading.Thread(target=check_for_objects, args=())
	# t.daemon = True
	# t.start()
	app.run(host='0.0.0.0', debug=False)
