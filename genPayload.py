import sys
from genPayload import *

#from trial import genPayload
sys.path.insert(0, "../core/")
#print(sys.path)

import paho.mqtt.client as mqtt
import sparkplug_b as sparkplug

from sparkplug_b import *
# Application Variables
serverUrl = "localhost"
myGroupId = "Sparkplug B Devices"
myNodeName = "Python Edge Node 1"
myDeviceName = "Emulated Device"
publishPeriod = 5000
client = mqtt.Client(serverUrl, 1883, 60)

def genPayload(data):
    #Required dictionary structure for the code to run
    if data is None:                                                                        
        data= {'WeightStatus':dict(Value='S'), 'WeightValue':dict(Value=100,units="g")}
    payload = sparkplug.getDdataPayload()
    
    #Loop structure to capture all the items sent by the connected device dictionary
    for name,output in data.items():
       
        #If the value of the dictionary(passed by the device) is a string, create an appropriate metric
        if type(output['Value']) is str:
            metric=addMetric(payload,name, None, MetricDataType.String,output["Value"])
            
        elif type(output['Value']) is int:
            metric=addMetric(payload,name, None, MetricDataType.Int16,output["Value"])
        
        elif type(output['Value']) is type(None):
            metric=addNullMetric(payload,name, None,MetricDataType.Boolean)
            
        elif type(output['Value']) is bool:
            metric=addMetric(payload,name, None, MetricDataType.Boolean,output["Value"])
           
        elif type(output['Value']) is float:
            metric=addMetric(payload,name, None, MetricDataType.Float,output["Value"])
            
        #If the value of the dictionary is neither string, integer, None, bool or float, print a fail message
        else:
            print("Data type not supported")
        
        #adding the units
        if "Weight_Unit" in output:
            metric.properties.keys.extend(["engUnit"])
            propertyValue = metric.properties.values.add()
            propertyValue.type = ParameterDataType.String
            propertyValue.string_value = output["Weight_Unit"]

        if "ITemp_Unit" in output:
            metric.properties.keys.extend(["engUnit"])
            propertyValue = metric.properties.values.add()
            propertyValue.type = ParameterDataType.String
            propertyValue.string_value = output["ITemp_Unit"]
        
        if "ETemp_Unit" in output:
            metric.properties.keys.extend(["engUnit"])
            propertyValue = metric.properties.values.add()
            propertyValue.type = ParameterDataType.String
            propertyValue.string_value = output["ETemp_Unit"]

        if "Pressure_Unit" in output:
            metric.properties.keys.extend(["engUnit"])
            propertyValue = metric.properties.values.add()
            propertyValue.type = ParameterDataType.String
            propertyValue.string_value = output["Pressure_Unit"]

    # Publish the message data
    print(payload)
    byteArray = bytearray(payload.SerializeToString())
    return byteArray
    
    #client.publish("spBv1.0/" + myGroupId + "/DDATA/" + myNodeName + "/" + myDeviceName,byteArray, 0, False)
  