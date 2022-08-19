#Attributes to be considered for any given device
#Port       #Baud Rate       #Parity      #Bytesize       #Timeout        #Stopbits

from dataclasses import dataclass
from datetime import datetime
from genPayload import genPayload 
import serial
import re

@dataclass                                                                      #Class definition that takes in device name, port #, baudrate, ...
class Device:
    port: str
    baudrate: int
    parity: str
    bytesize: int
    timeout: int
    stopbits: int
    deviceID: str

    def openSerial(self):                                                       #Helper function to help connect the device to the node(Raspberry pi)
        self.ser = serial.Serial(port = self.port,                              #Variable to map the device attributes                    
                                 baudrate =  self.baudrate,                     #to the serial and self.ser globalizes the scope     
                                 parity = self.parity, 
                                 bytesize = self.bytesize, 
                                 timeout = self.timeout
                                 )          
@dataclass
class MT_Balance(Device):                                                       #Class definition, custom for the MT weight balance
    
    def read(self):                                                             #Helper function to read and send data from balance to console
        
        Weight_Return = {"Weight_Status": {"Value": "Default"},                 #Dictionary to store the instantaneous Balance parameters
                         "Weight_Value" : {"Value": 99999 ,
                         "Weight_Unit" : "Default"}}                            #Includes Dynamic/Static(S/D) status, decimal weight and units
        
        self.ser.write("SI\n".encode('Ascii'))                                  #Prompt the Weight Balance to send data  
      
        ReceiveStr = self.ser.readline()                                        #Receive the line feed from MT-Balance
        DecodedStr = ReceiveStr.decode("Ascii")                                 #Read a single character at a single time:  receive = ser.read() 
                                                                                #Decode the string in Ascii
              
        pattern = re.compile(r"^\w\w?\s(?P<WeightStatus>\w)\s+(?P<WeightValue>\-?\d+\.\d+)\s+(?P<WeightUnit>\w+)")
        #S S --------.-- --                                                     (Reads new line feed as well)
        #1 S/D   Mass   Unit                                                    Sample pattern(S S 12345678.90 g)
        #
        #pattern = re.compile(r"S\s[SD]\s*([+-]?\d+\.\d+)\s*.g")                Substitute pattern for reference: regex101
        
        RegCheck = re.search(pattern, DecodedStr)                               #Checks the decoded string to match with desired REGEX pattern
        
        if RegCheck is not None:                                                #If the REGEX pattern finds a match
            
            Weight_Return["Weight_Status"]["Value"] = RegCheck["WeightStatus"]  #Store respectives values in the dictionary
            Weight_Return["Weight_Value"]["Value"] = float(RegCheck["WeightValue"])
            Weight_Return["Weight_Value"]["Weight_Unit"] = RegCheck["WeightUnit"]
     
        return Weight_Return                                                    #Return the value of the dictionary
                                                                         
    def setMetadata(self, make = "Mettler-Toledo", model = "PG5002-S", sernum = "undefined"):
        
        self.Metadata = {"Make" : {"Value": make},                              #Dictionary to store the initial profile of Balance parameter
                         "Model" : {"Value": model},                            #Includes make and model of the device
                         "Serial Number":{"Value": sernum},                     #Serial Number
                         "Weight_Status": {"Value": "Default"},                 #Dynamic/Static(S/D) status, 
                         "Weight_Value" : {"Value": 99999 ,                     #Decimal weight
                         "Weight_Unit" : "Default"}}                            #and Units
        return self.Metadata

@dataclass
class Vacucell(Device):                                                         #Class definition, custom for the MT weight balance
    
    def read(self):                                                             #Helper function to read and send data from balance to console
        
        Metric_Return = {"Internal_Temp": {"Value": 99999,
                                           "ITemp_Unit" : "C" },                 #Dictionary to store the instantaneous Balance parameters
                         "External_Temp": {"Value": 99999,
                                           "ETemp_Unit" : "C"} ,
                         "Pressure":      {"Value" : 99999,
                                           "Pressure_Unit" : "Default"}}         #Includes Dynamic/Static(S/D) status, decimal weight and units
        
        ReceiveStr = self.ser.readline()                                        #Receive the line feed from MT-Balance
        DecodedStr = ReceiveStr.decode("Ascii")                                 #Read a single character at a single time:  receive = ser.read() 
                                                                                       #Decode the string in Ascii
        pattern_1 = re.compile(r"\((?P<LineCheck>1)\) (?P<InternalTemp>\-?\d+\.\d+)\[C\s+(\d?\d\:\d\d) (\d?\d)\.(\d\d)")
        #(1) 20.4[C 13:51 23.06 
        pattern_a = re.compile(r"\((?P<LineCheck>a)\) (?P<ExternalTemp>\-?\d+\.\d+)\[C\s+(?P<Pressure>\-?\d+\.\d+)(?P<PressureUnit>\w+)")
        #(a) 20.1[C  989.1mBar
       
        RegCheck_1 = re.search(pattern_1, DecodedStr) 
                                     #Checks the decoded string to match with desired REGEX pattern
        RegCheck_a = re.search(pattern_a, DecodedStr)
                
        if RegCheck_1 is not None and RegCheck_1["LineCheck"] == "1":                                                #If the REGEX pattern finds a match
            Metric_Return["Internal_Temp"]["Value"] = float(RegCheck_1["InternalTemp"])  #Store respectives values in the dictionary
            
        if RegCheck_a is not None and RegCheck_a["LineCheck"] == "a":                                                #If the REGEX pattern finds a match
            Metric_Return["External_Temp"]["Value"] = float(RegCheck_a["ExternalTemp"])  #Store respectives values in the dictionary
            Metric_Return["Pressure"]["Value"] = float(RegCheck_a["Pressure"])
            Metric_Return["Pressure"]["Pressure_Unit"] = RegCheck_a["PressureUnit"]
     
        return Metric_Return                                                    #Return the value of the dictionary
                                                                         
    def setMetadata(self, make = "BMT_Medical", model = "55-ECO", sernum = "undefined"):
        
        self.Metadata = {"Make" : {"Value": make},                              #Dictionary to store the initial profile of Balance parameter
                         "Model" : {"Value": model},                            #Includes make and model of the device
                         "Serial Number":{"Value": sernum},                              #Serial Number
                         "Internal_Temp":{"Value": 99999,
                                          "ITemp_Unit" : "C" },
                         "External_Temp":{"Value": 99999,
                                          "ETemp_Unit" : "C" },                             #Decimal weight
                         "Pressure":     {"Value": 99999,
                                          "Pressure_Unit" : "Default"}}                                     #and Units
        return self.Metadata