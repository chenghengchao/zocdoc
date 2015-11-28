import Queue
import threading
import urllib2
import time
import json
from getInfo import get_info

hosts = 'http://www.zocdoc.com/'
offset_queue = Queue.Queue()
doc_queue = Queue.Queue()

class ThreadDoctor(threading.Thread):
    def __init__(self, offset_queue, doc_queue):
        threading.Thread.__init__(self)
        self.offset_queue = offset_queue
        self.doc_queue = doc_queue

    def run(self):
        while True:
            host = self.offset_queue.get()
            url = urllib2.urlopen(host)
            the_page = url.read()
            try:
                strjson = json.loads(the_page[8:])
                tmpp = strjson['model']['Doctors']
                for i in range(len(tmpp)):
                    print tmpp[i]['ProfReviewUrl']
                    self.doc_queue.put(hosts + tmpp[i]['ProfReviewUrl'])
            except Exception, e:
                print 'error',e
            print 'offset_queue', self.offset_queue.qsize()
            self.offset_queue.task_done()

class ThreadInfo(threading.Thread):
    def __init__(self, doc_queue, out_file):
        threading.Thread.__init__(self)
        self.doc_queue = doc_queue
        self.out_file = out_file

    def run(self):
        while True:
            url = self.doc_queue.get()
            print url+'\n'
            get_info(url, self.out_file)
            print self.doc_queue.qsize()
            self.doc_queue.task_done()

start = time.time()
if __name__ == '__main__':
    for i in range(5):
        t = ThreadDoctor(offset_queue, doc_queue)
        t.setDaemon(True)
        t.start()

    for offset in range(0, 20, 10):
        url = 'https://www.zocdoc.com/search/searchresults?HospitalId=-1&InsuranceId=-1&InsurancePlanId=-1&LanguageId=1&SpecialtyId=153&LimitToThisSpecialty=false&ExcludedSpecialtyIds=&PatientTypeChild=false&languageChanged=false&PlacemarkId=217701&DayFilter=AnyDay&TimeFilter=AnyTime&SortSelection=DefaultOrder&StartDate=null&ProcedureId=75&Offset='+str(offset)
        offset_queue.put(url)

    f = open('tmp.txt', 'w+')
    for i in range(10):
        t = ThreadInfo(doc_queue, f)
        t.setDaemon(True)
        t.start()

    offset_queue.join()
    doc_queue.join()
    print time.time() - start
