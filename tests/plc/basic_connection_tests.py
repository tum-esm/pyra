import snap7
from snap7.exceptions import Snap7Exception
import time

plc = snap7.client.Client()

def connect(plc):
    
    start_time = time.time()
    while(True):
        try:
            plc.connect("10.10.0.4", 0, 1)
            time.sleep(0.2)
            
            if time.time()-start_time > 10:
                print("Could not connect to PLC")
                return False
            
            if plc.get_connected():
                print("Connected")
                return True
            
            print("Connection try failed. Retrying.")
            plc.destroy()
            plc = snap7.client.Client()
            
        except Snap7Exception:
            print("PLC connect raied an error.")
            continue


if connect(plc):

    time.sleep(2)

    if plc.get_connected():
        result = plc.db_read(8,0,25)
        print(result)
        time.sleep(0.2)
        result = plc.db_read(25,0,9)
        print(result)
        time.sleep(0.2)
        result = plc.db_read(3,0,5)
        print(result)
        
        
    
plc.disconnect()
plc.destroy()
    
    
