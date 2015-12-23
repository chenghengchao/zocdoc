import urllib2
import urllib
import json
import ConfigParser
import Queue
import threading
import time
import sys
import re
import os
import string
import logging
import MySQLdb

total_url = "https://www.zocdoc.com"
lock = threading.Lock()
Set = set()

def get_badges(html, prof, cur, conn):
    Badges_pattern = re.compile(r'<div class="badge[\s\S]*?data-description')
    Badges_res = Badges_pattern.findall(html)
    Badges = []
    for m in Badges_res:
        Badges.append(m.split('title="')[1].split('"')[0])

    if len(Badges) != 0:
        for badges in Badges:
            sql = 'select badges_id from badges where badges_name=\"' + badges + '\"'
            try:
                cur.execute(sql)
                results = cur.fetchall()
            except Exception, e:
                logging.error('failed to get badge\'s id' + str(e))

            if len(results) == 0:
                sql = 'insert into badges(badges_name) values(\"' + badges + '\")'
                try:
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('Success to update badges with ' + badges)
                except Exception, e:
                    logging.error('failed to insert new badges to badges' + str(e))

            sql = 'select badges_id from badges where badges_name=\"' + badges + '\"'
            try:
                cur.execute(sql)
                results = cur.fetchall()
            except Exception, e:
                logging.error('Failed to get badge\'s id 2' + str(e))
            badges_id = results[0][0]
            sql = 'insert into badges_doc values( ' + str(prof['ProfId']) + ',' + str(badges_id) + ')'
            try:
                cur.execute(sql)
                conn.commit()
                # logging.info('Success to insert into badges_doc ' + str(prof['ProfId']) + ' ' + str(badges_id))
            except Exception, e:
                logging.error('Failed to insert into badges_doc ' + str(e))

def get_info_offline(url, prof, conn):

    global lock
    #getInsurances(url.split('?')[0].split('-')[-1])
    # logging.info('Start to get info offline ' + url)
    try:
        html = urllib2.urlopen(url, timeout = 15).read()
    except Exception, e:
        logging.error('Error to get info offline ' + str(e) + ' url = ' + url)
        return

    Profile_pattern = re.compile(r'<span class="docLongName[\s\S]*?</div>')
    Profile_res = Profile_pattern.findall(html)
    tmp = Profile_res[0].split('</span>')
    name = tmp[0].split('>')[1]
    suffix = tmp[1].split('>')[1]
    profSpecTitle = tmp[2].split('</div>')[0].split('>')[-1]

    Practice_name_pattern = re.compile(r'<span itemprop="branchOf" data-test="practice-name">[\s\S]*?</span>')
    Practice_name_res = Practice_name_pattern.findall(html)
    Practice_name = Practice_name_res[0].split('>')[1].split('<')[0]

    Qual_pattern = re.compile(r'<h3>(Education|Language Spoken|Board Certifications|Specialties)(</h3>[\s\S]*?</div>)')
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

    lock.acquire()
    cur = conn.cursor()
    sql = 'insert into doctor values(' + str(prof['ProfId']) \
                    + ',"' + prof['LongProfessionalName'] \
                    + '","' + prof['Gender'] \
                    + '","' + prof['State'] \
                    + '","' + prof['City'] \
                    + '","' + 'null' \
                    + '","' + prof['Address1'] \
                    + '","' + prof['Address2'] \
                    + '","' + Practice_name \
                    + '","' + prof['MainSpecialtyName'] \
                    + '","' + profSpecTitle \
                    + '","' + prof['Title'] \
                    + '","' + '' \
                    + '");'

    cur = conn.cursor()
    try:
        # logging.info('Prepare to insert doc ' + str(prof['ProfId']) + ' profile to db')
        cur.execute(sql)
        Set.add(prof['ProfId'])
        # logging.info(str(prof['ProfId']) + ' has been stored successfully')
        conn.commit()
    except Exception,e:
        logging.error(str(prof['ProfId']) + ' fail to store' + str(e) + url)
        cur.close()
        lock.release()
        return

    get_badges(html, prof, cur, conn)

    for qua in Qualificaton:
        if qua[0] == 'Education':
            for edu in qua[1]:
                sql = 'select edu_id from education where edu_name=\"' + edu + '\"'
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    if len(results) == 0:
                        # logging.info(edu + ' not in table education, start to insert')
                        sql = 'insert into education(edu_name) values(\"' + edu + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info(edu + ' has been inserted into education successfully')
                    sql = 'select edu_id from education where edu_name=\"' + edu + '\"'
                    cur.execute(sql)
                    results = cur.fetchall()
                    for res in results:
                        edu_id = res[0]

                    sql = 'insert into education_doc values(\"' + str(edu_id) +'\",\"' + \
                            str(prof['ProfId']) + '\")'
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('success to insert education of doctor ' + str(prof['ProfId']))
                except Exception, e:
                    logging.error('err to insert education of doctor ' + str(prof['ProfId']) + str(e))
        elif qua[0] == 'Languages Spoken':
            for lang in qua[1]:
                sql = 'select lang_id from language where lang_name=\"' + lang + '\"'
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    if len(results) == 0:
                        # logging.info(lang + ' not in table language, start to insert')
                        sql = 'insert into language(lang_name) values(\"' + lang + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info(lang + ' has been inserted into language successfully')
                    sql = 'select lang_id from language where lang_name = \"' + lang + '\"'
                    cur.execute(sql)
                    results = cur.fetchall()
                    for res in results:
                        lang_id = res[0]

                    sql = 'insert into language_doc values(\"' + str(lang_id) + '\",\"' + \
                            str(prof['ProfId']) + '\")'
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('success to insert language of doctor ' + str(prof['ProfId']))
                except Exception, e:
                    logging.error('err to insert language of doctor ' + str(prof['ProfId']) + str(e))
        elif qua[0] == 'Specialties':
            for spec in qua[1]:
                sql = 'select spec_id from specialty where spec_name=\"' + spec + '\"'
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    if len(results) == 0:
                        # logging.info(spec + ' not in table specialty, start to insert')
                        sql = 'insert into specialty(spec_name) values(\"' + spec + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info(spec + ' has been inserted into specialty successfully')
                    sql = 'select spec_id from specialty where spec_name = \"' + spec + '\"'
                    cur.execute(sql)
                    results = cur.fetchall()
                    for res in results:
                        spec_id = res[0]

                    sql = 'insert into specialty_doc(spec_id, doc_id) values(' + str(spec_id) + ',' + \
                            str(prof['ProfId']) + ')'
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('success to insert specialty of doctor ' + str(prof['ProfId']))
                except Exception, e:
                    logging.error('err to insert specialty of doctor ' + str(prof['ProfId']) + str(e))
        elif qua[0] == 'Board Certifications':
            for cer in qua[1]:
                sql = 'select cer_id from certification where cer_name=\"' + cer + '\"'
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    if len(results) == 0:
                        # logging.info(cer + ' not in table certification, start to insert')
                        sql = 'insert into certification(cer_name) values(\"' + cer + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info(cer + ' has been inserted into certification successfully')
                    sql = 'select cer_id from certification where cer_name = \"' + cer + '\"'
                    cur.execute(sql)
                    results = cur.fetchall()
                    for res in results:
                        cer_id = res[0]

                    sql = 'insert into certification_doc(cer_id, doc_id) values(' + str(cer_id) + ',' + \
                            str(prof['ProfId']) + ')'
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('success to insert certification of doctor ' + str(prof['ProfId']))
                except Exception, e:
                    logging.error('err to insert certification of doctor ' + str(prof['ProfId']) + str(e))
        else:
            pass

    cur.close()

    lock.release()

def get_info(url, prof, conn):

    global lock
    logging.info('start to getinfo ' + str(url))
    if  (url.split('?')[0].split('-')[-1][0:-19]).isdigit() == False:
        get_info_offline(url, prof, conn)
        return
    logging.info('Start to get info: ' + url)
    insurances = get_insurances(prof['ProfId'])
    # insurances = get_insurances(url.split('?')[0].split('-')[-1][0:-19])
    if insurances != False:
        try:
            resp = urllib2.urlopen(url, timeout=15)
            html = resp.read()
        except:
            return

        '''Profile is list of the name, suffix, sub Specilaty name'''
        Profile_pattern = re.compile(r'<h1 class="sg-h1 profile-doctor-name">[\s\S]*?</div>')
        Profile_res = Profile_pattern.findall(html)
        Profile = []
        if len(Profile_res) != 0:
            tmp = Profile_res[0].replace(' ','')
            res, num = re.compile(r'<[\s\S]*?>').subn('', tmp)
            L = res.split('\n');
            Profile.append(L[1]); Profile.append(L[2]); Profile.append(L[-1]);
        # print Profile

        '''Doc_Rating is the rating of the doctor'''
        Doc_Rating_pattern = re.compile(r'<div class="sg-rating-big sg-rating-big-[\s\S]*?">')
        Doc_Rating_res = Doc_Rating_pattern.findall(html)
        Doc_Rating = ''
        try:
            Doc_Rating = Doc_Rating_res[0].split('<div class="sg-rating-big sg-rating-big-')[1].split('">')[0].replace('_', '.')
        except:
            pass
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
        # Badges_pattern = re.compile(r'<div class="badge[\s\S]*?data-description')
        # Badges_res = Badges_pattern.findall(html)
        # Badges = []
        # for m in Badges_res:
        #     Badges.append(m.split('title="')[1].split('"')[0])
        # # print Badges

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
            rating = {}
            rating_list = m.split('<div class="stars">')[1:]
            for r in rating_list:
                score = r.split('<div class="sg-rating sg-rating-')[1][0:3].replace('_', '.')
                name = r.split('<div class="explanation sg-h4">\n')[1].split('</div>')[0].strip()
                rating[name] = score

            comment = m.split('<p class="review-body"')[1].split('>')[1].split('</p')[0].strip()
            Review.append((date, author, rating, comment))
        # print review

        lock.acquire()

        logging.info('Start to insert ' + str(prof['ProfId']) + ' to db')
        sql = 'insert into doctor values(' + str(prof['ProfId']) \
                + ',"' + prof['LongProfessionalName'] \
                + '","' + prof['Gender'] \
                + '","' + prof['State'] \
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
        cur = conn.cursor()
        try:
            # logging.info('Prepare to insert doc ' + str(prof['ProfId']) + ' profile to db')
            cur.execute(sql)
            Set.add(prof['ProfId'])
            # logging.info(str(prof['ProfId']) + ' has been stored successfully')
        except Exception,e:
            logging.error(str(prof['ProfId']) + ' fail to store' + str(e) + url)
            cur.close()
            lock.release()
            return

        conn.commit()

        get_badges(html, prof, cur, conn)

        if len(Review) !=0:
            for review in Review:
                date = review[0]
                author = review[1][3:]
                comment = review[3]
                rating = review[2]
                overall_rating = rating.get('Overall Rating', '')
                bedside_rating = rating.get('Bedside Manner', '')
                wait_time = rating.get('Wait Time', '')
                sql = 'insert into comment(doc_id, comm_time, comm_author,\
                        overall_rating, bedside_rating, wait_time, content) \
                        values(\"' + str(prof['ProfId']) + \
                        '\",\"' + date + '\",\"' + \
                        author + '\",\"' + overall_rating + '\",\"' + bedside_rating + '\",\"' + \
                        wait_time + '\",\"' +  comment + '\")'

                try:
                    cur.execute(sql)
                    conn.commit()
                    # logging.info('insert into comment success ' + str(prof['ProfId']))
                except Exception, e:
                    logging.error('insert into comment error ' + str(prof['ProfId']) + str(e))

        for qua in Qualificaton:
            if qua[0] == 'Education':
                for edu in qua[1]:
                    sql = 'select edu_id from education where edu_name=\"' + edu + '\"'
                    try:
                        cur.execute(sql)
                        results = cur.fetchall()
                        if len(results) == 0:
                            # logging.info(edu + ' not in table education, start to insert')
                            sql = 'insert into education(edu_name) values(\"' + edu + '\")'
                            cur.execute(sql)
                            conn.commit()
                            # logging.info(edu + ' has been inserted into education successfully')
                        sql = 'select edu_id from education where edu_name=\"' + edu + '\"'
                        cur.execute(sql)
                        results = cur.fetchall()
                        for res in results:
                            edu_id = res[0]

                        sql = 'insert into education_doc values(\"' + str(edu_id) +'\",\"' + \
                                str(prof['ProfId']) + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info('success to insert education of doctor ' + str(prof['ProfId']))
                    except Exception, e:
                        logging.error('err to insert education of doctor ' + str(prof['ProfId']) + str(e))
            elif qua[0] == 'Languages Spoken':
                for lang in qua[1]:
                    sql = 'select lang_id from language where lang_name=\"' + lang + '\"'
                    try:
                        cur.execute(sql)
                        results = cur.fetchall()
                        if len(results) == 0:
                            # logging.info(lang + ' not in table language, start to insert')
                            sql = 'insert into language(lang_name) values(\"' + lang + '\")'
                            cur.execute(sql)
                            conn.commit()
                            # logging.info(lang + ' has been inserted into language successfully')
                        sql = 'select lang_id from language where lang_name = \"' + lang + '\"'
                        cur.execute(sql)
                        results = cur.fetchall()
                        for res in results:
                            lang_id = res[0]

                        sql = 'insert into language_doc values(\"' + str(lang_id) + '\",\"' + \
                                str(prof['ProfId']) + '\")'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info('success to insert language of doctor ' + str(prof['ProfId']))
                    except Exception, e:
                        logging.error('err to insert language of doctor ' + str(prof['ProfId']) + str(e))
            elif qua[0] == 'Specialties':
                for spec in qua[1]:
                    sql = 'select spec_id from specialty where spec_name=\"' + spec + '\"'
                    try:
                        cur.execute(sql)
                        results = cur.fetchall()
                        if len(results) == 0:
                            # logging.info(spec + ' not in table specialty, start to insert')
                            sql = 'insert into specialty(spec_name) values(\"' + spec + '\")'
                            cur.execute(sql)
                            conn.commit()
                            # logging.info(spec + ' has been inserted into specialty successfully')
                        sql = 'select spec_id from specialty where spec_name = \"' + spec + '\"'
                        cur.execute(sql)
                        results = cur.fetchall()
                        for res in results:
                            spec_id = res[0]

                        sql = 'insert into specialty_doc(spec_id, doc_id) values(' + str(spec_id) + ',' + \
                                str(prof['ProfId']) + ')'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info('success to insert specialty of doctor ' + str(prof['ProfId']))
                    except Exception, e:
                        logging.error('err to insert specialty of doctor ' + str(prof['ProfId']) + str(e))
            elif qua[0] == 'Board Certifications':
                for cer in qua[1]:
                    sql = 'select cer_id from certification where cer_name=\"' + cer + '\"'
                    try:
                        cur.execute(sql)
                        results = cur.fetchall()
                        if len(results) == 0:
                            # logging.info(cer + ' not in table certification, start to insert')
                            sql = 'insert into certification(cer_name) values(\"' + cer + '\")'
                            cur.execute(sql)
                            conn.commit()
                            # logging.info(cer + ' has been inserted into certification successfully')
                        sql = 'select cer_id from certification where cer_name = \"' + cer + '\"'
                        cur.execute(sql)
                        results = cur.fetchall()
                        for res in results:
                            cer_id = res[0]

                        sql = 'insert into certification_doc(cer_id, doc_id) values(' + str(cer_id) + ',' + \
                                str(prof['ProfId']) + ')'
                        cur.execute(sql)
                        conn.commit()
                        # logging.info('success to insert certification of doctor ' + str(prof['ProfId']))
                    except Exception, e:
                        logging.error('err to insert certification of doctor ' + str(prof['ProfId']) + str(e))
            else:
                pass


        for insurance in insurances:
            insu = insurance[0]
            if len(insu) == 0:
                continue
            sql = 'select insu_id from insurance where insu_name=\"' + insu + '\"'
            try:
                cur.execute(sql)
                results = cur.fetchall()
                if len(results) == 0:
                    # logging.info(insu + ' not in table insurance, start to insert')
                    sql = 'insert into insurance(insu_name) values(\"' + insu + '\")'
                    cur.execute(sql)
                    conn.commit()
                    # logging.info(insu + ' has been inserted into insurance successfully')
                sql = 'select insu_id from insurance where insu_name = \"' + insu + '\"'
                cur.execute(sql)
                results = cur.fetchall()
                for res in results:
                    insu_id = res[0]

                sql = 'insert into insurance_doc(insu_id, doc_id) values(' + str(insu_id) + ',' + \
                        str(prof['ProfId']) + ')'
                cur.execute(sql)
                conn.commit()
                # logging.info('success to insert insurance of doctor ' + str(prof['ProfId']))
            except Exception, e:
                logging.error('err to insert insurance of doctor ' + str(prof['ProfId']) + str(e))

        cur.close()
        lock.release()

def get_insurances(id):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    url = 'https://www.zocdoc.com/insuranceinformation/ProfessionalInsurances?id=' + str(id)
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
        logging.error('error in get_surances( ' + str(id) + ' )' + str(e))
        return False

def get_doctor(offset, speciality, city, conn):
    logging.info('Get ' + city + '  ' + str(speciality) + ' ' + str(offset))
    params = {
            "HospitalId": -1,
            "Address": city,
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
        resp = urllib2.urlopen(url, timeout=5)
        strAns = resp.read()
        cnt = 0
        strJson = json.loads(strAns[8:])
        has = strJson['model']['NoResultsHeader']
        tmpp = strJson['model']['Doctors']

        threads = []
        for i in range(len(tmpp)):
            doc_url = total_url + tmpp[i]['ProfReviewUrl']
            tmpp[i]['ProfId'] = tmpp[i]['Identifier']['Id']
            doc_id = tmpp[i]['ProfId']
            if doc_id in Set:
                # logging.info(str(doc_id) + ' has already in db')
                continue
            t = threading.Thread(target=get_info, args=(doc_url, tmpp[i], conn))
            t.start()
            threads.append(t)
            # print doc_url + doc_spectialty + doc_state
            # print or store in db here
            cnt += 1
        if len(tmpp) == 10:
            return True
        else:
            return False
        for thread in threads:
            thread.join()
    except Exception, e:
        logging.error('exception has found in doctor\'s list' + str(e))
        return True

# the sys can only crawl 100 doctors per query url
cnt_doctor = 100

start = time.time()
specialty = []

def main():
    # initialize logging module
    logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt = '%a, %d %b %Y %H:%M:%S',
                    filename='zocdoc.log',
                    filemode='a')


    # read config file from "db.conf"
    try:
        cf = ConfigParser.ConfigParser()
        cf.read('db.conf')

        db_host = cf.get('db', 'db_host')
        db_port = cf.get('db', 'db_port')
        db_user = cf.get('db', 'db_user')
        db_pass = cf.get('db', 'db_pass')
        db_name = cf.get('db', 'db_name')
        logging.info("Success to get db's config")
    except Exception, e:
        logging.error("Fail to get db's config, " + str(e))
        exit(0)


    # try to connect to mysql
    try:
        conn =  MySQLdb.connect(host=db_host, user=db_user,
                passwd=db_pass, db=db_name, port=int(db_port))
        conn.set_character_set('utf8')
        cur = conn.cursor()
        set_inter_timeout = 'set interactive_timeout = 24*3600'
        cur.execute(set_inter_timeout)
        set_wait_timeout = 'set wait_timeout = 24*3600'
        cur.execute(set_wait_timeout)
        set_character = 'set names utf8'
        cur.execute(set_character)
        set_character = 'set character set utf8'
        cur.execute(set_character)
        set_character = 'set character_set_connection=utf8'
        cur.execute(set_character)
        logging.info('Connect to mysql success')
    except MySQLdb.Error, e:
        logging.error('Connect to mysql error' + str(e))
        exit(0)

    # try to get all doc_id in db, then store them to "Set"
    try:
        cur.execute('select doc_id from doctor')
        results = cur.fetchall()
        for res in results:
            # logging.info(str(res[0]) + ' in db')
            Set.add(res[0])
        logging.info("success to load doc_id from db")
    except:
        logging.error("error to load doc_id from db")


    # both of thesse two are useful to construct the query url
    # specialty.txt has stored all the specialties
    f_object = open('specialty.txt', 'r')
    # city.txt has stored all the cities
    f_city = open('city.txt', 'r')

    for line in f_object:
       line_1 = line.split(',')
       specialty.append(line_1[0][1:])

    f_object.close()

    # start to crawl data city & specialty based
    for city in f_city:
        city = city.strip()
        for spe_id in specialty:
            for offset in range(0, cnt_doctor, 10):
                get_doctor(offset, spe_id, city, conn)
                get_doctor(cnt_doctor - offset - 10, spe_id, city, conn)

    f_city.close()

    # close all the connect
    cur.close()
    conn.close()
    logging.info('Close connect to mysql success')
    logging.info('\n\n\n\n\n\n')

    # print the the total run time
    print time.time() - start

if __name__ =='__main__':
    while True:
        main()
        time.sleep(4 * 60 * 60)
