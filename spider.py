import urllib2
import json
import Queue
import threading
import time
import sys
import re
from getInfo import getInfo

total_url = "https://www.zocdoc.com"

threads = []
url_list = []

def GetDoctor(offset):
    url = "https://www.zocdoc.com/search/searchresults?HospitalId=-1&InsuranceId=-1&InsurancePlanId=-1&LanguageId=1&SpecialtyId=153&LimitToThisSpecialty=false&ExcludedSpecialtyIds=&PatientTypeChild=false&languageChanged=false&PlacemarkId=217701&DayFilter=AnyDay&TimeFilter=AnyTime&SortSelection=DefaultOrder&StartDate=null&ProcedureId=75&Offset="+str(offset)
    try:
        resp = urllib2.urlopen(url)
        strAns = resp.read()
        cnt = 0
        strJson = json.loads(strAns[8:])
        tmpp = strJson['model']['Doctors']
        print offset, len(tmpp)

        for i in range(len(tmpp)):
            doc_url = total_url + tmpp[i]['ProfReviewUrl']
            print doc_url
            url_list.append(doc_url)
            t = threading.Thread(target=getInfo, args=(doc_url,))
            t.start()
            # threads.append(t)
            doc_id = tmpp[i]['ProfId']
            doc_name = tmpp[i]['LongProfessionalName']
            doc_title = tmpp[i]['Title']
            doc_gender = tmpp[i]['Gender']
            doc_state = tmpp[i]['State']
            doc_spectialty = tmpp[i]['DisplaySpectialtyName']
            # print or store in db here
            cnt += 1
        if len(tmpp):
            return True
        else:
            return False
    except Exception, e:
        print e, str(offset) + '\n'
        return False

cnt_doctor = 100
threads = []

if __name__ =='__main__':
    for i in range(0, cnt_doctor, 10):
        if GetDoctor(i) == False:
            break
    #    t = threading.Thread(target=GetDoctor, args=(i,))
    #    threads.append(t)
    ##for t in threads:
    #    t.start()

    #t.join()


