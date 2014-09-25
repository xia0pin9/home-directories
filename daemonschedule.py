#!/usr/bin/evn python

import sys
import time
import schedule
import logging
from daemon import Daemon

class MyDaemon(Daemon):
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.setup_logger()
        self.setup_scheduler()

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        log_handler = logging.FileHandler('/tmp/oisc_schedule.log')
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)
        self.logger.addHandler(log_handler)
                
    def setup_scheduler(self):
        self.scheduler = schedule
        self.scheduler.every(1).seconds.do(self.job)
        #schedule.every(1).minutes.do(job)
        #schedule.every().hour.do(job)
        #schedule.every().day.at("16:30").do(job)
        #schedule.every().monday.do(job)
        #schedule.every().wednesday.at("13:15").do(job)

    def run(self):
        while True:
            try:
                self.scheduler.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)

    def job(self):
        self.logger.info("I'm working...")

if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-oisc.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.logger.info("Script started, entering loop")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.logger.info("Script stoped, exit loop") 
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.logger.info("Script restarted, reentering loop")
            daemon.restart()
        else:
            print "Unknown command, exit"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
