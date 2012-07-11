#!/usr/bin/python

"""
@Suneel Vana: This is the latest working version
Script to geneate load testing data for Magpie.

HOW TO RUN:
-----------
./LoadBees.py -h
"""


import os, sys, time
import datetime
import subprocess
import requests
import argparse
import random
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

BVID = ''
BVSID = ''
CLIENT = ['ABC', 'GOOG', 'MAG227', 'MAG339', 'MAG341']
MODE = ['old', 'single' , 'batch']
CLASS  = ['SCI', 'PageView', 'Conversion', 'PIIConversion', 'PageView', 'Transaction', 'SCI',]
EVENTTYPE = ['Sort', 'ReadAll', 'ProductFollow', 'Read', 'Associate', 'CustomClick', 'Default', 'Media', 'ProductLink', 'Paginate',
             'Write', 'Shoutit', 'Transaction', 'ProfileLink', 'AttributeFilter', 'SocialAlerts' , 'SubmitActivity']
BRAND = ["test"]
BVPRODUCT = ["RatingsAndReviews", "AskAndAnswer", "Stories", "Profiles"]
CHOST = ["example.com", "reviewsTest.com"]
COMMANDLIST = []
COOKIEMONSTER_DNS = ""
LOGFILE = ""


def set_new_cookies():
	""" Get new cookies from Cookiemonster """
	global BVID, BVSID
	URL = 'http://' + COOKIEMONSTER_DNS + '/t.gif?client=COOKIE&type=COOKIE&dc=test&cl=SCI'
	##print "URL:", URL
	response = requests.get(URL)
	BVID = response.cookies['BVSID']
	BVSID = response.cookies['BVID']
	print "\n COOKIES:", BVID, BVSID


def getBatchEvents():
	half1st = "(charset:UTF-8,cid:testCategory1031,fieldErrors:!n,geo:1,host:example.com,lang:en-us,pageStatus:!n,pageType:!n,pid:test1,ref:'http://example.com/',"
	half2nd = "res:'1680x1050',rootCid:testCategory1030,subject:Product,t:'(con:0,dns:0,load:-1330633078788,req:484,res:0,tot:-1330633078296)',version:'1.0',"
	cl = random.choice(CLASS)
	if cl == 'SCI':
		InputString = 'brand:test,bvproduct:' + random.choice(BVPRODUCT) + ',cl:' + cl + ',type:' + random.choice(EVENTTYPE) + ')'
	elif cl == 'PageView':
		InputString = 'brand:test,bvproduct:' + random.choice(BVPRODUCT) + ',cl:' + cl + ',type:' + random.choice(["Read", "Write", "Read"]) + ')'
	elif cl == 'Conversion':
		InputString = 'brand:test,bvproduct:' + random.choice(BVPRODUCT) + ',cl:' + cl + ',type:' + random.choice(["SubmitOrder", "Transaction", "StoreLocate"]) + ')'
	elif cl == 'PIIConversion':
		InputString = 'brand:test,bvproduct:' + random.choice(BVPRODUCT) + ',cl:' + cl + ',type:' + random.choice(["SubmitOrder", "Transaction", "StoreLocate"]) + ')'	
	elif cl == 'Transaction':
		InputString = 'brand:test,bvproduct:' + random.choice(BVPRODUCT) + ',cl:' + cl + ',type:' + random.choice(["proxy", "value", "Items"]) + ')'

	BatchEvent = half1st + half2nd + InputString 
	return BatchEvent


def getSingleEvent():
	half1st = "&bvid=" + BVID + '&bvsid=' + BVSID + "&version=1.0&subject=Product&pid=test1&cid=testCategory1031&rootCid=testCategory1030&&pageType=null&pageStatus=null&fieldErrors=null&"
	half2nd = "&host=example.com&ref=http://localhost:8980/&res=1680x1050&lang=en-us&charset=UTF-8&geo=1&t=%28con:0,dns:0,load:-1330633078788,req:484,res:0,tot:-1330633078296%29"
	#print "Single Event"
	cl = random.choice(CLASS)
	if cl == 'SCI':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(EVENTTYPE)
	elif cl == 'PageView':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(["Read", "Write", "Read"])
	elif cl == 'Conversion':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(["StoreLocate", "Transaction", "SubmitActivity"])
	elif cl == 'PIIConversion':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(["StoreLocate", "Transaction", "SubmitActivity"])
	elif cl == 'Transaction':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(["Proxy", "Purchase", "Order"])
	elif cl=='MAG':
		eventData = '&brand=test&bvproduct=' + random.choice(BVPRODUCT) + '&cl=' + cl + '&type=' + random.choice(EVENTTYPE)
	SingleEvent = half1st + eventData + half2nd
	return SingleEvent


def getOldEvent(hostname):
	oldurl = 'http://' + hostname + '/t.gif?displaycode=0025-en_us&product=136085&client=ABC&cateogry=12345&contentuuid=550e8400-e29b-41d4-a716-446655440000&pagetype=Input&cb=1332342417564'
	return oldurl


def getHttpUrl(mode, host):
	set_new_cookies()	
	if mode == 'batch':
		addr = 'http://' + host + '/t.gif?tz=360&dc=test&bvid=' + BVID + '&bvsid=' + BVSID + '&client=' + random.choice(CLIENT) + '&batch='
		httpurl = addr + getBatchEvents()
		for j in range(random.randint(1,3)):
			httpurl = httpurl + ',' + getBatchEvents()
			print "URL:", httpurl
	if mode == 'single':
		addr = 'http://' + host + '/t.gif?tz=360&dc=test&client=' + random.choice(CLIENT)
		httpurl = addr + getSingleEvent()
	elif mode == 'old':
		httpurl = getOldEvent(host)
	return httpurl


def FireBees(args):
	global COOKIEMONSTER_DNS, LOGFILE, COMMANDLIST
	COOKIEMONSTER_DNS = args.host

	host = args.host
	total_events = args.totalevents
	bee_count = args.beecount
	mode = args.mode
	os.system('./bees down')
	os.system('./bees up -s '+ bee_count +' -g ssh -k Magpie ')
	
	logpath = str(datetime.now()).replace(' ', '-')
	logpath = '/tmp/' + logpath.replace(':','-')
	logpath = logpath.split('.')[0]
	print "\n Path of Log Files:", logpath

	LOGFILE = logpath
	os.mkdir(logpath)
	time.sleep(30)
	if args.eventtype == 'multiple':
		for i in range(int(bee_count)):
		    command = './bees attack -n '+ str(int(total_events)/int(bee_count)) +' -c 10 -u "'
		    httpurl = getHttpUrl(mode, host)
		    ecommand = command + httpurl + '" >> ' + logpath + '/Result.txt' + ' 2>&1'
		    COMMANDLIST.append(ecommand)
		#print "\n Command List in Multiple Mode", COMMANDLIST
	## Comments for nothing		

	if args.eventtype == 'single':
		command = './bees attack -n '+ total_events +' -c 10 -u "'
		httpurl_single = getHttpUrl(mode, host)
		ecommand = command + httpurl_single + '" >> ' + logpath + '/Result.txt' + ' 2>&1'
		COMMANDLIST.append(ecommand)
    	#print "\n Command List in Single Mode", COMMANDLIST
	FireEvents()
	
	
def FireEvents():
	global COMMANDLIST
	print "\n Command List: ", COMMANDLIST
	for req in COMMANDLIST:
		print "\n Bees Command \n", req
		subprocess.Popen([req], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		os.system(req)
		print " \n"
		time.sleep(5)
		continue
	os.system('./bees down')


def print_results():
	global LOGFILE
	total = 0
	os.system('cat '+ LOGFILE + "/Result.txt  | grep 'Requests per second' | awk '{print $4}' > " + LOGFILE + "/rps.txt")
	f1 = open( LOGFILE + '/rps.txt', 'r')
	f1data = f1.readlines()
	f1.close()
	for val in f1data:
		total = total + int(float(val))
		#print "value:", val
	#print "Total", total
	avg_number_requests = total/len(f1data)
	print "=================	Average Number of Requests per Second:", avg_number_requests
	
	rsptime = 0.00
	os.system('cat '+ LOGFILE + "/Result.txt  | grep '90% response time' | awk '{print $4}' > " + LOGFILE + "/rsp.txt")
	f2 = open(LOGFILE + '/rsp.txt' ,'r')
	f2data = f2.readlines()
	f2.close()
	for val in f2data:
		rsptime = rsptime + float(val)
	response_90th = rsptime/len(f2data)
	print "================		90% Response Time:", response_90th,  "[ms]"
	
	f2 = open(LOGFILE+'/Result.txt' , 'a')
	f2.write(' \n ===========	Average Number of Requests Per Second:' + str(avg_number_requests) + '\n')
	f2.write(' \n ===========	90th % Response Time:' + str(response_90th) + '\n')
	f2.close()

	rsptime = 0.00
	os.system('cat '+ LOGFILE + "/Result.txt  | grep '99% response time' | awk '{print $4}' > " + LOGFILE + "/rsp.txt")
	f3 = open(LOGFILE + '/rsp.txt' ,'r')
	f3data = f3.readlines()
	f3.close()
	for val in f3data:
		rsptime = rsptime + float(val)
	response_99th = rsptime/len(f3data)
	print "=================		99% Response Time:", response_99th,  "[ms]"

	f3 = open(LOGFILE+'/Result.txt' , 'a')
	f3.write('99th % Response Time:' + str(response_99th) + '\n')
	f3.close()


if __name__=="__main__":
	parser = argparse.ArgumentParser(description=__doc__, add_help=True, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-c', '--host', default='cookiemonster-staging.mag.bazaarvoice.com',  help='DNS Name of Cookiemosner / ELB.')
	parser.add_argument('-b', '--beecount',  default='4',				help='Number if Bees to be used.')
	parser.add_argument('-t', '--totalevents',      default='10000',	help='Total Number of events to be created')
	parser.add_argument('-e', '--eventtype',  default='multiple',		help='Only one type of Events or Multiple Types of events ex: single, multiple')
	parser.add_argument('-m', '--mode',  default='single',		help='Mode in which events are sent ex: single, batch, old')
	args = parser.parse_args()
 	FireBees(args)
 	print_results()
