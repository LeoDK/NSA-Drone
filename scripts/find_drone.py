#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
Trouve s'il y a un drone dans les airs, en utilisant l'output en csv d'une commande airodump-ng.
"""

import sys

#Le fichier .csv à fournir
filename = sys.argv[1]

with open(filename, 'r') as f:
	lines = tuple( l.strip() for l in f )

	for i in range(1, len(lines)-3):
		data = tuple( s.replace(',', '') for s in lines[i].split() )
		#Tous les AR drones 2.0 possèdent un bssid qui commence par cette séquence
		if data[0].startswith('90:03:B7'):
			bssid = data[0]
			channel = data[5]
			essid = data[len(data)-1]
			print "{}\n{}\n{}".format(bssid, channel, essid)
			break
