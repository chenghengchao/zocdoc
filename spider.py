import urllib2
import urllib
import json
import Queue
import threading
import time
import sys
import re
import pycurl
import StringIO
import logging
import MySQLdb
# from getInfo import get_info

total_url = "https://www.zocdoc.com"
sql_list = Queue.Queue()
threads = []
url_list = []
Set = set()

def get_info(url, prof, conn):

    insurances = get_insurances(url.split('?')[0].split('-')[-1][0:-19])
    if insurances != False:
        try:
            resp = urllib2.urlopen(url, timeout=15)
            html = resp.read()
        except:
            return

        '''Profile is list of the name, suffix, sub Specilaty name'''
        Profile_pattern = re.compile(r'<h1 class="sg-h1 profile-doctor-name">[\s\S]*?</div>')
        Profile_res = Profile_pattern.findall(html)
        tmp = Profile_res[0].replace(' ','')
        res, num = re.compile(r'<[\s\S]*?>').subn('', tmp)
        L = res.split('\n');
        Profile = []
        Profile.append(L[1]); Profile.append(L[2]); Profile.append(L[-1]);
        # print Profile

        '''Doc_Rating is the rating of the doctor'''
        Doc_Rating_pattern = re.compile(r'<div class="sg-rating-big sg-rating-big-[\s\S]*?">')
        Doc_Rating_res = Doc_Rating_pattern.findall(html)
        Doc_Rating = Doc_Rating_res[0].split('<div class="sg-rating-big sg-rating-big-')[1].split('">')[0].replace('_', '.')
        # print Doc_Rating

        '''Practice_name is the list of Practice name'''
        Practice_name_pattern = re.compile(r'<h3>Practice Name</h3>[\s\S]*?</ul>')
        Practice_name_res = Practice_name_pattern.findall(html)
        L = Practice_name_res[0].replace('\t', '').replace('\r', '')
        res, num = re.compile(r'<[\s\S]*?>').subn('', L)
        Practice_name = []
        for p in res.split('\n'):
            if p != '' and p != 'Practice Name' : Practice_name.append(p)
        # print Practice_name

        '''Badges is the Badges of the doctor'''
        Badges_pattern = re.compile(r'<div class="badge[\s\S]*?data-description')
        Badges_res = Badges_pattern.findall(html)
        Badges = []
        for m in Badges_res:
            Badges.append(m.split('title="')[1].split('"')[0])
        # print Badges

        Qual_pattern = re.compile(r'<h3>(Education|Languages Spoken|Board Certifications|Specialties)(</h3>[\s\S]*?</div>)')
        Qualificaton_res = Qual_pattern.findall(html)

        # Qualificaton list of tuple of (qualification, item_list)
        Qualificaton = []
        for m in Qualificaton_res:
            k = m[1].replace('\t', '')
            res, num = re.compile(r'<[\s\S]*?>').subn('', k)
            L = ('\r\n' + res).split('\r\n\r\n\r\n')
            last = -1
            if L[-2] == 'Less...':
                last = -3
            Qualificaton.append((m[0], L[1:last]))
        # print Qualificaton

        # Statement is the Professional Statement of the doctor
        State_pattern = re.compile(r'<p itemprop="description">[\s\S]*?</p>')
        Statement_res = State_pattern.findall(html)
        Statement = ''
        try:
            Statement = Statement_res[0].split('<p itemprop="description">\r\n        ')[1].split('\r\n        \t</p>')[0].replace('<br/>', '')
            if Statement.find('span') != -1:
                Statement = Statement.split('</span>')[0].replace('<span class="-hidden  hide">', '').replace('                    ', '')
        except IndexError:
            Statement = ''
        Statement = Statement.replace('"', r"\"")
        Statement = Statement.replace("'", r'\'')
        # print Statement

        # Review is the list of tuple4 of date, author, rating and comment
        Review = []
        Review_pattern = re.compile(r'<div class="whenWho sg-h3">[\s\S]*?<div class="reviewsMain clearfix"')
        Review_res = Review_pattern.findall(html)
        for m in Review_res:
            date = ''
            author = ''
            tmp = m.split('>')[2].split('</span')[0]
            if tmp[0:2] != 'by':
                date = tmp
                author = m.split('>')[4].split('</span')[0]
            else:
                author = tmp;
            # rating is the tuple of label and the rating value of this review
            rating = []
            rating_list = m.split('<div class="stars">')[1:]
            for r in rating_list:
                score = r.split('<div class="sg-rating sg-rating-')[1][0:3].replace('_', '.')
                name = r.split('<div class="explanation sg-h4">\n')[1].split('</div>')[0].strip()
                rating.append((name, score))

            comment = m.split('<p class="review-body"')[1].split('>')[1].split('</p')[0].strip()
            Review.append((date, author, rating, comment))
        # print review

        sql = 'insert into doctor values(' + str(prof['ProfId']) \
                                           + ',"' + prof['LongProfessionalName'] \
                                           + '","' + prof['Gender'] \
                                           + '","' + prof['City'] \
                                           + '","' + Doc_Rating \
                                           + '","' + prof['Address1'] \
                                           + '","' + prof['Address2'] \
                                           + '","' + Practice_name[0] \
                                           + '","' + prof['MainSpecialtyName'] \
                                           + '","' + Profile[2] \
                                           + '","' + prof['Title'] \
                                           + '","' + Statement \
                                           + '");'
        # print sql
        sql_list.put(sql)
        cur = conn.cursor()
        try:
            cur.execute(sql)
            print str(prof['ProfId']) + 'success'
        except Exception,e:
            print Statement
            print str(prof['ProfId']), e

        conn.commit()
        # print 'here ' + url + ' ' + prof + '\n'

def get_insurances(id):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    url = 'https://www.zocdoc.com/insuranceinformation/ProfessionalInsurances?id=' + id
    try:
        resp = urllib2.urlopen(url, timeout=15).read()
        data = json.loads(resp[8:])['Carriers']
        Insurances = []
        for d in data:
            name = d['Name']
            plans = d['Plans']
            item_list = []
            for p in plans:
                item_list.append(p['Name'])
            Insurances.append((name, item_list))
        return Insurances
    except Exception, e:
        print 'error in get_surances( ' + str(id) + ' )', e
        return False

def GetDoctor(offset, speciality, conn):
    params = {"HospitalId": -1,
            "InsuranceId":-1,
            "InsurancePlanId":-1,
            "SpecialtyId": speciality,
            "LimitToThisSpecialty": "true",
            "ExcludedSpecialtyIds":"",
            "PatientTypeChild":"false",
            "languageChanged":"false",
            "PlacemarkId":"",
            "DayFilter":"AnyDay",
            "TimeFilter":"AnyTime",
            "SortSelection":"DefaultOrder",
            "StartDate":"null",
            "ProcedureId":75,
            "Offset":offset}

    data = urllib.urlencode(params)

    url = "https://www.zocdoc.com/search/searchresults?" + data
    try:
        resp = urllib.urlopen(url)
        strAns = resp.read()
        cnt = 0
        strJson = json.loads(strAns[8:])
        tmpp = strJson['model']['Doctors']
        # print speciality, offset, len(tmpp)

        for i in range(len(tmpp)):
            doc_url = total_url + tmpp[i]['ProfReviewUrl']
            url_list.append(doc_url)
            t = threading.Thread(target=get_info, args=(doc_url, tmpp[i], conn))
            t.start()
            threads.append(t)
            doc_id = tmpp[i]['ProfId']
            Set.add(doc_id)
            doc_name = tmpp[i]['LongProfessionalName']
            doc_title = tmpp[i]['Title']
            doc_gender = tmpp[i]['Gender']
            doc_state = tmpp[i]['State']
            doc_spectialty = tmpp[i]['DisplaySpectialtyName']
            # print doc_url + doc_spectialty + doc_state
            # print or store in db here
            cnt += 1
        if len(tmpp) == 10:
            return True
        else:
            return False
    except Exception, e:
        return True

cnt_doctor = 10

start = time.time()
specialty = []
if __name__ =='__main__':

    try:
        conn =  MySQLdb.connect(host="localhost", user="root",
                passwd="yyjmac", db="test", port=3306)
        cur = conn.cursor()
        # cur.execute("select * from test")
        # results = cur.fetchmany(100)
        # for res in results:
        #     print res
    except MySQLdb.Error, e:
        print 'Connect to mysql error'
        exit(0)

    GetDoctor(0, 98, conn)

    for th in threads:
        th.join()

    # try:
    #     cur.execute("select * from test")
    #     results = cur.fetchall()
    #     for res in results:
    #         print res
    # except Exception,e:
    #     print e

    cur.close()
    conn.close()
    # while sql_list.empty() == False:
    #    print sql_list.get()
    # f_object = open('specialty.txt', 'r')

    # for line in f_object:
    #    line_1 = line.split(',')
    #    specialty.append(line_1[0][1:])
    # f_object.close()

    # for spe_id in specialty:
    #     for offset in range(0, cnt_doctor, 10):
    #         if GetDoctor(offset, spe_id, cur) == False:
    #             break

    # for th in threads:
    #     th.join()

    print time.time() - start
