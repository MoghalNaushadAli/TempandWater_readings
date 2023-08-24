import BAC0
import json
import time
import socket
import datetime

#importing Azure IOT Hub Device Client 
import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

#--------------------------------------------------------------------------------------------#
#------------------------Function to send data to azure cloud--------------------------------#
#---------------If you change the device conn_str needs to be updated----------------------- # 
#--------------------------------------------------------------------------------------------#
# async def SendDataToIotHub(jsonToSend):
    # Fetch the connection string from an environment variable
    #conn_str = "HostName=iothub-cs-ppcaz155.azure-devices.net;DeviceId=wmedge;SharedAccessKey=w4s+z4EhXFlnnPUS20hrmtxHa9PcSmGt3xpAHkE0cUM="
    
    # Create instance of the device client using the connection string
    #device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client.
   # await device_client.connect()

    # Send a single message
    #print("Sending message...")
    #await device_client.send_message(jsonToSend)
    #print("Message successfully sent!")

    # Finally, shut down the client
    #await device_client.shutdown()



#getting VPN ip for connecting to bacnet device

def get_ethernet_ip():
 hostname = socket.gethostname() 
 ipip = socket.gethostbyname(hostname)
 #print(ipip)
 ip_list = socket.getaddrinfo(hostname, None,socket.AF_INET,socket.SOCK_STREAM)

 for ip in ip_list:

  if ip[0] == socket.AF_INET:

   if not ip[4][0].startswith('192.') and not ip[4][0].startswith('169.254.'):

    return ip[4][0]



def get_bacnet_data(bacnet,ip,Meter_ID,name,obj,param_1,param_2,meter_type):
                 readings = bacnet.readMultiple(ip,request_dict=obj)

                 data={}
                 now =datetime.datetime.now()
                 current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                 data['Meter Name']=name
                 data['Meter ID']=Meter_ID
                 data['Parameter Type'] = meter_type
                 data["Time Stamp"]=current_time
                 present_values = []
                 ##########if able to read bacnet data##############
                 if (len(readings)) >= 2: 
                  readings = str(readings)
                  values = eval(readings)
                  

                  for key,value in values.items():
                    for inner_tuple in value:
                     
                     if  inner_tuple[0]=='presentValue'and inner_tuple !=None:
                                            
                           present_values.append((inner_tuple[1])) 
                  val_1 =(present_values[0])
               
                  val_2 = (present_values[1])                           
                    ##########################################################################    
                 else :
                  val_1 = "NA" 
                  val_2 = "NA"                 

                 json_pv = json.dumps((present_values))

                 data[param_1]=val_1
                 data[param_2]=val_2
                 json_data = json.dumps(data,indent=4)
#                 print(json_data)
                 return json_data
                 

def main():
     ethernet_ip = get_ethernet_ip()

     while True:
        bacnet = BAC0.lite(ip=ethernet_ip)
        #taking input from json file for reading present value of each avalogvalue of all ip of bacnet device
        with open("C:/Users/moghalnaushad.baig/Downloads/maininput_v1.json") as input:
            data = json.load(input)
            # Print the type of data variable
            print("Type:", type(data))
#            for key in data.keys():
#                print (key[)
 
            # Print the data of dictionary
#            print("\nData1:", data['Data1'])

            json_temp = str("[")
            

###################### For Main meter #########################            
            for obj in data['Quality']:
                 keys = list(obj.keys())
                 value = list(obj.values())
                 position = value.index('xxxx')

                 param_1= keys[position]
                 position = value.index('yyyy')

                 param_2= keys[position]
                 meter_type = 'Quality'
                 name =(obj['Name'])

                 ip = (obj['address'])
                 Meter_ID = (obj['IP Address'])

                 json_obj = get_bacnet_data(bacnet,ip,Meter_ID,name,obj,param_1,param_2,meter_type)            
                 json_send = json_temp + str(json_obj) + str(",")
                 json_temp = json_send;
             
            json_send = json_send[:-1]
            json_send = json_send + str("]")  
           
            for obj in data['Flow']:
#            for obj in range (0, len(data)):
                 keys = list(obj.keys())
                 value = list(obj.values())
                 position = value.index('xxxx')

                 param_1= keys[position]
                 position = value.index('yyyy')

                 param_2= keys[position]
                 meter_type = 'Flow'

                 name =(obj['Name'])
                 ip = (obj['address'])
                 Meter_ID = (obj['IP Address'])
                 
                 json_obj = get_bacnet_data(bacnet,ip,Meter_ID,name,obj,param_1,param_2,meter_type)
                 json_send = json_temp + str(json_obj) + str(",")
                 json_temp = json_send;


            json_send = json_send[:-1]
            json_send = json_send + str("]")
        
        #send data
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(SendDataToIotHub(json_send))
        
        print(json_send)
        bacnet.disconnect()
        time.sleep(900)
              
             
if __name__ == '__main__':
          
          main()
