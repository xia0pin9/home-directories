#!/usr/bin/env python

"""
This script can take a pcap format network flow data file and extrate all the contained network flow information, such as data length, request frequence, request interval, etc.
"""

import getopt, sys, os
import dpkt
import socket, hashlib, getopt

def usage():
    print """
    Usage:
    ------
        python %s -s <singlefile> -d <directory>

    Valid options are:

        -h      You are looking at this.
        -s      Single pcap file name.
        -d      Multiple pcap files, typically a directory path.
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

def mfile(directory, maxlen, minlen, tcpstreamnum, udpstreamnum, tcpmatric, udpmatric):
    dirlist = os.listdir(directory)
    filelist = []
    tsnum = tcpstreamnum
    usnum = udpstreamnum
    tcplist = tcpmatric
    udplist = udpmatric
    for fname in dirlist:
        fname = os.path.join(directory, fname)
        #print fname
        if fname.split('.')[len(fname.split('.'))-1] != 'pcap':
            continue
        if filemd5(fname) not in filelist:
            filelist.append(filemd5(fname))
            tsnum, usnum, tcplist, udplist = sfile(fname, maxlen, minlen, tsnum, usnum, tcplist, udplist)
        else:
            continue
        #print snum
    return tsnum, usnum, tcplist, udplist

def sfile(fname, maxlen, minlen, tcpstreamnum, udpstreamnum, tcpmatric, udpmatric):
    try:
        f = file(fname,"rb")
        pcap = dpkt.pcap.Reader(f)
    except:
        print "Open pcap error: maybe not pcap format file"
        sys.exit()
    streamlist = {}
    processnum = maxlen
    app = os.path.basename(fname)
    #print app
    
    for ts, buf in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                print eth.type
                continue
        except:
            continue   
            
        ip = eth.data
        src = socket.inet_ntoa(ip.src)
        dst = socket.inet_ntoa(ip.dst)
        sport = str(ip.data.sport)
        dport = str(ip.data.dport)
        proto = str(ip.p)
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
                streamlist[dst+'_'+dport+'_'+src+'_'+sport+'_'+proto].append(('r',packetlength))
            else:
                continue
        elif streamlist.has_key(src+'_'+sport+'_'+dst+'_'+dport+'_'+proto) :
            if len(streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto]) < processnum:
                streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto].append(('s',packetlength))
            else:
                continue
        else:
            streamlist[src+'_'+sport+'_'+dst+'_'+dport+'_'+proto] = [('s',packetlength)]         

    for key, stream in streamlist.items():
        if len(stream) < minlen:
            continue
        else:
            lenlist = []

            if key.split('_')[3] == 1900:
                continue
                print key

            for packets in stream:
                lenlist.append(packets[1])
                
            if key.split('_')[4] == '6':
                tcpmatric.append(lenlist)
                tcpstreamnum = tcpstreamnum + 1
            elif key.split('_')[4] == '17':
                udpmatric.append(lenlist)
                udpstreamnum = udpstreamnum + 1
            else:
                continue
            #print len(timelist)     
            #if tempsend == 0 or temprecv == 0:
            #    continue
            
    return tcpstreamnum, udpstreamnum, tcpmatric, udpmatric
    
def main():
    """ pcap paser for machine learning. """
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hs:d:o:p:m:n:", ["help", "single=", "directory=", "app=", "maxlen=", "minlen="])
        except getopt.GetoptError, err:
            print str(err)
            usage()
            sys.exit(1)
            
    fname = ''
    directory = ''
    maxlen = 16
    minlen = 16
    tcpstreamnum = 0
    udpstreamnum = 0
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--single"):
            fname = a
        elif o in ("-d", "--directory"):
            directory = a
        elif o in ("-m", "--maxlen"):
            maxlen = int(a)
        elif o in ("-n", "--minlen"):
            minlen = int(a)

    tcp_output = open('tcp.csv','w')
    udp_output = open('udp.csv','w')
    tcpmatric = []
    udpmatric = []
    
    print "Starting to processing the pcap file(s), please wait...\n"
    if fname and directory:
        print "Syntax error: You can only use one mode, either provide a single file or a directory"
        sys.exit()
    elif fname:
        tcpstreamnum, udpstreamnum, tcpmatric, udpmatric = sfile(fname, maxlen, minlen, tcpstreamnum, udpstreamnum, tcpmatric, udpmatric)
    elif directory:
        tcpstreamnum, udpstreamnum, tcpmatric, udpmatric = mfile(directory, maxlen, minlen, tcpstreamnum, udpstreamnum, tcpmatric, udpmatric)
    if tcpmatric != []:
        for tcp in tcpmatric:
            tcp_output.write(','.join(map(lambda x:str(x), tcp)))
            tcp_output.write('\n')
        print "Tcp stream flow matrics saved to %s , got %s stream flows\n " % (tcp_output.name, tcpstreamnum)
    if udpmatric != []:
        for udp in udpmatric:
            udp_output.write(','.join(map(lambda x:str(x), udp)))
            udp_output.write('\n')
        print "Udp stream flow matrics saved to %s , got %s stream flows\n" % (udp_output.name, udpstreamnum)
    tcp_output.close()
    udp_output.close()
    
    print "All done!"
                 
if __name__ == '__main__':
    main()
