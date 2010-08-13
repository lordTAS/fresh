import os
from fresh.grabber.Config import Config

config  = Config(__service__.config_file('config.xml'))
grabber = config.get_grabber()

def run(service, order, conn):
    grabber.grab(conn)

def enter(service, order):
    return len(order.get_hosts()) > 0
