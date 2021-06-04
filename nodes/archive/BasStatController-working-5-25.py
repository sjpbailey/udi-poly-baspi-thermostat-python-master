try:
    from polyinterface import Controller,LOG_HANDLER,LOGGER
except ImportError:
    from pgc_interface import Controller,LOGGER
import logging
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from enum import Enum
import ipaddress
import bascontrolwire_ns
from bascontrolwire_ns import Device, Platform

# My Template Node
from nodes import BasStatOneNode

# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class BasStatController(Controller):
    def __init__(self, polyglot):
        super(BasStatController, self).__init__(polyglot)
        self.name = 'BASpi Thermostat Controller'
        self.hb = 0
        
    def start(self):
        serverdata = self.poly.get_server_data(check_profile=True)
        LOGGER.info('Started Fan Coil NodeServer {}'.format(serverdata['version']))
        # Show values on startup if desired.
        LOGGER.debug('ST=%s',self.getDriver('ST'))
        self.setDriver('ST', 1)
        self.heartbeat(0)
        self.check_params()
        self.set_debug_level(self.getDriver('GV1'))
        self.discover()
        
    def shortPoll(self):
        self.discover()
        LOGGER.debug('shortPoll')
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def longPoll(self):
        self.heartbeat() 
        LOGGER.debug('longPoll')
        

    def query(self,command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()
    
    class bc:
        def __init__(self, sIpAddress, ePlatform, bIsBinary ):
            self.bc = Device()
            self.ePlatform = ePlatform
            self.bIsBinary = bIsBinary
                
    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth('http://' + self.ipaddress + '/cgi-bin/xml-cgi')) 
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("BASpi6u6r.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))
    
    def delete(self):
        LOGGER.info('Rmoving BAS Thermostat')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config))
        LOGGER.info("process_config: Exit")

    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def set_debug_level(self,level):
        LOGGER.debug('set_debug_level: {}'.format(level))
        if level is None:
            level = 30
        level = int(level)
        if level == 0:
            level = 30
        LOGGER.info('set_debug_level: Set GV1 to {}'.format(level))
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level <= 10:
            LOGGER.setLevel(logging.DEBUG)
        elif level == 20:
            LOGGER.setLevel(logging.INFO)
        elif level == 30:
            LOGGER.setLevel(logging.WARNING)
        elif level == 40:
            LOGGER.setLevel(logging.ERROR)
        elif level == 50:
            LOGGER.setLevel(logging.CRITICAL)
        else:
            LOGGER.debug("set_debug_level: Unknown level {}".format(level))
        # this is the best way to control logging for modules, so you can
        # still see warnings and errors
        #if level < 10:
        #    self.set_module_logs(logging.DEBUG)
        #else:
        #    # Just warnigns for the modules unless in module debug mode
        #    self.set_module_logs(logging.WARNING)
        # Or you can do this and you will never see mention of module logging
        if level < 10:
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            # This is the polyinterface default
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    def check_params(self):
        self.removeNoticesAll()
        default_stat1_ip = None
        
        if 'stat1_ip' in self.polyConfig['customParams']:
            self.ipaddress = self.polyConfig['customParams']['stat1_ip']    

        else:
                self.ipaddress = default_stat1_ip
                LOGGER.error(
                    'check_params: The First BASpi6u6r IP is not defined in customParams, please add at least one.  Using {}'.format(self.ipaddress))
                  
       
        self.addCustomParam({'stat1_ip': self.ipaddress})

        if self.ipaddress == default_stat1_ip:
            self.setDriver('GV2', 0) 
            self.addNotice('Please set proper, IP for your Zone Controllers as key = stat1_ip and the BASpi IP Address for Value '
                           'in configuration page, and restart this nodeserver for additional controllers input irr2_ip, irr3_ip up to irr6')
            st = False

    def discover(self, *args, **kwargs):
        ### BASpi One ###
        LOGGER.info(self.ipaddress)
        if self.ipaddress is not None:
            self.bc = Device(self.ipaddress)
            self.addNode(BasStatOneNode(self, self.address, 'basstatid', 'Fan Coil', self.ipaddress, self.bc))
        
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.debug("cmd_set_debug_mode: {}".format(val))
        self.set_debug_level(val)

    id = 'controller'
    
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        'SET_DM': cmd_set_debug_mode,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV1', 'value': 10, 'uom': 25}, # Debug (Log) Mode, default=30=Warning
        {'driver': 'GV2', 'value': 1, 'uom': 2},
    ]
