import serial
import time

SerialObj = serial.Serial('/dev/ttyACM0', 9600, 8) #, 'N', 1
time.sleep(1)
while True:
    userinput = input("Enter value: ")
    if userinput == 'q':
        break
    tosend = userinput.encode()
    print(tosend)
    SerialObj.write(tosend)


SerialObj.close()      # Close the port