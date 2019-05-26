#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFTracker version Web
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import settings as s

import requests
import datetime
import os
import locale

# Usage
def usage():
    print 'Usage: RRFTracker.py [options ...]'
    print
    print '--help               this help'
    print
    print 'Room settings:'
    print '  --room ROOM        set room (default=RRF, choose between [RRF, TECHNIQUE, INTERNATIONAL, BAVARDAGE, LOCAL])'
    print
    print 'Log settings:'
    print '  --log-path         set the location of log files'
    print
    print '88 & 73 from F4HWN Armel'

# Convert time in second to minute
def convert_time(time):
    hours = time // 3600
    time = time - (hours * 3600)

    minutes = time // 60
    seconds = time - (minutes * 60)

    if hours == 0:
        return str('{:0>2d}'.format(int(minutes))) + ':' + str('{:0>2d}'.format(int(seconds)))
    else:
        return str('{:0>2d}'.format(int(hours))) + ':' + str('{:0>2d}'.format(int(minutes))) + ':' + str('{:0>2d}'.format(int(seconds)))

# Save stats
def save_stat_node(history, call, duration=0):
    if call != '':
        try:
            if duration == 0:
                history[call][0] += 1
            else:
                history[call][1] += duration
        except KeyError:
            history[call] = [1, duration]

    return history

# Save stats
def save_stat_porteuse(history, call, duration=0):
    if call != '':
        try:
            history[call][0] += 1
            history[call].append(duration)
        except KeyError:
            history[call] = [1, duration]

    return history

# Log write for history
def log_write():

    # Write if init
    if s.init is True:
        log_porteuse('porteuse')
        log_porteuse('porteuse_extended')
        log_node_list()
        log_activity()
        log_node('best')
        log_node('all')
        log_last()
        log_transmit()

        s.init = False

    # Refresh always

    log_abstract()
    log_news()
    log_transmit()
    log_node('all')
    log_elsewhere()

    # Change only if transmitter...
    if s.call_current != '':
        log_last()

    return 0

# Log abstract
def log_abstract():

    data = '[\n'

    locale.setlocale(locale.LC_TIME, '')

    tmp = datetime.datetime.now()
    now = tmp.strftime(' du %A %d/%m/%Y à %H:%M')

    data += '{\n'
    data += '\t"Salon": "' + s.room + '",\n'
    data += '\t"Date": "' + now + '",\n'
    data += '\t"TX total": ' + str(sum(s.qso_hour)) + ',\n'
    data += '\t"Emission cumulée": "' + convert_time(s.day_duration) + '",\n'
    data += '\t"Nœuds actifs": ' + str(len(s.node)) + ',\n'
    data += '\t"Nœuds connectés": ' + str(s.node_count) + ',\n'
    data += '\t"Indicatif": "' + s.call_current + '",\n'
    data += '\t"TOT": ' + str(s.duration) + ',\n'

    tmp = ''
    for n in s.node_list_in:
        tmp += str(n) + ', '
    tmp = tmp[:-2]

    data += '\t"Nœuds entrants": "' + tmp + '",\n'

    tmp = ''
    for n in s.node_list_out:
        tmp += str(n) + ', '
    tmp = tmp[:-2]

    data += '\t"Nœuds sortants": "' + tmp + '",\n'
    data += '\t"Nœuds max": ' + str(s.node_count_max) + ',\n'
    data += '\t"Nœuds min": ' + str(s.node_count_min) + '\n'
    data += '},\n'

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'abstract.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log transmit
def log_transmit():

    if s.duration == 0:
        s.call_current = ''

    if s.call_current == '':
        s.duration = 0

    latitude = 0
    longitude = 0

    if s.call_current != '':
        tmp = s.call_current.split(' ')
        if (len(tmp) > 1):
            if(tmp[1] in s.geolocalisation):
                tmp = s.geolocalisation[tmp[1]].split(' ')
                latitude = tmp[0]
                longitude = tmp[1]

    data = '[\n'

    data += '{\n'
    data += '\t"Indicatif": "' + s.call_current + '",\n'
    data += '\t"Latitude": ' + str(latitude) + ',\n'
    data += '\t"Longitude": ' + str(longitude) + ',\n'
    data += '\t"TOT": ' + str(s.duration) + '\n'
    data += '},\n'

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'transmit.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log history
def log_activity():

    data = '[\n'

    l = 1
    for i in xrange(0, 24):

        x = str('{:0>2d}'.format(int(i)))
        y = str('{:0>2d}'.format(int(l)))
        z = str(s.qso_hour[i])

        x += 'h - ' + y + 'h'

        l += 1

        if l == 24:
            l = 0

        data += '{\n'
        data += '\t"Hour": "' + x + '",\n'
        data += '\t"TX": ' + z + '\n'
        data += '},\n'

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'activity.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log last
def log_last():

    data = '[\n'

    for i in xrange(0, 10):
        if s.call_date[i] == '':
            break
        data += '{\n'
        data += '\t"Date": "' + s.call_date[i] + '",\n'
        data += '\t"Indicatif": "' + s.call[i] + '",\n'
        data += '\t"Durée": "' + convert_time(s.call_time[i]) + '"\n'
        data += '},\n'

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'last.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log node
def log_node(type):
    tmp = sorted(s.node.items(), key=lambda x: x[1])
    tmp.reverse()

    if type == 'best':
        limit = 20
    else:
        limit = 10**4

    data = '[\n'

    p = 1
    for c, t in tmp:
        data += '{\n'
        if type in ['all']:
            data += '\t"Pos": "' + str('{:0>3d}'.format(int(p))) + '",\n'
        data += '\t"Indicatif": "' + c + '",\n'
        if type in ['all']:
            data += '\t"Durée": "' + convert_time(t[1]) + '",\n'
        data += '\t"TX": ' + str(t[0]) + '\n'
        data += '},\n'

        p += 1
        if p > limit:
            break

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + type + '.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log node list
def log_node_list():

    data = '[\n'

    width = 4

    tmp = []
    for n in s.node_list:
        tmp.append(n)
    node_list = sorted(tmp)

    total = len(node_list)
    line = (total / width)

    complete = total - (line * width)

    if complete != 0:
        line += 1
        complete = (line * width) - total
        for n in xrange(0, complete):
            node_list.append('')

    limit = len(node_list)
    indice = 0

    while(indice < limit):
        data += '{\n'
        for e in xrange(0, width - 1):
            data += '\t"Node '+ str(e) +'": "' + node_list[indice + e] + '",\n'
        data += '\t"Node '+ str(e + 1) +'": "' + node_list[indice + e + 1] + '"\n'
        data += '},\n'
        indice += width

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'node_extended.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log special
def log_porteuse(type):
    tmp = sorted(s.porteuse.items(), key=lambda x: x[1])
    tmp.reverse()

    data = '[\n'

    p = 1
    for c, t in tmp:
        if type == 'porteuse':
            if t[0] < 10:
                break

        data += '{\n'
        if type == 'porteuse':
            data += '\t"Pos": "' + str('{:0>3d}'.format(int(p))) + '",\n'
            data += '\t"Indicatif": "' + c + '",\n'
            data += '\t"TX": ' + str(t[0]) + '\n'
        else:
            data += '\t"Pos": "' + str('{:0>3d}'.format(int(p))) + '",\n'
            data += '\t"Indicatif": "' + c + '",\n'
            data += '\t"TX": ' + str(t[0]) + ',\n'

            tmp = ''
            for e in t[1:]:
                tmp += str(e) + ', '
            tmp = tmp[:-2]

            data += '\t"Date": "' + str(tmp) + '"\n'
        data += '},\n'

        p += 1

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + type + '.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log news
def log_news():

    message = ''

    # Nœuds entrants

    tmp = ''
    for n in s.node_list_in:
        tmp += str(n) + ', '
    tmp = tmp[:-2]

    if tmp != '':
        if len(s.node_list_in) == 1:
            message += 'Nœud entrant: ' + tmp + '. '
        else:
            message += 'Nœuds entrants: ' + tmp + '. '

    # Nœuds sortants

    tmp = ''
    for n in s.node_list_out:
        tmp += str(n) + ', '
    tmp = tmp[:-2]

    if tmp != '':
        if len(s.node_list_out) == 1:
            message += 'Nœud sortant: ' + tmp + '. '
        else:
            message += 'Nœuds sortants: ' + tmp + '. '

    if s.minute % 10 == 0:
        message += 'Si vous testez un système, si vous faites des réglages, basculez sur un salon non occupé. '
    elif s.minute % 5 == 0:
        message += 'Si vous constatez un problème (panne, perturbation, etc.), envoyez un mail à admin@f5nlg.ovh afin que nous puissions intervenir. '
    elif s.minute % 3 == 0:
        message += 'Ne monopolisez pas le réseau. Soyez poli et courtois. Respectez les autres utilisateurs. '
    elif s.minute % 2 == 0:
        message += 'Le salon RRF doit être considéré comme une « fréquence d\'appel », pensez à faire QSY sur un des salons annexes. '
    else:
        message += 'Merci de faire des blancs de l\'ordre de 5 secondes ! '
    # Format JSON

    data = '[\n'

    data += '{\n'

    data += '\t"Message": "' + message + '"\n'
    data += '},\n'

    data += ']\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    file = open(s.log_path_day + '/' + 'news.json', 'w')
    file.write(data)
    file.close()

    return 0

# Log everywhere
def log_elsewhere():
    room_other = s.room_list.copy()
    room_other.pop(s.room, None)

    data = '[\n'
    data += '{\n'

    for room in room_other:
        data += '\t"' + room + '": "' + room_other[room]['dtmf'] + '",\n'

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    data += '}, \n'
    data += '{\n'

    tx = []
    time = []
    call = []
    actif = []
    connected = []

    for room in room_other:
        filename = s.log_path + '/' + room + '-today/abstract.json'

        if os.path.isfile(filename):
            with open(filename, 'r') as content_file:
                content = content_file.read()

                # Indicatif 

                search_start = content.find('Indicatif": "')        # Search this pattern
                search_start += 13                                  # Shift...
                search_stop = content.find('"', search_start)       # And close it...

                tmp = content[search_start:search_stop]

                if tmp == '':
                    call.append("Aucune émission en cours")
                else:
                    call.append(tmp)

                # Emission cumulée

                search_start = content.find('Emission cumulée": "') # Search this pattern
                search_start += 21                                  # Shift...
                search_stop = content.find('"', search_start)       # And close it...

                tmp = content[search_start:search_stop]

                time.append(tmp)

                # Emission cumulée
                
                search_start = content.find('TX total": ')          # Search this pattern
                search_start += 11                                  # Shift...
                search_stop = content.find(',', search_start)       # And close it...

                tmp = content[search_start:search_stop]

                tx.append(tmp)

                # Noeuds actifs
                
                search_start = content.find('Nœuds actifs": ')      # Search this pattern
                search_start += 15                                  # Shift...
                search_stop = content.find(',', search_start)       # And close it...

                tmp = content[search_start:search_stop]

                actif.append(tmp)

                # Noeuds connectés
                
                search_start = content.find('Nœuds connectés": ')   # Search this pattern
                search_start += 19                                  # Shift...
                search_stop = content.find(',', search_start)       # And close it...

                tmp = content[search_start:search_stop]

                connected.append(tmp)
                

    tmp = 0
    for room in room_other:
        data += '\t"' + room + '": "' + call[tmp] + '",\n'
        tmp += 1

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    data += '}, \n'
    data += '{\n'

    tmp = 0
    for room in room_other:
        data += '\t"' + room + '": "' + tx[tmp] + '",\n'
        tmp += 1

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    data += '}, \n'
    data += '{\n'

    tmp = 0
    for room in room_other:
        data += '\t"' + room + '": "' + time[tmp] + '",\n'
        tmp += 1

    last = data.rfind(',')
    data = data[:last] + '' + data[last + 1:]

    data += '}\n'
    data += ']\n'

    file = open(s.log_path_day + '/' + 'elsewhere.json', 'w')
    file.write(data)
    file.close()

    return 0