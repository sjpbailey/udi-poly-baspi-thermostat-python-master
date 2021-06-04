#!/usr/bin/env python
"""
Thermostat Based on the BASpi-6U6R and the BASpi-Edge Controllers
"""
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys

LOGGER = polyinterface.LOGGER

""" Grab My Controller Node """
from nodes import BasStatController

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('BasStatPoly')
        """
        Instantiates the Interface to Polyglot.
        The name doesn't really matter unless you are starting it from the
        command line then you need a line Template=N
        where N is the slot number.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = BasStatController(polyglot)
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)
