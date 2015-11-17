import urllib2
import re

def GetAttribute (url):
    resp = urllib2.urlopen(url);
    strAns = resp.read();
    ans = re.search(r'<div class="sg-p sg-mkt">[\W\w]*?</div>', strAns)
    if ans:
        strAns = ans.group(0);
        strAns = strAns[25:-6]
        print strAns

def Url (url):
    resp = urllib2.urlopen(url)
    print resp.read()

if __name__ == '__main__':
    test = "http://www.hit.edu.cn"
    f = open('tmp.txt')
    try:
        for line in f:
            ans = line.split('\t', 1)
            url = ans[0]
            print url
            GetAttribute(line)
    finally:
        f.close()


