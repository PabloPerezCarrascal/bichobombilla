#!/usr/bin/env python2
# coding: utf-8

from flask import Flask, json, request
import subprocess
import logging
import pdb
import json




GATEWAY_IP='192.168.1.2'
BRIGHTNESS_DELTA=51

locations= {'habitacion':65540, 'salon':65538, 'cocina': 65541}

#color payload:  '{"3311":[{"5707":5800}]}',

color_components={
 'blanco': '{"3311":[{"5707":5800, "5708": 24394, "5709": 25022, "5710": 24884, "5706": "f5faf6"}]}',
 'amarillo': '{"3311":[{"5707":5427, "5708": 42596, "5709": 30015, "5710": 26870, "5706": "f1e0b5"}]}',
 'naranja': '{"3311":[{"5707":4173, "5708": 65279, "5709": 38011, "5710": 24904, "5706": "e78834"}]}',
 'rosa': '{"3311":[{"5707":59789, "5708": 65279, "5709": 32768, "5710": 15729, "5706": "d9337c"}]}',
 'azul': '{"3311":[{"5707":47324, "5708": 51744, "5709": 13107, "5710": 6554, "5706": "6c83ba"}]}',
 'rojo': '{"3311":[{"5707":1490, "5708": 61206, "5709": 38011, "5710": 22282, "5706": "da5d41"}]}'
}


mode_colors={
    'noche': {'habitacion': '{"3311":[{"5850": 1, "5851": 1, "5707":4173, "5708": 65279, "5709": 38011, "5710": 24904, "5706": "e78834"}]}',
                  'salon': '{"3311":[{"5850": 1, "5851": 1, "5707":4173, "5708": 65279, "5709": 38011, "5710": 24904, "5706": "e78834"}]}',
                  'cocina': '{"3311":[{"5850": 1,"5851": 1, "5707":4173, "5708": 65279, "5709": 38011, "5710": 24904, "5706": "e78834"}]}'},
    'cine': {'habitacion': '{"3311":[{"5850": 0, "5851":0}]}',
                    'salon': '{"3311":[{"5850": 1, "5851":20, "5707":5427, "5708": 42596, "5709": 30015, "5710": 26870, "5706": "f1e0b5"}]}',
                    'cocina': '{"3311":[{"5850": 0, "5851":0}]}'}}

def encender_luz(parameters):
    logging.error('encender_luz: parameters: ' + repr(parameters))
    if parameters['localizacion'][0] == 'todo':
        for location in locations.keys():
            send_coap(locations[location], '{"3311":[{"5850":1}]}', 'put')
    else:
        for location in parameters['localizacion']:
            send_coap(locations[location], '{"3311":[{"5850":1}]}', 'put')

def apagar_luz(parameters):
    logging.error('apagar_luz: parameters: ' + repr(parameters))
    if parameters['localizacion'][0] == 'todo':
        for location in locations.keys():
            send_coap(locations[location], '{"3311":[{"5850":0}]}', 'put')
    else:
        for location in parameters['localizacion']:
            send_coap(locations[location], '{"3311":[{"5850":0}]}', 'put')


def bajar_luz(parameters):
    logging.error('bajar_luz: parameters: ' + repr(parameters))
    if parameters['localizacion'][0] == 'todo':
        for location in locations.keys():
            result = send_coap(locations[location], '', 'get')
            logging.error('RESULT:' + result)
            result = json.loads(result.split('\n')[3])
            brightness = result['3311'][0]['5851'] - BRIGHTNESS_DELTA
            brightness = 1 if brightness <1 else brightness
            send_coap(locations[location], '{"3311":[{"5851":'+str(brightness)+'}]}', 'put')
    else:
        for location in parameters['localizacion']:
            result = send_coap(locations[location], '', 'get')
            logging.error('OSTIA YA: ' + result.split('\n')[3])
            result = json.loads(result.split('\n')[3])
            brightness = result['3311'][0]['5851'] - BRIGHTNESS_DELTA
            brightness = 1 if brightness <1 else brightness
            send_coap(locations[location], '{"3311":[{"5851":'+str(brightness)+'}]}', 'put')


def subir_luz(parameters):
    logging.error('subir_luz: parameters: ' + repr(parameters))
    if parameters['localizacion'][0] == 'todo':
        for location in locations.keys():
            result = send_coap(locations[location], '', 'get')
            logging.error('RESULT:' + result)
            result = json.loads(result.split('\n')[3])
            brightness = result['3311'][0]['5851'] + BRIGHTNESS_DELTA
            brightness = 254 if brightness > 255 else brightness
            send_coap(locations[location], '{"3311":[{"5851":'+str(brightness)+'}]}', 'put')
    else:
        for location in parameters['localizacion']:
            result = send_coap(locations[location], '', 'get')
            logging.error('OSTIA YA: ' + result.split('\n')[3])
            result = json.loads(result.split('\n')[3])
            brightness = result['3311'][0]['5851'] + BRIGHTNESS_DELTA
            brightness = 254 if brightness > 255 else brightness
            send_coap(locations[location], '{"3311":[{"5851":'+str(brightness)+'}]}', 'put')


def cambiar_modo(parameters):
    logging.error('cambiar_color: parameters: ' + repr(parameters))
    for location in locations.keys():
        payload = mode_colors[parameters['modos']][location]
        send_coap(locations[location], payload, 'put')
    


def poner_color(parameters):
    logging.error('pon_color: parameters: ' + repr(parameters))
    if parameters['localizacion'][0] == 'todo':
        for location in locations.keys():
            send_coap(locations[location], color_components[parameters['Colores']], 'put')
    else:
        for location in parameters['localizacion']:
            send_coap(locations[location], color_components[parameters['Colores']], 'put')



actions = {
    'encender_luz' : {'function': encender_luz, 'parameters': ['localizacion'] },
    'apagar_luz' : {'function': apagar_luz, 'parameters' : ['localizacion'] },
    'bajar_luz' : {'function': bajar_luz,'parameters' : ['localizacion'] },
    'subir_luz' : {'function': subir_luz, 'parameters' : ['localizacion'] },
    'cambiar_modo' :{'function': cambiar_modo, 'parameters' : ['modos'] },
    'poner_color' : {'function' : poner_color, 'parameters' : ['localizacion','Colores'] }
    }



app=Flask(__name__)


def send_coap(location, payload, method):
    base_command=['./coap-client','-v', '0','-B','5','-T','bicho','-k','2dOMdO8Wjv9Jqp2Z','-m',method,'-e']
    base_command.append(payload)
    coaps_url='coaps://192.168.1.2//15001/{location}'.format(location=location)
    base_command.append(coaps_url)
    try:
        post_coap = subprocess.Popen(base_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd='/home/alarm/libcoap/examples')
        output = post_coap.communicate()[0]
        logging.error('OUTPOUT: ' + output)
        return output
    except subprocess.CalledProcessError:
        logging.error('NOK'+post_coap.stderr)


def find_parameter_in_contexts(contexts, parameter):
    parameter_value=''
    for context in contexts:
        try:
            parameter_value = context['parameters'][parameter]
            if parameter_value != '':
                return parameter_value
        except:
            pass
    return parameter_value

def process_json(data):
    if data['actionIncomplete']:
        logging.error('action incomplete')
        return
    contexts = sorted(data['contexts'], key=lambda k: k['lifespan'], reverse = True )[1:]
    action = data['action']
    for action_key in actions.keys():
        if action_key in action:
            function = actions[action_key]['function']
            parameters = actions[action_key]['parameters']
    found_parameters={}
    for parameter in parameters:
        if parameter in data['parameters'].keys():
            found_parameters[parameter] = eval(data['parameters'][parameter])
            logging.error('PING: '+ repr(found_parameters[parameter]))
        else:
            logging.error('YUJUUUUUU: '+ repr(find_parameter_in_contexts(contexts, parameter)))
            found_parameters[parameter] = eval(find_parameter_in_contexts(contexts, parameter))
    function(found_parameters)


@app.route('/bichobombilla/', methods = ['POST'])
def bichobombilla():
    print request.headers
    if request.headers['Content-Type'] != 'application/json':
        return('invalid request')
    print request.json
    process_json(request.json)
    return '<html>success</html>'



if __name__ == "__main__":
 app.run(host='0.0.0.0',port=55111)
