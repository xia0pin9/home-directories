#!/usr/bin/python

try:
    import sys, getopt, socket, urllib, httplib2, urllib2 
    from urllib import urlencode
    from random import seed, randint
except:
    print """
Execution error:
    You required some basic Python Libraries.
    This application use: sys, getopt.
    Please, check if you have all of them installed in your system.
"""
    sys.exit(1)

USER_AGENTS = [
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Crazy Browser 1.0.5)",
	"curl/7.7.2 (powerpc-apple-darwin6.0) libcurl 7.7.2 (OpenSSL 0.9.6b)",
	"Mozilla/5.0 (X11; U; Linux amd64; en-US; rv:5.0) Gecko/20110619 Firefox/5.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b8pre) Gecko/20101213 Firefox/4.0b8pre",
	"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205",
	"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)",
	"Opera/9.80 (Windows NT 6.1; U; sv) Presto/2.7.62 Version/11.01",
	"Opera/9.80 (Windows NT 6.1; U; pl) Presto/2.7.62 Version/11.00",
	"Opera/9.80 (X11; Linux i686; U; pl) Presto/2.6.30 Version/10.61",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2",
	"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.872.0 Safari/535.2",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.812.0 Safari/535.1",
	"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
	]

def printSyntax ():
    """Print application syntax."""
    print """\nGoogle Safe Browsing Lookup/API

Usage:
------
    python %s -u <url> -l <filelist> OTHER OPTIONS

Valid OPTIONS are:

    -h      You are looking at this.
    -u      Single url target.
    -f      If you have multiple urls, you can specify a file with one url per line.
    -s      Simple (default) Mode, check the http status of the url(s) ot see if they are still valid.
    -l      Check the url(s) through google safe browsing lookup api.
    -a      Check the url(s) through google safe browsing api.
    
""" % (sys.argv[0])
    
def setup(mode, url=None, urls=None):
    """Set up the needed variables, prepare target the url or all the urls of a file."""

    # Only one of the two possible inputs can be setted.
    if (not url and not urls) or (url and urls):
        print "Syntax error, you can only specify one of the two possible inputs at one time."

    urltocheck = []    
    if url:
        urltocheck = [url]
    elif urls:
        try:
            tempfile = open(urls)
            urltocheck=tempfile.read().split("\n")
        except:
            print "\nIt is not possible to open file (%s). \n" % (urls)
            sys.exit(1)
        if tempfile:
            tempfile.close()
    else:
        print "NO url(s) speficied"
 
    if mode == "simple":
        simplecheck(urltocheck)
    elif mode == "lookup":
        lookupcheck(urltocheck)
    else:
        apicheck(urltocheck)

def simplecheck(urltocheck):
    #Try to check all the urls...
    print "\nSimple mode. Start testing...\n"
    count=0
    while count < len(urltocheck):
    #Build the URL(s)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            print 'socket error: %s'%e
            sock.close()
            continue
    
        url =  urltocheck[count]
        tempurl = url.split(';')
        url = tempurl[0]
        count+=1
    
        if not url:
            break
        if url.find('http') == -1:
            url = 'http://'+url
        try:
            proto, rest = urllib.splittype(url)
            host, location = urllib.splithost(rest)
            host, port = urllib.splitport(host)
        except:
            print 'No. %4s  Url:%s  TypeError: expected string or buffer'%(count,url)
            continue
        
        if not proto:
            proto = 'http'
            if not port:
                port = 80
        elif proto == 'http':
            if not port:
                port = 80
        elif proto == 'https':
            if not port:
                port = 443
        else: port = 80

        if not location:
            location = "/"

        try:
            sock.connect((host,int(port)))
        except socket.error, e:
            print 'No. %4s  Url:%s  Socket connect error:%s'%(count,url,e)
            sock.close()
            continue
        #Build the Headers with a random User-Agent
        useragent = USER_AGENTS[randint(0, len(USER_AGENTS))-1]
        data = ''   
        try:
            str='GET %s HTTP/1.1\r\nHost:%s\r\nUser-Agent:%s\r\nConnection:keep-alive\r\n\r\n'%(location,host,useragent)
            sock.send(str)
            data = sock.recv(1024)
    
            if data.find('HTTP/') == -1:
                print 'No. %4s  Url:%s  Odd! Detailed information:\n%s'%(count,url,data)
            else:
                if  data[data.find('HTTP/')+9:data.find('HTTP/')+12] != "200":
                    temp = data.split('\r\n')
                    t = temp[0]
                    print 'No. %4s  Url:%s  Reason:%s'%(count,url,t[9:])
    
        except socket.error, e:
            print 'No. %4s  Url:%s  Socket send error:%s'%(count,url,e)
            sock.close()
            continue
        sock.close()

def lookupcheck(urltocheck):
    #Build the URL(s)
    url = ""

    #Build the Headers with a random User-Agent
    headers = { "User-Agent" : USER_AGENTS[randint(0, len(USER_AGENTS))-1]}

    print "\nLOOKUP\n"

def apicheck(urltocheck):
    #Build the URL(s)
    url = ""

    #Build the Headers with a random User-Agent
    headers = { "User-Agent" : USER_AGENTS[randint(0, len(USER_AGENTS))-1]}

    print "\nAPI\n"    

def main():
    """Main method"""

    #Syntax check
    if len(sys.argv) < 3:
        printSyntax()
        sys.exit(1)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hslau:f:", ["help","simple","lookup","api","url=","file="])
        except getopt.GetoptError, err:
            #print the error message
            print str(err) 
            printSyntax()
            sys.exit(1)

    #Load input parameters
    url = None
    urls = None
    mode = "simple"
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printSyntax()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-f", "--file"):
            urls = arg
        elif opt in ("-l", "--lookup"):
            mode = "lookup"
        elif opt in ("-a", "--api"):
            mode = "api"
        else:
            mode = "simple"

    # Initialize PRNG seed and relevant variables
    seed()

    checked = 0
    
    # Check the url(s)
    setup(mode, url, urls)
    
    # App is finished
    sys.exit()
    
if __name__ == '__main__':
    main()