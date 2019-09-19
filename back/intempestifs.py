#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
RRFTracker version Web
Learn more about RRF on https://f5nlg.wordpress.com
Check video about RRFTracker on https://www.youtube.com/watch?v=rVW8xczVpEo
73 & 88 de F4HWN Armel
'''

import os
import glob
import datetime
import time
import sys
import getopt
import json


# Ansi color
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Usage
def usage():
    print 'Usage: RRFTracker.py [options ...]'
    print
    print '--help               this help'
    print
    print 'Search settings:'
    print '  --path         set path to RRF files (default=/var/www/RRFTracker/)'
    print '  --pattern      set search pattern (default=current month)'
    print
    print '88 & 73 from F4HWN Armel'

# Convert second to time
def convert_second_to_time(time):
    hours = time // 3600
    time = time - (hours * 3600)

    minutes = time // 60
    seconds = time - (minutes * 60)

    if hours == 0:
        return str('{:0>2d}'.format(int(minutes))) + 'm ' + str('{:0>2d}'.format(int(seconds))) + 's'
    else:
        return str('{:0>2d}'.format(int(hours))) + 'h ' + str('{:0>2d}'.format(int(minutes))) + 'm ' + str('{:0>2d}'.format(int(seconds))) + 's'


# Convert time to second
def convert_time_to_second(time):
    if len(time) > 5:
        format = [3600, 60, 1]
    else:
        format = [60, 1]

    return sum([a * b for a, b in zip(format, map(int, time.split(':')))])

def main(argv):

    room_list = {
        'RRF',
    }

    porteuse = dict()
    all = dict()

    tmp = datetime.datetime.now()

    search_path = '/var/www/RRFTracker/'
    search_pattern = tmp.strftime('%Y-%m')

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'path=', 'pattern='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('--path'):
            search_path = arg
        elif opt in ('--pattern'):
            search_pattern = arg

    print color.BLUE + 'Path ' + color.END + search_path,
    print ' with ',
    print color.BLUE + 'Pattern ' + color.END + search_pattern,
    print '...'

    time_super_total = 0

    for r in room_list:
        path = search_path + r + '-' + search_pattern + '-*/rrf.json'
        file = glob.glob(path)
        file.sort()

        time_total = 0

        for f in file:
            if os.path.isfile(f):
                rrf_json = open (f)
                rrf_data = json.load(rrf_json)

                for data in rrf_data['porteuseExtended']:
                    try:
                        porteuse[data[u'Indicatif'].encode('utf-8')] += data[u'TX']
                    except:
                        porteuse[data[u'Indicatif'].encode('utf-8')] = data[u'TX']

                if 'all' in rrf_data:
                    for data in rrf_data['all']:
                        try:
                            all[data[u'Indicatif'].encode('utf-8')] += convert_time_to_second(data[u'Durée'])
                        except:
                            all[data[u'Indicatif'].encode('utf-8')] = convert_time_to_second(data[u'Durée'])

                else:
                    for data in rrf_data['allExtended']:
                        try:
                            all[data[u'Indicatif'].encode('utf-8')] += convert_time_to_second(data[u'Durée'])
                        except:
                            all[data[u'Indicatif'].encode('utf-8')] = convert_time_to_second(data[u'Durée'])


    if 'RRF' in porteuse:
        del porteuse['RRF']
    if 'F5ZIN-L' in porteuse:
        del porteuse['F5ZIN-L']

    tmp = sorted(porteuse.items(), key=lambda x: x[1])
    tmp.reverse()

    i = 1
    for e in tmp:
        print '%03d' % i, 
        print '\t', e[0], '\t',
        if len(e[0]) < 15:
            print '\t',
        print '%03d' % e[1],
        if e[0] in all:
            print '\t', convert_second_to_time(all[e[0]])
        else:
            print '\t', 'Jamais en émission'
        i += 1
        if i == 51:
            break

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
