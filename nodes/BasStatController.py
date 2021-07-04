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
        self.ipaddress = None
        self.debug_enable = 'False'
        self.poly.onConfig(self.process_config)

    def start(self):
        # This grabs the server.json data and checks profile_version is up to date
        serverdata = self.poly.get_server_data()
        if 'debug_enable' in self.polyConfig['customParams']:
            self.debug_enable = self.polyConfig['customParams']['debug_enable']
        self.heartbeat(0)
        if self.check_params():
            self.discover()

        LOGGER.info('Starting BASpi Thermostat Controller')
        self.check_params()
        self.discover()
        #self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")

    def shortPoll(self):
        self.get_request(self)
        self.check_params()        
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def longPoll(self):
        self.heartbeat()

    def query(self, command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()
    class bc:
        def __init__(self, sIpAddress):
            self.bc = Device()    

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(self.ipaddress))
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("BASpiFanCoil.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))
    

    def discover(self, *args, **kwargs):
        if self.ipaddress is not None:
            self.bc = Device(self.ipaddress)
            self.addNode(BasStatOneNode(self, self.address, 'basstatid', 'Fan Coil', self.ipaddress, self.bc))
            self.setDriver('GV0', 1, force=True)
                            
    def delete(self):
        LOGGER.info('Removing Fan Coil')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    def heartbeat(self, init=False):
        #LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        #   LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON", 2)
            self.hb = 1
        else:
            self.reportCmd("DOF", 2)
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
        st = True
        self.remove_notices_all()
        default_stat1_ip = None
        
        if 'stat1_ip' in self.polyConfig['customParams']:
            self.ipaddress = self.polyConfig['customParams']['stat1_ip']
        else:
            self.ipaddress = default_stat1_ip
            LOGGER.error(
                'check_params: BASpi IP not defined in customParams, please add it.  Using {}'.format(self.ipaddress))
            st = False
        
        if 'debug_enable' in self.polyConfig['customParams']:
            self.debug_enable = self.polyConfig['customParams']['debug_enable']

        # Make sure they are in the params 'password': self.password, 'user': self.user,
        self.addCustomParam({'stat1_ip': self.ipaddress, 'debug_enable': self.debug_enable})

        # Add a notice if they need to change the user/password from the defaultself.user == default_user or self.password == default_password or .
        if self.ipaddress == default_stat1_ip:
            self.addNotice('Please set proper, BASpi IP as key = stat1_ip and your IP Address'
                           'in configuration page, and restart this nodeserver')
            st = False

        if st:
            return True
        else:
            return False

    def remove_notices_all(self):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command):
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
        {'driver': 'GV0', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 10, 'uom': 25}, # Debug (Log) Mode, default=30=Warning
    ]
