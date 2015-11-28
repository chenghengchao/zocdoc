# coding=utf-8
import re
import sys
import json
import urllib2


def get_info(url, prof, conn):

   # print 'here ' + url
    if get_insurances(url.split('?')[0].split('-')[-1]):
        try:
            resp = urllib2.urlopen(url, timeout=15)
            html = resp.read()
        except:
            return

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
        # print Statement

'''Badges is the Badges of the doctor'''
    Badges_pattern = re.compile(r'<div class="badge[\s\S]*?data-description')
    Badges_res = Badges_pattern.findall(html)
    Badges = []
    for m in Badges_res:
        Badges.append(m.split('title="')[1].split('"')[0])
    print Badges
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
                score = r.split('<div class="sg-rating sg-rating-')[1][0]
                name = r.split('<div class="explanation sg-h4">\n')[1].split('</div>')[0].strip()
                rating.append((name, score))

            comment = m.split('<p class="review-body"')[1].split('>')[1].split('</p')[0].strip()
            Review.append((date, author, rating, comment))
        # f = open('tmp.txt', 'w+')
#         f.write('here ' + url + '\n')
        # f.close()
        sql = 'insert into test values(' + str(prof['ProfId']) + ',"' + str(prof['LongProfessionalName']) + '");'
        print sql
        cur = conn.cursor()
        try:
            cur.execute(sql)
            print str(prof['ProfId']) + 'success'
        except Exception,e:
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
        return True
    except Exception, e:
        print 'error in get_surances( ' + str(id) + ' )', e
        return False
    # p rint Insurances
