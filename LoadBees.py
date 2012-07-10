#!/usr/bin/python

"""
@Suneel Vana: This is the latest working version
Script to geneate load testing data for Magpie.

HOW TO RUN:
-----------
./LoadMagpie.py <ELB HostName/Cookiemonster Host Name> <Number of Bee Instances> <Total Number of requests>
Example: ./LoadMagpie-Parallel.py cookiemonster-staging-1330424627.us-east-1.elb.amazonaws.com 2 10
"""

import random
import os, sys, time
import datetime
import subprocess
import requests
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

CLIENT = ["ABC", "GOOG", "MAG227", "MAG339", "MAG341"]
MODE = ["old", "single" , "batch"]
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
    URL = 'http://' + COOKIEMONSTER_DNS + '/t.gif?client=COOKIE&type=COOKIE&dc=test&cl=SCI'
    ##print "URL:", URL
    response = requests.get(URL)
    global BVID
    BVID = response.cookies['BVSID']
    global BVSID
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


def LoadEvents(host, count, total, mode='single'):
    global COOKIEMONSTER_DNS, LOGFILE
    COOKIEMONSTER_DNS = host
    os.system('./bees down')
    os.system('./bees up -s '+ count +' -g ssh -k Magpie ')
    logpath = str(datetime.now()).replace(' ', '-')
    logpath = '/tmp/' + logpath.replace(':','-')
    logpath = logpath.split('.')[0]
    print "\n Path of Log Files:", logpath
    LOGFILE = logpath
    os.mkdir(logpath)
    time.sleep(50)

    for i in range(int(count)):
        if i % 5 == 0:
            set_new_cookies()
        command = './bees attack -n '+ total +' -c 10 -u "'
        ##command = './bees attack -n '+ total +' -c ' + str(int(total)/10) + ' -u "'
        if mode == 'batch':
            addr = 'http://' + host + '/t.gif?tz=360&dc=test&bvid=' + BVID + '&bvsid=' + BVSID + '&client=' + random.choice(CLIENT) + '&batch='
            httpurl = addr + getBatchEvents()
            for i in range(random.randint(1,3)):
                httpurl = httpurl + ',' + getBatchEvents()
                #print "\n ITERATION: ", i+1
                #print "\n COMPLETE URL in BATCH MODE: \n"
                print "URL:", httpurl
        elif mode == 'single':  
            addr = 'http://' + host + '/t.gif?tz=360&dc=test&client=' + random.choice(CLIENT)
            httpurl = addr + getSingleEvent()
            print "\n ITERATION:", i+1
            print "\n COMPLETEURL IN SINGLE MODEE: \n", 
            print httpurl
        elif mode == 'old':
            httpurl = getOldEvent(host)
        ecommand = command + httpurl + '" >> ' + logpath + '/Result.txt' + ' 2>&1'
        #	print "Flushing DNS Cahce:", os.system('sudo dscacheutil -flushcache')
        COMMANDLIST.append(ecommand)
        print COMMANDLIST

    for req in COMMANDLIST:
        print " Bees Command \n", req
        subprocess.Popen([req], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system(req)
        time.sleep(5)
        continue
    os.system('./bees down')


def print_results():
	global LOGFILE
	total = 0
	os.system('cat '+ LOGFILE + "/Result.txt  | grep 'Requests per second' | awk '{print $4}' > " + LOGFILE + "/rps.txt")
	f1 = open('/tmp/rps.txt', 'r')
	f1data = f1.readlines()
	f1.close()
	for val in f1data:
		total = total + int(float(val))
		#print "value:", val
	#print "Total", total
	avg_number_requests = total/len(f1data)
	print "Average Number of Requests per Second:", avg_number_requests
	
	rsptime = 0.00
	os.system('cat '+ LOGFILE + "/Result.txt  | grep '90% response time' | awk '{print $4}' > " + LOGFILE + "/rsp.txt")
	f2 = open(LOGFILE + '/rsp.txt' ,'r')
	f2data = f2.readlines()
	f2.close()
	for val in f2data:
		rsptime = rsptime + float(val)
	response_90th = rsptime/len(f2data)
	print "90% Response Time:", response_90th
	
	f2 = open(LOGFILE+'/Result.txt' , 'a')
	f2.write('Average Number of Requests Per Second:' + str(avg_number_requests) + '\n')
	f2.write('90th % Response Time:' + str(response_90th) + '\n')
	f2.close()

	rsptime = 0.00
	os.system('cat '+ LOGFILE + "/Result.txt  | grep '99% response time' | awk '{print $4}' > " + LOGFILE + "/rsp.txt")
	f3 = open(LOGFILE + '/rsp.txt' ,'r')
	f3data = f3.readlines()
	f3.close()
	for val in f3data:
		rsptime = rsptime + float(val)
	response_99th = rsptime/len(f3data)
	print "99% Response Time:", response_99th

	f3 = open(LOGFILE+'/Result.txt' , 'a')
	f3.write('99th % Response Time:' + str(response_99th) + '\n')
	f3.close()


if __name__=="__main__":
    if len(sys.argv)<4:
        print "\n"
        print "Please provide all input parameters. <CookieMonster HostName> <# of Micro Instances> <Total Number of Requests>"
        print "Ex: ./LoadMagpie-parallel.py cookiemonster-staging-1330424627.us-east-1.elb.amazonaws.com 4 100"
        print "\n"
        exit(0)
    LoadEvents(sys.argv[1], sys.argv[2], sys.argv[3])
    print_results()
