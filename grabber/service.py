import os
from fresh.grabber.Config import Config

config  = Config(__service__.config_file('config.xml'))
grabber = config.get_grabber()

def run(conn):
    grabber.grab(conn)

def enter(service, order):
    if not order.get_hosts():
        return False
    service.enqueue_hosts(order, order.get_hosts(), run)
    service.set_order_status(order, 'queued')
    return True
