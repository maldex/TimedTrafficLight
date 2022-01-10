#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pip3 install sortedcontainers yattag flask simplejson

import os, sys, requests, time, datetime, threading
import simplejson as json
import RPi.GPIO as GPIO
from flask import Flask, request, Response, jsonify, abort, render_template, redirect, send_from_directory
from yattag import Doc
from sortedcontainers import SortedDict

from pprint import pprint

GPIO.setmode(GPIO.BCM)

class MyGpioLed:
    def __init__(self, pin=26):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.set(False)

    def set(self, value=False):
        GPIO.output(self.pin, value)

    def get(self):
        return GPIO.input(self.pin)

    def toggle(self):
        self.set(self.get() == False)


class TrafficLight():
    states = ['off', 'stop', 'ready', 'go', 'warn', 'on']

    def __init__(self, red=26, ylw=19, grn=13):
        self.leds = {
            "red": MyGpioLed(red),
            "ylw": MyGpioLed(ylw),
            "grn": MyGpioLed(grn)
        }
        self.schedules = {'00:00': 'off'}
        self.scheduler = False
        self.timer_offset = 0
        self.state = None
        self._restore()

        self.alive = True
        threading.Thread(target=self.schedule_checker_thread).start()


    def _save(self):
        with open('last.state', 'w') as f:
            f.write(json.dumps({'state': self.get_state(),
                                'schedules': self.schedules,
                                'scheduler': self.scheduler,
                                'timer_offset': self.timer_offset}, indent=True))


    def _restore(self):
        try:
            with open('last.state', 'r') as f:
                data = json.loads(f.read())
                self.set_state(data['state'])
                self.schedules = data['schedules']
                self.scheduler = data['scheduler']
                self.timer_offset = data['timer_offset']
        except os.error:
            self.set_state('on')

    def get_state(self):
        return self.state

    def set_state(self, state='go'):
        assert state in self.states
        self.state = state
        self._save()
        if state == self.states[0]:  # off
            self.leds['red'].set(False);
            self.leds['ylw'].set(False)
            self.leds['grn'].set(False)
        elif state == self.states[1]:  # stop
            self.leds['red'].set(True)
            self.leds['ylw'].set(False)
            self.leds['grn'].set(False)
        elif state == self.states[2]:  # ready
            self.leds['red'].set(True)
            self.leds['ylw'].set(True)
            self.leds['grn'].set(False)
        elif state == self.states[3]:  # go
            self.leds['red'].set(False)
            self.leds['ylw'].set(False)
            self.leds['grn'].set(True)
        elif state == self.states[4]:  # warn
            self.leds['red'].set(False)
            self.leds['ylw'].set(True)
            self.leds['grn'].set(False)
        elif state == self.states[5]:  # on
            self.leds['red'].set(True)
            self.leds['ylw'].set(True)
            self.leds['grn'].set(True)

    def get_offsetted_time(self):
        return (datetime.datetime.now() + datetime.timedelta(minutes=self.timer_offset)).strftime('%H:%M')

    def get_current_schedule(self):
        current_schedule = list(self.schedules.keys())[0]
        now = int(self.get_offsetted_time().replace(':', ''))
        for schedule in SortedDict(self.schedules).keys():
            if int(schedule.replace(':', '')) <= now:
                current_schedule = schedule
        return current_schedule

    def check_state_change(self):
        if self.scheduler:
            self.set_state(
                self.schedules[self.get_current_schedule()]
            )

    def schedule_checker_thread(self, interval=15):
        while self.alive:
            time.sleep(interval)
            self.check_state_change()
        os._exit(0)


traffic_light = TrafficLight()

app = Flask(__name__)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# the / page
@app.route('/', methods=["GET"])
def url_index():
    doc, tag, text = Doc().tagtext()
    with tag('h1'):
        with tag('a', href='/TrafficLight'):
            text("click here for application")

    with tag('h3'):   text('flask registered endpoints')
    with tag('pre'):
        endpoints = list(map(lambda x: repr(x), app.url_map.iter_rules()))
        endpoints.sort()
        for endpoint in endpoints: text(endpoint + '\n')
    with tag('hr'): text('request.args')
    with tag('pre'):
        for k, v in request.args.items(): text(str(k) + ': ' + str(v) + '\n')
    with tag('hr'): text('request.environ')
    with tag('pre'):
        for k, v in request.environ.items(): text(str(k) + ': ' + str(v) + '\n')
    return Response(doc.getvalue(), mimetype='text/html;charset=UTF-8')

@app.route("/ts", methods=["GET", "POST"])
def url_time_stamp():
    return traffic_light.get_offsetted_time()


@app.route('/get_state/')
def get_state():
    return traffic_light.get_state()

@app.route('/set_state/<value>')
def set_state(value):
    traffic_light.scheduler = False
    traffic_light.set_state(value)
    return get_state()


@app.route("/TrafficLight", methods=["GET", "POST"])
def url_traffic_light():
    if request.environ['REQUEST_METHOD'] == "POST":
        form_data = request.form.to_dict(flat=True)
        pprint(form_data)

        if 'terminate' in form_data and form_data['terminate'].startswith('fixme'):
            print("termination upon web-ui fixme button")
            traffic_light.alive = False
            return render_template("GoodBy.html")

        if 'state' in form_data:
            traffic_light.scheduler = False
            traffic_light.set_state(form_data['state'])

        if 'schedule_action' in form_data:
            if form_data['schedule_action'] == 'del':
                traffic_light.schedules.pop(form_data['s_time'])

            if form_data['schedule_action'] == 'new':
                traffic_light.schedules[form_data['s_time']] = form_data['s_state']
                traffic_light.schedules = SortedDict(traffic_light.schedules)

            if form_data['schedule_action'].endswith('scheduler'):
                traffic_light.scheduler = form_data['schedule_action'].startswith('enable')

        if 'timer_offset' in form_data:
            if form_data['timer_offset_adj'] == "=0":
                traffic_light.timer_offset = 0
            else:
                traffic_light.timer_offset = int(form_data['timer_offset']) + int(form_data['timer_offset_adj'])

        traffic_light.check_state_change()
        return redirect(request.environ['REQUEST_URI'])

    return render_template("TimedTrafficLight.html",
                           current_state=traffic_light.get_state(),
                           all_states=traffic_light.states,
                           schedules=SortedDict(traffic_light.schedules),
                           scheduler=traffic_light.scheduler,
                           current_schedule=traffic_light.get_current_schedule(),
                           current_time=datetime.datetime.now().strftime('%H:%M'),
                           timer_offset=traffic_light.timer_offset,
                           offseted_time=traffic_light.get_offsetted_time()
                           )

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=2400)
    traffic_light.alive = False