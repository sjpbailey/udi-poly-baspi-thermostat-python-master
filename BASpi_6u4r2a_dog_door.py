try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import bascontrolwire_ns
from bascontrolwire_ns import Device, Platform

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = "BASPIAO_DOG"
        self.ipaddress = None  #self.ipaddress = None
        self.debug_enable = 'False'
        self.poly.onConfig(self.process_config)
        self.pwm = None
        self.pwm_dc = 0

    def start(self):
        # This grabs the server.json data and checks profile_version is up to date
        serverdata = self.poly.get_server_data()
        LOGGER.info('Started BASPI6U4R2AO Controller {}'.format(serverdata['version']))
        self.check_params()
        self.discover()
        self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")

    def shortPoll(self):
        self.discover()

    def longPoll(self):
        self.discover()
        

    def query(self,command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    class bc:
        def __init__(self, sIpAddress):
            self.bc = Device()

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth('http://' + self.ipaddress + '/cgi-bin/xml-cgi'))
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("BASpi_DOGDOOR.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))                

    def discover(self, *args, **kwargs):
        if self.ipaddress is not None:
            self.bc = Device(self.ipaddress)
            self.addNode(Baspiaodog_one(self, self.address, 'baspiao1_id', 'BASpi6U4R2AO 1', self.ipaddress, self.bc))
            self.setDriver('GV19', 1)
        

    def delete(self):
        LOGGER.info('Removing BASpi6U4R2AO')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    def check_params(self):
        self.remove_notices_all(self)
        self.remove_notice_test(self)
        default_baspidog_ip = None
        st = None
        
        if 'baspidog_ip' in self.polyConfig['customParams']:
            self.ipaddress = self.polyConfig['customParams']['baspidog_ip']
        else:
            self.ipaddress = default_baspidog_ip
            LOGGER.error(
                'check_params: BASpi_DOGDOOR IP not defined in customParams, please add it.  Using {}'.format(self.ipaddress))
            st = False
       
        if 'debug_enable' in self.polyConfig['customParams']:
            self.debug_enable = self.polyConfig['customParams']['debug_enable']

        # Make sure they are in the params 'password': self.password, 'user': self.user,
        self.addCustomParam({'baspidog_ip': self.ipaddress, 'debug_enable': self.debug_enable})

        # Add a notice if they need to change the IP Address for == default_baspidog_ip.
        if self.ipaddress == default_baspidog_ip:
            self.addNotice('Please set proper, IP Address for the key baspidog_ip in the configuration page, and restart this nodeserver')

        # Add a notice if they need to change the user/password from the defaultself.user == default_user or self.password == default_password or .
        if self.ipaddress == default_baspidog_ip:
            self.addNotice('Please set proper, BASpi_DOGDOOR IP in configuration page, and restart this nodeserver')
            st = False

        if st == True:
            return True
        else:
            return False

    def remove_notice_test(self,command):
        LOGGER.info('remove_notice_test: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNotice('test')

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        'REMOVE_NOTICE_TEST': remove_notice_test
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV19', 'value': 1, 'uom': 2},
    ]

class Baspiaodog_one(polyinterface.Node):
    def __init__(self, controller, primary, address, name, ipaddress, bc):
        super(Baspiaodog_one, self).__init__(controller, primary, address, name)
        self.ipaddress = (str(ipaddress).upper()) #Device(str(ipaddress).upper())
        self.bc = bc

    def start(self):
        if self.ipaddress is not None:
            self.bc = Device(self.ipaddress)
            if self.bc.ePlatform == Platform.BASC_NONE:
                LOGGER.info('Unable to connect')
            if self.bc.ePlatform == Platform.BASC_AO:
                LOGGER.info('connected to BASpi6U4R2AO')    

            LOGGER.info('\t' + str(self.bc.uiQty) + ' Universal inputs in this BASpi6u4r2ao')
            LOGGER.info('\t' + str(self.bc.boQty) + ' Binary outputs in this BASpi6u4r2ao')
            LOGGER.info('\t' + str(self.bc.aoQty) + ' Analog outputs In This BASpi6u4r2ao')
            LOGGER.info('Please open your Device Webpage to configure your input types')

     # Please Configure your Devices inputs by logginging into the devices GUI at http://"yout ip address"             
            # Universal Inputs   
            input_one = self.bc.universalInput(1)
            input_two = self.bc.universalInput(2)
            input_tre = self.bc.universalInput(3)
            input_for = self.bc.universalInput(4)
            input_fiv = self.bc.universalInput(5)
            input_six = self.bc.universalInput(6)
            
            # Binary/Analog Outputs
            output_one = self.bc.binaryOutput(1)
            output_two = self.bc.binaryOutput(2)
            output_tre = self.bc.binaryOutput(3)
            output_for = self.bc.binaryOutput(4)
            output_ao1 = self.bc.analogOutput(1)
            output_ao2 = self.bc.analogOutput(2)   
            
            
            # Universal Inputs
            LOGGER.info("Temp: " + str(input_one))
            LOGGER.info("Temp: " + str(input_two))
            LOGGER.info("Temp: " + str(input_tre))
            LOGGER.info("Temp: " + str(input_for))
            LOGGER.info("Temp: " + str(input_fiv))
            LOGGER.info("Temp: " + str(input_six))
                
            # Binary/Analog Outputs 
            LOGGER.info("OnOff: " + str(output_one))
            LOGGER.info("OnOff: " + str(output_two))
            LOGGER.info("OnOff: " + str(output_tre))
            LOGGER.info("OnOff: " + str(output_for))
            LOGGER.info("Analog: " + str(output_ao1))
            LOGGER.info("Analog: " + str(output_ao2))
                
            # Universal Inputs
            self.setDriver('GV13', input_one, force=True)
            self.setDriver('GV14', input_two, force=True)
            self.setDriver('GV15', input_tre, force=True)
            self.setDriver('GV16', input_for, force=True)
            self.setDriver('GV17', input_fiv, force=True)
            self.setDriver('GV18', input_six, force=True)
            
            # Binary/Digital Outputs
            self.setDriver('GV1', output_one, force=True)
            self.setDriver('GV2', output_two, force=True)
            self.setDriver('GV3', output_tre, force=True)
            self.setDriver('GV4', output_for, force=True)
            self.setDriver('GV5', output_ao1, force=True)
            self.setDriver('GV0', output_ao2, force=True)
        
        LOGGER.info("BASpi6U4R2AO IP IO Points configured")
    
    # Output 1 Open Door
    def setOnOff(self,command):
        if self.bc.binaryOutput(1) != 1:
            self.bc.binaryOutput(1, 1)
            self.setDriver("GV1", 1)
            LOGGER.info('Output 1 On')
            time.sleep(5)
            self.bc.binaryOutput(1, 0)
            self.setDriver("GV1", 0)
            LOGGER.info('Output 1 Off')
            self.setDriver("GV1", 1)
    # Output 2 Close Door
    def setOnOff2(self,command):
        GV2 = command.get('value')
        if self.bc.binaryOutput(2) != 1:
            self.bc.binaryOutput(2, 1)
            self.setDriver("GV2", 1)
            LOGGER.info('Output 2 On')
            time.sleep(5)
            self.bc.binaryOutput(2, 0)
            self.setDriver("GV2", 0)
            LOGGER.info('Output 2 Off')         
    # Enable Lock Door Open
    def setLockOpn(self,command):
        if self.bc.binaryOutput(4) != 1:
            self.bc.binaryOutput(4, 1)
            self.setDriver("GV4", 1)
            LOGGER.info('Output 4 On')
            time.sleep(5)
            self.bc.binaryOutput(1, 1)
            self.setDriver("GV1", 1)
            LOGGER.info('Output 1 On')
            time.sleep(5)
            self.bc.binaryOutput(1, 0)
            self.setDriver("GV1", 0)
            LOGGER.info('Output 1 Off')
            self.setDriver("GV1", 1)
    # Disable Lock Door Open
    def setLockCls(self,command):
        if self.bc.binaryOutput(4) == 1:
            self.bc.binaryOutput(4, 0)
            self.setDriver("GV4", 1)
            LOGGER.info('Output 4 Off')
                
    # Analog Output 1
    def setValue5(self, command):
        output_ao1 = 'speed'
        speed = float(command.get('value'))
        def set_speed(self, command):
            speed = float(command.get('value'))
        if speed < 0 or speed > 11:
            LOGGER.error('Invalid volts selection {}'.format(speed))
        else:
            #self.device.set_fan_speed(FanSpeed("%04d" % speed))
            self.bc.analogOutput(1, speed)
            self.setDriver('GV5', speed)
            LOGGER.info('Analog Output 1 = ' + str(speed) +'VDC') 
        
    # Analog Output 2
    def setValue6(self, command=None):
        speed2 = float(command.get('value'))
        def set_speed(self, command):
            speed2 = float(command.set('value'))
        if speed2 < 0 or speed2 > 11:
            LOGGER.error('Invalid volts selection {}'.format(speed2))
        else:
            #self.device.set_fan_speed(FanSpeed("%04d" % speed))
            self.bc.analogOutput(2, speed2)
            self.setDriver('GV0', speed2)
            LOGGER.info('Analog Output 2 = ' + str(speed2) +'VDC')

    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV13', 'value': 1, 'uom': 25},
        {'driver': 'GV14', 'value': 1, 'uom': 25},
        {'driver': 'GV15', 'value': 1, 'uom': 25},
        {'driver': 'GV16', 'value': 1, 'uom': 25},
        {'driver': 'GV17', 'value': 1, 'uom': 17},
        {'driver': 'GV18', 'value': 1, 'uom': 25},
        {'driver': 'GV1', 'value': 1, 'uom': 80},
        {'driver': 'GV2', 'value': 1, 'uom': 80},
        {'driver': 'GV3', 'value': 1, 'uom': 80},
        {'driver': 'GV4', 'value': 1, 'uom': 80},
        {'driver': 'GV5', 'value': 1, 'uom': 72},
        {'driver': 'GV0', 'value': 1, 'uom': 72},
        ]
   
    id = 'baspiaodog_id'
    
    commands = {
        'DON': setOnOff,
        'DON2': setOnOff2,
        'DONL': setLockOpn,
        'DONC': setLockCls,
        'SPEED2': setValue6,
        'SPEED': setValue5,
        'QUERY': query,
        }
    
if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('BASPIAODOG')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
        
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
        
