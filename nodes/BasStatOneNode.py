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
        LOGGER.info('Virtual')
        for i in range(1,8):
            for x in range(1):
                LOGGER.info('VT '  + '\t' + str(self.bc.virtualValue(i, x)))

        # Set Nodes used
        ### Universal Inputs ###
        self.setInputDriver('GV0', 1) # Room Temperature float
        self.setInputDriver('GV1', 2) # Supply Air Temp float
        self.setInputDriver('GV2', 3) # Return Air Temp float
        self.setInputDriver('GV3', 4) # Fan Status Bool
        self.setInputDriver('GV4', 5) # Outside Air Temp float
        self.setInputDriver('GV5', 6) # Attic Air Temp float
        
        ### Binary/Digital Outputs ###
        self.setOutputDriver('GV6', 1) # Fan Command BO-1
        self.setOutputDriver('GV7', 2) # Heat Stage 1 BO-2
        self.setOutputDriver('GV8', 3) # Heat Stage 2 BO-3
        self.setOutputDriver('GV9', 4) # Cool Stage 1 BO-4
        self.setOutputDriver('GV10', 5) # Cool Stage 2 BO-5
        self.setOutputDriver('GV11', 6) # Aux Override BO-6

        ### Virtual Values ###
        self.setVirtualDriver('GV12', 1, 201) # Virtual Value VT-1 Heat SETP
        self.setVirtualDriver('GV13', 2, 202) # Virtual Value VT-2 Cool SETP
        self.setVirtualDriver('GV14', 3, 203) # Virtual Value VT-3 Schedual
        self.setVirtualDriver('GV15', 4, 204) # Virtual Value VT-4 Fan Enable
        self.setVirtualDriver('GV16', 5, 205) # Virtual Value VT-5 Heat Enable
        self.setVirtualDriver('GV17', 6, 206) # Virtual Value VT-6 Cool Enable
        self.setVirtualDriver('GV18', 7, 207) # Virtual Value VT-7 Aux Enable   
    
        ### Control Drivers ###
        self.setControllerDriver('GV19' ) #For Schedual OVRD
        self.setControllerDriver('GV20' ) #For Fan OVRD
        self.setControllerDriver('GV21' ) #For Aux OVRD
        self.setControllerDriver('GV22' ) #For Mode OVRD
    
    def setControllerDriver(self, driver):

        pass

    ### Universal Input Conversion ###
    def setInputDriver(self, driver, input):
        input_val = self.bc.universalInput(input)
        count = 0
        if input_val is not None:
            count = int(float(input_val))
            self.setDriver(driver, count, force=True)        

    ### Binary Output Conversion ###    
    def setOutputDriver(self, driver, input):
        output_val = self.bc.binaryOutput(input)
        count = 0
        if output_val is not None:
            count = (output_val)
            self.setDriver(driver, count, force=True)

    ### Virtual Conversion ###
    def setVirtualDriver(self, driver, input, chanel):
        vtout_val = self.bc.virtualValue(input, chanel)
        self.setDriver(driver, vtout_val)
        count = 0
        if vtout_val is not None:
            count = int(float(vtout_val))
            #self.setDriver(driver, count, force=True)
        pass
    
    # OOP Control Commands
    # Remote Schedule 
    def cmdOn1(self, command):
        self.setsch = int(command.get('value'))
        self.setDriver("GV19", self.setsch, force=True)
        if self.setsch == 1:
            self.bc.virtualValue(3, 203, 1)
            self.setDriver("GV14", 1)
            LOGGER.info('Occupied')
        elif self.setsch == 0:
            self.bc.virtualValue(3, 203, 0)
            self.setDriver("GV14", 0)
            LOGGER.info('UnOccupied')
    
    # Heat Off Cool
    def modeOn(self, command):
        self.modeOn = int(command.get('value'))
        self.setDriver('GV22', self.modeOn, force=True)
        if self.modeOn == 0:
            self.bc.virtualValue(5, 205, 0)
            self.bc.virtualValue(6, 206, 0)
            self.setDriver("GV16", 0)
            self.setDriver("GV17", 0) 
            LOGGER.info('Off')
        elif self.modeOn == 1:
            self.bc.virtualValue(5, 205, 1)
            self.bc.virtualValue(6, 206, 0)
            self.setDriver("GV16", 1)
            self.setDriver("GV17", 0) 
            LOGGER.info('Heat')
        elif self.modeOn == 2:
            self.bc.virtualValue(5, 205, 0)
            self.bc.virtualValue(6, 206, 1)
            self.setDriver("GV16", 0)
            self.setDriver("GV17", 1)
            LOGGER.info('Cool')
        elif self.modeOn == 3:
            self.bc.virtualValue(5, 205, 1)
            self.bc.virtualValue(6, 206, 1)
            self.setDriver("GV16", 1)
            self.setDriver("GV17", 1) 
            LOGGER.info('Auto')
        pass    
            
    
    # Heating Setpoint
    def setHeat(self, command):
        ivr_one = 'heat'
        heat = float(command.get('value'))
        def set_heat(self, command):
            heat = float(command.get('value')*10)
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
            cool = float(command.get('value')*10)
        if cool < 40 or cool > 100:
            LOGGER.error('Invalid Setpoint {}'.format(cool))
        else:
            self.bc.virtualValue(2, 202, cool)
            self.setDriver('GV13', cool)
            LOGGER.info('Cooling Setpoint = ' + str(cool) +'F')       

    # Fan Override 
    def cmdOn2(self, command=None ):
        self.setfan = int(command.get('value'))
        self.setDriver("GV20", self.setfan, force=True) 
        if self.setfan == 1:
            self.bc.virtualValue(4, 204, 1)
            self.setDriver("GV15", 1, force=True)
            self.setDriver("GV6", 1, force=True)
            LOGGER.info('On')
        elif self.setfan == 0:
            self.bc.virtualValue(4, 204, 0)
            self.setDriver("GV15", 0, force=True)
            self.setDriver("GV6", 0, force=True)
            LOGGER.info('Auto')
        
    # Aux Override for Whole House Fan or Exhaust
    def cmdOn3(self, command=None):
        self.setaux = int(command.get('value'))
        self.setDriver("GV21", self.setaux, force=True) 
        if self.setaux == 1:
            self.bc.virtualValue(7, 207, 1)
            self.setDriver("GV18", 1, force=True)
            self.setDriver("GV11", 1, force=True)
            LOGGER.info('On')
    # def cmdOn4(self, command):    
        elif self.setaux == 0:
            self.bc.virtualValue(7, 207, 0)
            self.setDriver("GV18", 0, force=True)
            self.setDriver("GV11", 0, force=True)
            LOGGER.info('Auto')

    def query(self,command=None):
        self.reportDrivers()

    #"Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = '0x01020900'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 1, 'uom': 17}, # Room Temperature float
        {'driver': 'GV1', 'value': 1, 'uom': 17}, # Supply Air Temp float
        {'driver': 'GV2', 'value': 1, 'uom': 17}, # Return Air Temp float
        {'driver': 'GV3', 'value': 1, 'uom': 80}, # Fan Status Bool
        {'driver': 'GV4', 'value': 1, 'uom': 80}, # Outside Air Temp float
        {'driver': 'GV5', 'value': 1, 'uom': 17}, # Attic Air Temp float
        {'driver': 'GV6', 'value': 1, 'uom': 80}, # Fan Command BO-1
        {'driver': 'GV7', 'value': 1, 'uom': 80}, # Heat Stage 1 BO-2
        {'driver': 'GV8', 'value': 1, 'uom': 80}, # Heat Stage 2 BO-3
        {'driver': 'GV9', 'value': 1, 'uom': 80}, # Cool Stage 1 BO-4
        {'driver': 'GV10', 'value': 1, 'uom': 80}, # Cool Stage 2 BO-5
        {'driver': 'GV11', 'value': 1, 'uom': 80}, # Aux Override BO-6
        {'driver': 'GV12', 'value': 1, 'uom': 17}, # Virtual Value VT-1 Heat SETP
        {'driver': 'GV13', 'value': 1, 'uom': 17}, # Virtual Value VT-2 Cool SETP
        {'driver': 'GV14', 'value': 1, 'uom': 25}, # Virtual Value VT-3 Schedual
        {'driver': 'GV15', 'value': 1, 'uom': 25}, # Virtual Value VT-4 Fan Enable
        {'driver': 'GV16', 'value': 1, 'uom': 25}, # Virtual Value VT-5 Heat Enable
        {'driver': 'GV17', 'value': 1, 'uom': 25}, # Virtual Value VT-6 Cool Enable
        {'driver': 'GV18', 'value': 1, 'uom': 25}, # Virtual Value VT-7 Aux Enable
        {'driver': 'GV19', 'value': 0, 'uom': 25}, # For Schedual OVRD
        {'driver': 'GV20', 'value': 0, 'uom': 25}, # For Fan OVRD
        {'driver': 'GV21', 'value': 0, 'uom': 25}, # For Aux OVRD
        {'driver': 'GV22', 'value': 0, 'uom': 25}, # For Mode OVRD
        ]
    id = 'basstatid'
    """
    id of the node from the nodedefs.xml that is in the profile.zip. This tells
    the ISY what fields and commands this node has.
    """
    commands = {
                    'BON1': cmdOn1,
                    'BON2': cmdOn2,
                    'BON3': cmdOn3,
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