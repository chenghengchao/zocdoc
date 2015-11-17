import urllib2
import json
import Queue
import threading
import time
from getInfo import getInfo

total_url = "https://www.zocdoc.com"

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
            getInfo(doc_url)
            doc_id = tmpp[i]['ProfId']
            doc_name = tmpp[i]['LongProfessionalName']
            doc_title = tmpp[i]['Title']
            doc_gender = tmpp[i]['Gender']
            doc_state = tmpp[i]['State']
            doc_spectialty = tmpp[i]['DisplaySpectialtyName']
            # print or store in db here
            cnt += 1
    except Exception, e:
        print e, str(offset) + '\n'

threads = []
cntt = 0
cnt_doctor = 100

if __name__ =='__main__':
    # f = open('tmp.txt', 'w+')
    for i in range(0, cnt_doctor, 10):
        GetDoctor(i)
        # t = threading.Thread(target=GetDoctor, args=(i, f))
        # threads.append(t)

    # for t in threads:
        #t.start()

    # t.join()


