#!/usr/bin/python
#/*******************************************************************************
# *
# * Contributors:
# * Abolee Diwate, Anand Agrawal, Marco Saucedo, Tobias Spitz
# * 
# * Modified the template code by Cirrus Link Solutions - initial implementation
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License 2.0 which is available at
# * http://www.eclipse.org/legal/epl-2.0.
# ********************************************************************************/

# Usage: python Vacucell_MT_Log.py COMx COMy

import sys
#from trial import genPayload
sys.path.insert(0, "../core/")

import paho.mqtt.client as mqtt
import sparkplug_b as sparkplug
import time
import serial 

from sparkplug_b import *
from DeviceConfig_v2 import MT_Balance, Vacucell

#importing the payload function
from genPayload import *

# Application Variables
serverUrl = "mql4hivemqdev.am.lilly.com"
myGroupId = "Sparkplug B Devices"
myNodeName = "Raspberry Pi : ETCInterns"
myDeviceName = "Emulated Device"
publishPeriod = 5000
######################################################################

######################################################################
# The callback for when the client receives a CONNACK response from the server.
######################################################################
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code "+str(rc))
    else:
        print("Failed to connect with result code "+str(rc))
        sys.exit()

    global myGroupId
    global myNodeName
    
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("spBv1.0/" + myGroupId + "/NCMD/" + myNodeName + "/#")
    client.subscribe("spBv1.0/" + myGroupId + "/DCMD/" + myNodeName + "/#")
######################################################################

######################################################################
# The callback for when a PUBLISH message is received from the server.
######################################################################
def on_message(client, userdata, msg):
    print("Message arrived: " + msg.topic)
    tokens = msg.topic.split("/")

    if tokens[0] == "spBv1.0" and tokens[1] == myGroupId and (tokens[2] == "NCMD" or tokens[2] == "DCMD") and tokens[3] == myNodeName:
        inboundPayload = sparkplug_b_pb2.Payload()
        inboundPayload.ParseFromString(msg.payload)
        for metric in inboundPayload.metrics:
            
            if metric.name == "Node Control/Next Server":
                # 'Node Control/Next Server' is an NCMD used to tell the device/client application to
                # disconnect from the current MQTT server and connect to the next MQTT server in the
                # list of available servers.  This is used for clients that have a pool of MQTT servers
                # to connect to.
                print( "'Node Control/Next Server' is not implemented in this example")
            
            elif metric.name == "Node Control/Rebirth":
                # 'Node Control/Rebirth' is an NCMD used to tell the device/client application to resend
                # its full NBIRTH and DBIRTH again.  MQTT Engine will send this NCMD to a device/client
                # application if it receives an NDATA or DDATA with a metric that was not published in the
                # original NBIRTH or DBIRTH.  This is why the application must send all known metrics in
                # its original NBIRTH and DBIRTH messages.
                publishBirth() #same as the defined reboot functionality
           
            elif metric.name == "Node Control/Reboot":
                # 'Node Control/Reboot' is an NCMD used to tell a device/client application to reboot
                # This can be used for devices that need a full application reset via a soft reboot.
                # In this case, we fake a full reboot with a republishing of the NBIRTH and DBIRTH
                # messages.
                publishBirth()
            
            elif metric.name == "output/Device Metric2":
                # This is a metric we declared in our DBIRTH message and we're emulating an output.
                # So, on incoming 'writes' to the output we must publish a DDATA with the new output
                # value.  If this were a real output we'd write to the output and then read it back
                # before publishing a DDATA message.

                # We know this is an Int16 because of how we declated it in the DBIRTH
                newValue = metric.int_value
                print( "CMD message for output/Device Metric2 - New Value: {}".format(newValue))

                # Create the DDATA payload
                #payload = sparkplug.getDdataPayload()
                #addMetric(payload, None, None, MetricDataType.Int16, newValue)

                #DDATA Payload for MT Balance
                payload = sparkplug.getDdataPayload()
                                
            elif metric.name == "output/Device Metric3":
                # This is a metric we declared in our DBIRTH message and we're emulating an output.
                # So, on incoming 'writes' to the output we must publish a DDATA with the new output
                # value.  If this were a real output we'd write to the output and then read it back
                # before publishing a DDATA message.

                # We know this is an Boolean because of how we declated it in the DBIRTH
                newValue = metric.boolean_value
                print( "CMD message for output/Device Metric3 - New Value: %r" % newValue)

                # Create the DDATA payload
                payload = sparkplug.getDdataPayload()
                addMetric(payload, None, None, MetricDataType.Boolean, newValue)

                # Publish a message data
                byteArray = bytearray(payload.SerializeToString())
                client.publish("spBv1.0/" + myGroupId + "/DDATA/" + myNodeName + "/" + myDeviceName, byteArray, 0, False)
            
            else:
                print( "Unknown command: " + metric.name)
    
    else:
        print( "Unknown command...")

    print( "Done publishing")
######################################################################
#Defining the device instance and declaring its relevant parameters
######################################################################
D1 = MT_Balance("/dev/ttyUSB0",                                                 #Defining the first device parameters: Port
                9600,                                                           #Baud Rate
                serial.PARITY_NONE,                                             #Parity
                serial.EIGHTBITS,                                               #Bytesize
                0,                                                              #Timeout
                serial.STOPBITS_ONE,                                            #Stopbits
                "ADSS-MT"                                                       #Serial Number
                )

D2 = Vacucell("/dev/ttyUSB0",                                                    #Defining the second device parameters: Port
                9600,                                                           #Baud Rate
                serial.PARITY_NONE,                                             #Parity
                serial.EIGHTBITS,                                               #Bytesize
                1,                                                              #Timeout
                serial.STOPBITS_ONE,                                            #Stopbits
                "ADSS-VC"                                                       #Serial Number
                )
MySpecialDevice = D2
                                       
######################################################################

######################################################################
# Publish the BIRTH certificates
######################################################################
def publishBirth():                                                         
    global MySpecialDevice
    publishNodeBirth()
    publishDeviceBirth(MySpecialDevice)
######################################################################

######################################################################
# Publish the NBIRTH certificate
######################################################################
def publishNodeBirth():
    print( "Publishing Node Birth")

    # Create the node birth payload
    payload = sparkplug.getNodeBirthPayload()

    # Set up the Node Controls
    addMetric(payload, "Node Control/Next Server", None, MetricDataType.Boolean, False)
    addMetric(payload, "Node Control/Rebirth", None, MetricDataType.Boolean, False)
    addMetric(payload, "Node Control/Reboot", None, MetricDataType.Boolean, False)

    # Add some regular node metrics (for thr R-PI)
    addMetric(payload, "Node Metric0", None, MetricDataType.String, "hello from the R-Pi node")
    addMetric(payload, "Node Metric1", None, MetricDataType.String,"40.12.154.8")
    addNullMetric(payload, "Node Metric3", None, MetricDataType.Int32)

    # Add a metric with a custom property
    metric = addMetric(payload, "Node Metric2", None, MetricDataType.Int16, 13)
    metric.properties.keys.extend(["engUnit"])
    propertyValue = metric.properties.values.add()
    propertyValue.type = ParameterDataType.String
    propertyValue.string_value = "MyCustomUnits"

    # Publish the node birth certificate
    byteArray = bytearray(payload.SerializeToString())
    client.publish("spBv1.0/" + myGroupId + "/NBIRTH/" + myNodeName, byteArray, 0, False)
######################################################################

######################################################################
# Publish the DBIRTH certificate
######################################################################
def publishDeviceBirth(ConDevice):
    print( "Publishing Device Birth")
    ConDevice.openSerial()
    ConDevice.setMetadata() 
   
    # Get the payload
    payload = sparkplug.getDeviceBirthPayload()
    payload = genPayload(ConDevice.setMetadata())
    # Publish the device birth certificate
    client.publish("spBv1.0/" + myGroupId + "/DBIRTH/" + myNodeName + "/" + ConDevice.deviceID, payload, 0, False)
#####################################################################

######################################################################
# Main Application
######################################################################
print("Starting main application")
# Create the node death payload
deathPayload = sparkplug.getNodeDeathPayload()

# Start of main program - Set up the MQTT client connection
client = mqtt.Client(serverUrl, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

deathByteArray = bytearray(deathPayload.SerializeToString())
client.will_set("spBv1.0/" + myGroupId + "/NDEATH/" + myNodeName, deathByteArray, 0, False)
client.connect(serverUrl, 1883, 60)

# Short delay to allow connect callback to occur
time.sleep(.1)
client.loop()

# Publish the birth certificates
publishBirth()
time.sleep(.1)
client.loop()
n = 1

while True:
    # Periodically publish some new data
    payload = sparkplug.getDdataPayload()

    # Publish a message data
    '''if n % 2 == 0:
        MySpecialDevice = D1
        n += 1
    else:
        MySpecialDevice = D2
        n -= 1'''
        
    payload = genPayload(MySpecialDevice.read())
    client.publish("spBv1.0/" + myGroupId + "/DDATA/" + myNodeName + "/" + MySpecialDevice.deviceID, payload, 0, False)
  
    # Sit and wait for inbound or outbound events
    for _ in range(5):
        time.sleep(1)
        client.loop()
######################################################################