from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep, time
from threading import Thread, Event
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

#TSE Thread
thread = Thread()
thread_stop_event = Event()

class example_thread(Thread):
	def __init__(self):
		self.delay = 1
		super(example_thread, self).__init__()
		self.ina = INA219(SHUNT_OHMS)
	def timeSinceEpoch(self):
		print("about to print some stuff in a loop")
		while not thread_stop_event.isSet():
			try:
				self.ina.configure()
				print("Current: %.3f mA" % self.ina.current())
				print("Power: %.3f mW" % self.ina.power())
				print("Voltage: %.3f mV" % self.ina.shunt_voltage())
			except DeviceRangeError as e:
				print(e)
			current = self.ina.current()
			power = self.ina.power()
			voltage = self.ina.shunt_voltage()
			socketio.emit('newnumber', {'current': round(current,2), 'power': round(power,3), 'voltage': round(voltage,3)}, namespace='/data')
			sleep(self.delay)
	def run(self):
		self.timeSinceEpoch()

@app.route('/')
def index():
	return render_template('index2.html')

@socketio.on('connect', namespace='/data')
def test_connect():
	global thread
	print('Client connected')

	if not thread.isAlive():
		print("Starting Thread")
		thread = example_thread()
		thread.start()

@socketio.on('disconnect', namespace='/data')
def test_disconnect():
	print('Client disconnected')

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0',  port=80,)
