import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from Config import Config

filename = os.path.join(os.path.dirname(__file__), 'config.xml')
config   = Config(filename)
grabber  = config.get_grabber()

def run(service, order, conn):
    grabber.grab(conn)

def enter(service, order):
    return len(order.get_hosts()) > 0
