#!/usr/bin/python2

import sys
import urllib
import xml.etree.ElementTree as ET
import os
import argparse

username = "XXXX"
password = "XXXX"

def load(line):
	file = urllib.URLopener()

	try: file.retrieve(line,"data.xml")
	except Exception:
     		print("Error")
       		sys.exit()
       	if os.stat("data.xml").st_size == 0:
        	print "No route or stop was found!"
        	sys.exit()


def busStop(input):

	line = "http://api.reittiopas.fi/hsl/prod/?request=stop&user="+username+"&pass="+password+"&format=xml&code=" + input
	load(line)

	tree = ET.parse("data.xml")
	root = tree.getroot()

	for stop in root.findall("./node"):
		print "\n"
		stop_code = stop.find("code_short").text
		print "Stop: {}".format(stop_code)

		for departures in stop.findall("./departures/"):
			time = departures.find("time").text
			code = departures.find("code").text
			print "{1}{2}{3}{4} ".format(*code),
   			if len(time) == 3:
          			print "0{0}:{1}{2}".format(*time),
			else:
				print "{0}{1}:{2}{3}".format(*time),
   			print(getBusDest(code,root))


def getBusDest(line,root):

    	for dest in root.findall("./node/lines/node"):

		temp = dest.text.split(":")
       		if temp[0] == line:
			return temp[1]


def getLocation(input):

	line = "http://api.reittiopas.fi/hsl/prod/?request=geocode&user="+username+"&pass="+password+"&format=xml&epsg_out=4326&key=" + input
	load(line)

	tree = ET.parse("data.xml")
	root = tree.getroot()
	#loc = root.find("./node/coords").text.split(",")
 	#print("https://www.google.fi/maps/place/" + loc[1] + "," + loc[0])

	return root.find("./node/coords").text

def getRoute(departure, destination):

	line = "http://api.reittiopas.fi/hsl/prod/?request=route&user="+username+"&pass="+password+"&format=xml&epsg_in=4326&from="+departure+"&to="+destination
	load(line)

	tree = ET.parse("data.xml")
	root = tree.getroot()

 	for route in root.findall("./node/node"):
      		flag = 0
      		printedLine = ""

		for stop in route.findall("./legs/node"):
			if(stop.find("type").text == "walk"):
				if(flag == 0):
    					printedLine += "{}{}:{}{}".format(*stop.find("./locs/node[1]/arrTime").text[-4:])
    					flag = 1
        			printedLine += " Walk(" + str(round(float(stop.find("length").text)/1000,1)) + " km) "

    			if(stop.find("code") != None):
				printedLine += " {}{}:{}{}".format(*stop.find("./locs/node/depTime").text[-4:]) + " " + \
				lineFormat(stop.find("code").text) + " " + stop.find("./locs/node/name").text + " " + \
				"{}{}:{}{}".format(*stop.find("./locs/node[last()]/arrTime").text[-4:]) + " "

		print(printedLine + "{}{}:{}{}".format(*stop.find("./locs/node[last()]/arrTime").text[-4:]) + "\n")

def lineFormat(input):
	if(input[0] == "2"):
        	return "{1}{2}{3}{4}".format(*input)
        elif("1300" in input): #check if transport is metro
            return "Metro"
        elif(input[0] == "1"):
            	return "{2}{3}{4}".format(*input)
	return input


def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('-f', type=str, nargs='+', help='From location')
	parser.add_argument('-t', type=str, nargs='+', help='To location')
	parser.add_argument('-s', type=str, nargs='+', help='Bus stop schedule')

	args = parser.parse_args()

 	if(args.s != None and args.f == None and args.t == None):
     		busStop("".join(args.s))
       		sys.exit()
 	elif(args.f != None and args.t != None):
 		empty = getRoute(getLocation("".join(args.f)), getLocation("".join(args.t)))
   	else:
        	print("Invalid command arguments!\n")
         	parser.print_help()
         	sys.exit()


if __name__=="__main__":
	main()
 
