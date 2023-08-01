import cv2
import numpy as np
from Lib.vidgear.gears import CamGear
import time


def decode (frame):
    b = 0
    qcd = cv2.QRCodeDetector()
    retval, points = qcd.detectMulti(frame)
    if retval:
        if (np.any(points != None)):
            counter_points.append(points)
            masking(retval,counter_points,b)


def masking(retval,points,b):
    if retval:
        for point in counter_points:
           
                for y,x,h,c in point:
                    if int(y[1])-20>=360:
                        print('height out of bounds')
                        break
                    if int(c[0])-20>=1040:
                        print('width out of bounds')
                        break
                    if int(y[1])<=20:
                        print('height out of bounds')
                        break
                    if int(c[0])<=20:
                        print('width out of bounds')
                        break
                    
                    stream_w = int(x[0]-y[0])
                    stream_h = int(c[1]-y[1])
                    streams.append([stream_w,stream_h,y,c])
                    y1 = y
                    
def initialize_first_read(gray):
    
    qcd = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(gray)
    if retval:
        print (decoded_info)
        decoded = str(decoded_info[0])
        print (decoded)
        if decoded.startswith('https:'):
            return decoded
        else:
            return False      
def create_stream(check):
     options = {"STREAM_RESOLUTION": "480p"} 
     stream = CamGear(source=check, stream_mode = True, logging=True,**options).start()
     return stream 
 
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
Video_h1 = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
Video_w1 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
code_test= []
counter_points = []
streams = []
name = 'title'
k =0
b = 0
count = 0

is_stream = False
cv2.namedWindow(name, cv2.WINDOW_FREERATIO)
while True:
    r, frame = cap.read()
    fps_counter = (time.time())
    
    if r:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if is_stream == False:
            check = initialize_first_read(gray)
            test = gray
            if check:
                stream = create_stream(check)
                is_stream = True
            print (is_stream)
        if is_stream == True: 
            video = stream.read()
            video = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
            test = gray 
            decode(gray)
            for stream_w, stream_h,y,c in streams:
                if stream_w>0 and stream_h >0 :
                        resize = cv2.resize(video,(stream_w,stream_h))
                            
                        big_size = np.lib.pad(resize, ((int(y[1]),((Video_h1-stream_h)-(int(y[1])))),(int(c[0]),((Video_w1-stream_w)-int(c[0])))), 'constant', constant_values=(0))
                        
                        count = count + 1  
                        if k == 0:
                            y1 =y
                            c1 =c
                            big_start = big_size
                            big_counter = big_size
                            k= 1
                        if y1[0]- y[0] >10 or y1[1]- y[1] >10 :
                            
                            big_counter = cv2.add(big_size, big_start,big_counter)
                        else:
                            big_counter = big_size
                        test = np.where(big_counter == 0,gray,big_counter)
                        cv2.imshow("mask",big_counter)
                        if count == 20:
                            count= 0
                            streams = []
                            k = 0
                            big_counter = []
                            counter_points = []
                        y1 =y
                        c1 =c
        cv2.imshow(name, test) 
    if cv2.waitKey(30)==ord('c'):
         is_stream = False
    if cv2.waitKey(30)==ord('q'):
        break
    print ("FPS: ", 1.0 / (time.time() - fps_counter))
cv2.destroyAllWindows()
cap.release()
stream.stop()
                