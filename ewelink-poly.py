#!/usr/bin/env python3
"""
Polyglot v3 node server eWeLink Interface
Copyright (C) 2023 James Paul
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER

from nodes import EWeLinkController
from nodes import EWeLinkNode

if __name__ == "__main__":
    try:
        LOGGER.debug("Staring eWelink Interface")
        polyglot = udi_interface.Interface([EWeLinkController, EWeLinkNode])
        polyglot.start()
        control = EWeLinkController(polyglot, 'controller', 'controller', 'eWeLink Controller')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
    except Exception as err:
        LOGGER.error('Exception: {0}'.format(err), exc_info=True)
        sys.exit(0)
