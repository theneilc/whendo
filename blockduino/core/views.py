from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime
import json
import cPickle as pickle
from django.views.generic import TemplateView, View
import uuid
import jsonpickle
import time

modules = set(['accel', 'servo', 'led', 'push_button'])

class Accel:
	def __init__(self, data):
		self.data_pin = data['x_pin']
		self.power = data['y_pin']
		self.attribs = ['is_up', 'is_down', 'is_left', 'is_right']
		self.name = 'accel'
		self.sense = True

class Servo:
	def __init__(self, data):
		self.data_pin = data['data_pin']
		self.attribs = ['turn_left', 'turn_right', 'center']
		self.name = 'servo'
		self.sense = False

class LED:
	def __init__(self, data):
		self.power = data['power_pin']
		self.attribs = ['turn_on', 'turn_off']
		self.name = 'led'
		self.sense = False

class PushButton:
	def __init__(self, data):
		self.power = data['power_pin']
		self.attribs = ['is_on', 'is_off']
		self.name = 'push_button'
		self.sense = True

def new_module(request):
	payload = json.loads(request.body)
	mod_name = payload['name']

	if mod_name not in modules:
		resp = HttpResponse()
		resp.status_code = 401
		return resp
	else:
		if mod_name == 'accel':
			obj = Accel(payload['pin_info'])
		elif mod_name == 'servo':
			obj = Servo(payload['pin_info'])
		elif mod_name == 'led':
			obj = LED(payload['pin_info'])
		else:
			obj = PushButton(payload['pin_info'])

		# retrieve flags lookup
		try:
			flags = pickle.load(open('flags.pick'))
		except IOError:
			flags = {}

		uid = str(int(uuid.uuid4()))
		
		f = open(uid + '.pick', 'w')
		pickle.dump(obj, f)
		f.close()

		flags[uid] = False
		f = open('flags.pick', 'w')
		pickle.dump(flags, f)
		f.close()

		resp = HttpResponse()
		resp.status_code = 200
		return resp


# API views
class PollingAPIView(View):

	def get(self, *args, **kwargs):
		try:
			flags = pickle.load(open('flags.pick'))
			resp = []
			for key in flags:
				if not flags[key]:
					resp.append(pickle.load(open(key + '.pick')))
					flags[key] = True
			f = open('flags.pick', 'w')
			pickle.dump(flags, f)
			f.close()
		except IOError:
			resp = []

		return HttpResponse(jsonpickle.encode(resp, unpicklable=False), content_type="application/json")

# Rendering views
class HomeView(TemplateView):
	template_name = 'home.html'
