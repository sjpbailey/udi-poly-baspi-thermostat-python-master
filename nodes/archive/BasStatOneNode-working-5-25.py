try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
#import urllib3
import bascontrolwire_ns
from bascontrolwire_ns import Device, Platform

LOGGER = polyinterface.LOGGER

class BasStatOneNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, ipaddress, bc):
        super(BasStatOneNode, self).__init__(controller, primary, address, name)
        #self.lpfx = '%s:%s' % (address,name)
        self.ipaddress = (str(ipaddress).upper()) #Device(str(ipaddress).upper())
        self.bc = bc
        self.bIsBinary = None

    def start(self):
        if self.ipaddress is not None:
            self.bc = Device(self.ipaddress)
            #self.bIsBinary = bIsBinary
                  
        ### What is out there at this IP address
        if self.bc.ePlatform == Platform.BASC_NONE:
            LOGGER.info('Unable to connect')
            LOGGER.info('ipaddress')
        elif self.bc.ePlatform == Platform.BASC_PI or self.bc.ePlatform == Platform.BASC_PO:
            LOGGER.info('Connected to BASpi6U6R Module One')
        elif self.bc.ePlatform == Platform.BASC_ED:
            LOGGER.info('Connected to BASpi-Edge Module One')    
            self.setDriver('ST', 1)
        else:
            pass        
        
        ### Module Nodes
        if self.bc.ePlatform == Platform.BASC_ED:
                LOGGER.info('Universal inputs in this BASpi-EDGE = ' + str(self.bc.uiQty))
                LOGGER.info('Binary outputs in this BASpi-EDGE = ' + str(self.bc.boQty))
                LOGGER.info('Virtual Values in this BASpi-EDGE = ' + str(self.bc.vtQty))
        elif self.bc.ePlatform == Platform.BASC_PI or self.bc.ePlatform == Platform.BASC_PO:
                LOGGER.info('Universal inputs in this BASpi-6U6R = '  + str(self.bc.uiQty))
                LOGGER.info('Binary outputs in this BASpi-6U6R = '  + str(self.bc.boQty))
                LOGGER.info('Virtual Values in this BASpi-6U6R = ' + str(self.bc.vtQty))
        else:
            pass

        # What are the Physical Nodes or Device point currently reading
        LOGGER.info('Inputs')
        for i in range(1,7):
               LOGGER.info('UI ' + '\t' + str(self.bc.universalInput(i)))
        LOGGER.info('Outputs')
        for i in range(1,7):
               LOGGER.info('BO ' + '\t' + str(self.bc.binaryOutput(i)))
        for i in range(1,7):
            for x in range(1):
               LOGGER.info('VT '  + '\t' + str(self.bc.virtualValue(i, i)))

        # Set Nodes used
        ### Universal Inputs ###
        self.setInputDriver('GV0', 1)
        self.setInputDriver('GV1', 2)
        self.setInputDriver('GV2', 3)
        self.setInputDriver('GV3', 4)
        self.setInputDriver('GV4', 5)
        self.setInputDriver('GV5', 6)
        
    def setInputDriver(self, driver, input):
        input_val = self.bc.universalInput(input)
        self.setDriver(driver, input_val)
        
        
        ### Binary/Digital Outputs ###
        self.setOutputDriver('GV6', 1)
        self.setOutputDriver('GV7', 2)
        self.setOutputDriver('GV8', 3)
        self.setOutputDriver('GV9', 4)
        self.setOutputDriver('GV10', 5)
        self.setOutputDriver('GV11', 6)
        
    def setOutputDriver(self, driver, output):
        output_val = self.bc.binaryOutput(output)
        self.setDriver(driver, output_val)
        
        ### Virtual Values ###
        self.setVirtualDriver('GV12', 1, 201)
        self.setVirtualDriver('GV13', 2, 202)
        self.setVirtualDriver('GV14', 3, 203)
        self.setVirtualDriver('GV15', 4, 204)
        self.setVirtualDriver('GV16', 5, 205)
        self.setVirtualDriver('GV17', 6, 206)
        
    def setVirtualDriver(self, driver, input, chanel):
        vtout_val = self.bc.virtualValue(input, chanel)
        self.setDriver(driver, vtout_val)

    # OOP Control Commands
    # Heating Setpoint
    def setHeat(self, command):
        ivr_one = 'heat'
        heat = float(command.get('value'))
        def set_heat(self, command):
            heat = float(command.get('value'))
        if heat < 55 or heat > 100:
            LOGGER.error('Invalid Setpoint {}'.format(heat))
        else:
            self.bc.virtualValue(1, 201, heat)
            self.setDriver('GV12', heat)
            LOGGER.info('Heating Setpoint = ' + str(heat) +'F')

    # Cooling Setpoint
    def setCool(self, command):
        ivr_two = 'cool'
        cool = float(command.get('value'))
        def set_cool(self, command):
            cool = float(command.get('value'))
        if cool < 45 or cool > 100:
            LOGGER.error('Invalid Setpoint {}'.format(cool))
        else:
            self.bc.virtualValue(2, 202, cool)
            self.setDriver('GV13', cool)
            LOGGER.info('Cooling Setpoint = ' + str(cool) +'F')    
    
    # Remote Schedule 
    def cmdOn1(self, command):
        self.setsch = int(command.get('value'))
        self.setDriver("GV19", self.setsch)
        if self.setsch == 1:
            self.bc.virtualValue(3, 203, 1)
            self.setDriver("GV14", 1)
            LOGGER.info('Occupied')
        elif self.setsch == 0:
            self.bc.virtualValue(3, 203, 0)
            self.setDriver("GV14", 0)
            LOGGER.info('UnOccupied')
        else:
           pass

    # Fan Override 
    def cmdOn2(self, command):
        self.setfan = int(command.get('value'))
        self.setDriver("GV20", self.setfan) 
        if self.setfan == 1:
            self.bc.virtualValue(4, 204, 1)
            self.setDriver("GV15", 1)
            LOGGER.info('On')
        elif self.setfan == 0:
            self.bc.virtualValue(4, 204, 0)
            self.setDriver("GV15", 0)
            LOGGER.info('Auto')
        else:
            pass    
        
    def modeOn(self, command):
        self.modeOn = int(command.get('value',))
        self.setDriver('GV18', self.modeOn)
        if self.modeOn == 0:
            self.bc.virtualValue(5, 205, 1)
            self.bc.virtualValue(6, 206, 0)
            self.setDriver("GV16", 1)
            self.setDriver("GV17", 0) 
            LOGGER.info('Heat')
        elif self.modeOn == 1:
            self.bc.virtualValue(5, 205, 0)
            self.bc.virtualValue(6, 206, 0)
            self.setDriver("GV16", 0)
            self.setDriver("GV17", 0) 
            LOGGER.info('Off')
        elif self.modeOn == 2:
           self.bc.virtualValue(5, 205, 0)
           self.bc.virtualValue(6, 206, 1)
           self.setDriver("GV16", 0)
           self.setDriver("GV17", 1) 
           LOGGER.info('Cool')
        else:
           pass     
 
    def shortPoll(self):
        LOGGER.debug('shortPoll')
        
    def longPoll(self):
        LOGGER.debug('longPoll')
    
    def query(self,command=None):
        self.reportDrivers()

    
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 1, 'uom': 17},
        {'driver': 'GV1', 'value': 1, 'uom': 17},
        {'driver': 'GV2', 'value': 1, 'uom': 17},
        {'driver': 'GV3', 'value': 1, 'uom': 80},
        {'driver': 'GV4', 'value': 1, 'uom': 56},
        {'driver': 'GV5', 'value': 1, 'uom': 56},
        {'driver': 'GV6', 'value': 1, 'uom': 80},
        {'driver': 'GV7', 'value': 1, 'uom': 80},
        {'driver': 'GV8', 'value': 1, 'uom': 80},
        {'driver': 'GV9', 'value': 1, 'uom': 80},
        {'driver': 'GV10', 'value': 1, 'uom': 80},
        {'driver': 'GV11', 'value': 1, 'uom': 80},
        {'driver': 'GV12', 'value': 1, 'uom': 17},
        {'driver': 'GV13', 'value': 1, 'uom': 17},
        {'driver': 'GV14', 'value': 1, 'uom': 25},
        {'driver': 'GV15', 'value': 1, 'uom': 25},
        {'driver': 'GV16', 'value': 1, 'uom': 25},
        {'driver': 'GV17', 'value': 1, 'uom': 25},
        {'driver': 'GV18', 'value': 1, 'uom': 25},
        {'driver': 'GV19', 'value': 1, 'uom': 25},
        {'driver': 'GV20', 'value': 1, 'uom': 25},
       
        ]
    id = 'basstatid'
    """
    id of the node from the nodedefs.xml that is in the profile.zip. This tells
    the ISY what fields and commands this node has.
    """
    commands = {
                    #'BON1': cmdOn1,
                    #'BON2': cmdOn2,
                    'STHT': setHeat,
                    'STCL': setCool,
                    'HECO': modeOn,
                    'QUERY': query,
                }
    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """
### sjb gtb Union Made