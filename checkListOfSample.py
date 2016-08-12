
import os
import sys
import optparse
import re
import commands
import das_clientNew
import json
import pwd


def x509():
    "Helper function to get x509 either from env or tmp file"
    proxy = os.environ.get('X509_USER_PROXY', '')
    if  not proxy:
        proxy = '/tmp/x509up_u%s' % pwd.getpwuid( os.getuid() ).pw_uid
        if  not os.path.isfile(proxy):
            return ''
    return proxy

def check_glidein():
    "Check glideine environment and exit if it is set"
    glidein = os.environ.get('GLIDEIN_CMSSite', '')
    if  glidein:
        msg = "ERROR: das_client is running from GLIDEIN environment, it is prohibited"
        print(msg)
        sys.exit(EX__BASE)

def check_auth(key):
    "Check if user runs das_client with key/cert and warn users to switch"
    if  not key:
        msg  = "WARNING: das_client is running without user credentials/X509 proxy, create proxy via 'voms-proxy-init -voms cms -rfc'"
        print(msg)

check_glidein()
theKey=x509()
check_auth(theKey)

def checkHLTstatus(datasetName):
    theOutput=0
#    print datasetName
    jsondict = das_clientNew.get_data('https://cmsweb.cern.ch', "dataset dataset="+datasetName, 0, 0, False, 300, theKey, theKey)
    for anEntry in jsondict:
        if anEntry!="data":
            continue
        for dataset in jsondict[anEntry]:
            datasetfound=dataset["dataset"][0]["name"]
            if "reHLT" in datasetfound:
                theOutput=1
            if "withHLT"in datasetfound:
                theOutput=theOutput+2
    return theOutput




with open('samples20016.json') as f:
    json_data = json.load(f)

data = json_data["proc"]
for sampleType in data:
        for sub in sampleType:
            if not sub=="data":
                continue
            listSamples=[]
            for theSample in sampleType[sub]:
                theSampleTag =theSample["dtag"]
                theSampleName=theSample["dset"][0]
            #    if not "MC13TeV_DYJetsToLL_50toInf_2016" in theSampleTag:
            #        continue
                if "Run2016B" in theSampleName:
                    continue
                if "HLT" in theSampleName:
                    print theSampleTag+",1,0"
                    continue
                if (len(theSampleName)>0):
                    theDatasetName=re.split("/",theSampleName)[1]
                    theHLTstatus=checkHLTstatus("/"+theDatasetName+"/RunIISpring16*/MINIAODSIM")
                    print theSampleTag+",0,"+str(theHLTstatus)
