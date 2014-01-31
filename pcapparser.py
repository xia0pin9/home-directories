#!/usr/bin/env python

import getopt, sys, os
import dpkt
import socket, hashlib, getopt

def usage():
    print """
    Usage:
    ------
        python %s -s <singlefile> -d <directory> -o <outputfile>

    Valid options are:

        -h      You are looking at this.
        -s      Single pcap file name.
        -d      Multiple pcap files, typically a directory path.
        -o      Output file name, default is 'output.csv'.
        -m      Maxnum packets to be processed, default is 16.
        -n      Minnum packets of a stream, default is 16.
    """ % (sys.argv[0])

def filemd5(f):
    md5 = hashlib.md5()
    block_size=128*md5.block_size
    file = open(f, 'rb')
    while True:
        data = file.read(block_size)
        if not data:
            break
        md5.update(data)
    file.close()
    return md5.hexdigest()

def mfile(directory, output, maxlen, minlen, streamnum):
    dirlist = os.listdir(directory)
    filelist = []
    snum = streamnum
    for fname in dirlist:
        fname = os.path.join(directory, fname)
        #print fname
        if fname.split('.')[len(fname.split('.'))-1] != 'pcap':
            continue
        if filemd5(fname) not in filelist:
            filelist.append(filemd5(fname))
            snum = sfile(fname, output, maxlen, minlen, snum)
        else:
            continue
        #print snum
    return snum

def sfile(fname, output, maxlen, minlen, streamnum):
    try:
        f = open(fname,'rb')
        pcap = dpkt.pcap.Reader(f)
    except:
        print "Open pcap error: maybe not pcap format file"
        sys.exit()
    streamlist = {}
    print fname
    processnum = maxlen
    minnum = 10
    app = fname.split('.')[len(fname.split('.'))-2]
    app = app.split('\\')[len(app.split('\\'))-1]
    app = app.split('/')[len(app.split('/'))-1]
    app = app.split('_')[0]
    #print app
    
    for ts, buf in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                print eth.type
                continue
            
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            sport = str(ip.data.sport)
            dport = str(ip.data.dport)
            if ip.p==6:
                proto = 'tcp' 	
            elif ip.p == 17:
                proto = 'udp'
            packetlength = ip.len-ip.hl*4
    
            #if packetnum == 1:
            #    init_ts = ts
            #else ts -= init_ts
    
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                packetlength = packetlength - ip.data.off*4
                #print ( ip.data.flags & dpkt.tcp.TH_FIN ) != 0
                #print "%s : tcp, %s, %s, %4s" % (ts,ip.ttl,ip.len,ip.src)
            elif ip.p == dpkt.ip.IP_PROTO_UDP:
                packetlength = packetlength - 8
                #print "%s : udp, %s, %s, %4s" % (ts,ip.ttl,ip.len,ip.src)
            else:
                print ip.p
                continue
            #print sport, dport, packetlength
    
            if  streamlist.has_key(dst+'_'+dport+'_'+src+'_'+sport+'_'+proto) :
                if len(streamlist[dst+'_'+dport+'_'+src+'_'+sport+'_'+proto]) < processnum:
                    streamlist[dst+'_'+dport+'_'+src+'_'+sport+'_'+proto].append(('r',ts,packetlength,ip.hl))
                else:
                    continue
            elif streamlist.has_key(src+'_'+sport+'_'+dst+'_'+dport+'_'+proto) :
                if len(streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto]) < processnum:
                    streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto].append(('s',ts,packetlength,ip.hl))
                else:
                    continue
            else:
                streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto] = [('s',ts,packetlength,ip.hl)]
        except:
            continue           

    for key, stream in streamlist.items():
        if len(stream) < minnum:
            continue
        else:
            init_ts = 0
            lenlist = []
            timelist = []
            tempsend = 0
            temprecv = 0
            zeronum = 0
            streaminfo = []
            if key.split('_')[3] == 1900:
                continue
                print key
            streaminfo.append(key.split('_')[4])
            streaminfo.append(key.split('_')[1])
            streaminfo.append(key.split('_')[3])
            for packets in stream:
                if init_ts == 0:
                    init_ts = packets[1]                        
                time = "%.6f" % (float(packets[1])-float(init_ts))
                timelist.append(float(time))
                lenlist.append(packets[2])
                if packets[2] == 0:
                    zeronum += 1
                if packets[0] == 's':
                    tempsend += 1
                else:
                    temprecv += 1
            #print len(timelist)     
            if tempsend == 0 or temprecv == 0:
                continue
            streamnum = streamnum + 1       
            streaminfo.append(str(tempsend))
            streaminfo.append(str(temprecv))
            streaminfo.append(str(max(lenlist)))
            streaminfo.append(str(min(lenlist)))
            streaminfo.append(str(sum(lenlist)/float(len(lenlist))))
            streaminfo.append(str(zeronum))
            streaminfo.append(','.join(map(lambda x:str(x),lenlist)))
            for i in range(len(lenlist), maxlen):
                streaminfo.append('?')
            streaminfo.append(str(timelist[len(timelist)-1]-timelist[0]))
            timefirst = timelist[0]
            for i in range(1, len(timelist)):
                temp = timelist[i]
                timelist[i] = "%.3f" % (timelist[i]-timefirst)
                timefirst = temp
            streaminfo.append(str(max(map(lambda x:float(x), timelist))))
            streaminfo.append(str(min(map(lambda x:float(x), timelist[1:]))))
            streaminfo.append(str(sum(map(lambda x:float(x), timelist[1:]))/(len(timelist)-1)))
            streaminfo.append(','.join(timelist[1:]))
            for i in range(len(lenlist), maxlen):
                streaminfo.append('?')
            streaminfo.append(app)
            output.write('\n')
            output.write(','.join(streaminfo))
    return streamnum
    
def main():
    """ pcap paser for machine learning. """
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hs:d:o:p:m:n:", ["help", "single=", "directory=", "output=", "app=", "maxlen=", "minlen="])
        except getopt.GetoptError, err:
            print str(err)
            usage()
            sys.exit(1)
            
    fname = ''
    directory = ''
    output = 'output.csv'
    maxlen = 16
    minlen = 16
    streamnum = 0
    columnnum = 0
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--single"):
            fname = a
        elif o in ("-d", "--directory"):
            directory = a
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-m", "--maxlen"):
            maxlen = int(a)
        elif o in ("-n", "--minlen"):
            minlen = int(a)

    output = open(output,'w')
    print "Setting up the columns, please wait...\n"
    columns = ['proto,sport,dport,sentnum,recvnum,maxlen,minlen,avelen,zeronum',]
    columnnum = columnnum + 14 # fixed column number
    for i in range(1, maxlen+1):
        columns.append('len'+str(i))
        columnnum = columnnum + 1
    columns.append('duration,maxinterval,mininterval,aveinterval')
    for i in range(1, maxlen):
        columns.append('t'+str(i))
        columnnum = columnnum + 1
    columns.append('app')
    #print ','.join(columns)
    output.write(','.join(columns))
    print "Columns set up complete, column number is %s.\n" % columnnum
    print "Starting to processing the pcap file(s), please wait...\n"
    if fname and directory:
        print "Syntax error: You can only use one mode, either provide a single file or a directory"
        sys.exit()
    elif fname:
        streamnum = sfile(fname, output, maxlen, minlen, streamnum)
    elif directory:
        streamnum = mfile(directory, output, maxlen, minlen, streamnum)
    print "\nGot %s stream flows.\n" % streamnum
    print "All done, pcap file(s) propperties saved to", output.name
    output.close()
                 
if __name__ == '__main__':
    main()
