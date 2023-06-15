#!/usr/bin/env python3

"""
Polyglot v3 node server - eWeLink
Copyright (C) 2023 Universal Devices

MIT License
"""

# https://github.com/UniversalDevicesInc/udi_python_interface/blob/master/API.md

import sys
from udi_interface import LOGGER, Interface
from lib.ewelink_interface import EWeLinkInterface

from nodes import EWeLinkController

polyglot = None
ewelink_interface = None
ewelink_controller = None

def configDoneHandler():
    polyglot.Notices.clear()

    # accessToken = ewelink_interface.getAccessToken()
    #
    # if accessToken is None:
    #     LOGGER.info('Access token is not yet available. Please authenticate.')
    #     polyglot.Notices['auth'] = 'Please initiate authentication'
    #     return

    ewelink_controller.discover()

def pollHandler(pollType):
    if pollType == 'longPoll':
        ewelink_controller.query()

# def addNodeDoneHandler(node):
#     # We will automatically query the device after discovery
#     ewelink_controller.addNodeDoneHandler(node)

def stopHandler():
    # Set nodes offline
    for node in polyglot.nodes():
        if hasattr(node, 'setOffline'):
            node.setOffline()
    polyglot.stop()

if __name__ == "__main__":
    try:
        polyglot = Interface([])
        polyglot.start({ 'version': '1.0.4', 'requestId': True })

        # Show the help in PG3 UI under the node's Configuration option
        polyglot.setCustomParamsDoc()

        # Update the profile files
        polyglot.updateProfile()    # Use checkProfile() instead?

        # Implements the API calls & Handles the oAuth authentication & token renewals
        ewelink_interface = EWeLinkInterface(polyglot)

        # Create the controller node
        ewelink_controller = EWeLinkController(polyglot, 'controller', 'controller', 'eWeLink Controller', ewelink_interface)

        # subscribe to the events we want
        polyglot.subscribe(polyglot.POLL, pollHandler)
        polyglot.subscribe(polyglot.STOP, stopHandler)
        # polyglot.subscribe(polyglot.CUSTOMDATA, ewelink_interface.customDataHandler)
        # polyglot.subscribe(polyglot.CUSTOMNS, ewelink_interface.customNsHandler)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, ewelink_interface.customParamsHandler)
        #polyglot.subscribe(polyglot.OAUTH, oauthHandler)
        polyglot.subscribe(polyglot.CONFIGDONE, configDoneHandler)
        # polyglot.subscribe(polyglot.ADDNODEDONE, addNodeDoneHandler)

        # We can start receive events
        polyglot.ready()

        # Just sit and wait for events
        polyglot.runForever()

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
