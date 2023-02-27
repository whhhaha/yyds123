import sensor, image,time,lcd,image,json
from pyb import UART,Timer,LED
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
EXPOSURE_TIME_SCALE = 2.0
#sensor.set_auto_exposure(False,2000)
#sensor.set_gainceiling(16)
clock = time.clock()
K=5000
lcd.init()
uart = UART(3,115200,8,None,1)
LED_Red = LED(1)
LED_Green = LED(2)
LED_Blue = LED(3)
red_threshold = ( 15, 50, 40, 80, 20, 60)
green_threshold = (77, 99, -68, -24, 33, -21)
yellow_threshold  =  (63, 100, 37, -32, 87, 14)
black_threshold  =(0, 28, -118, 1, -128, 127)
green_number =0
red_number = 0
black_number = 0
color_flag=0
qrnumtime=0
firstcheck=0
clock = time.clock()
tim = Timer(3,freq=1)
tim.deinit()
data = []
Flaghld = 0
hld=0
FlagOK =0
num = 0
returnData = [0x55,0x02,0x92,0x02,0x02,0x00,0x00,0xBB]
runData	= [0x55,0x02,0x92,0x03,0x02,0x00,0x00,0xBB]
show_numTab = ["0","1","2","3","4","5","6","7","8","9"]
def tick(timer):
    global FlagOK,num
    print("Timer callback")
    num = num-1
    if(num == 0):
        num = 2
        FlagOK = 2
        tim.deinit()
def USART_Send(src,length):
    for i in range(length):
        uart.writechar(src[i])
def QR_Check(srcbuf):
    global FlagOK,num,qrnumtime
    date = ""
    if(FlagOK == 1):
        img.draw_string(100, 180,"open"+show_numTab[num],color=[255,0,0])
        for code in img.find_qrcodes():
            FlagOK = 0
            tim.deinit()
            print(code)
            print(clock.fps())
            date += code.payload()+""
            print(date)
            #qr_Tab = code.payload()
        if (FlagOK == 0 ):
            if(qrnumtime<2):
                qrnumtime=qrnumtime+1
                uart.writechar(0x55)
                uart.writechar(0x02)
                uart.writechar(0x92)
                uart.writechar(0x01)
                uart.writechar(len(date))
                for qrdata in date:
                    uart.writechar(ord(qrdata))
                uart.writechar(0xBB)
    if(FlagOK == 2):
        for rdata in returnData:
            uart.writechar(rdata)
        FlagOK = 0
def Color_data(srcbuf):
    global green_number , red_number , black_number , color_flag
    red_threshold2 = (100, 100, -3, 40, 19, -4) #( 15, 50, 40, 80, 20, 60) (62, 51, 29, 100, 0, 91)
    green_threshold2 = (100, 98, -1, 9, 5, 0)#(77, 99, -68, -24, 33, -21)
    black_threshold2  =(0, 28, -118, 1, -128, 127)
    if(color_flag):
        green_blobs = img.find_blobs([green_threshold2])
        red_blobs = img.find_blobs([red_threshold2])
        black_blobs = img.find_blobs([black_threshold2])
        if green_blobs:
            for b in green_blobs:
                green_number = green_number + 1
        if red_blobs:
            for b in red_blobs:
                red_number = red_number + 1
        if black_blobs:
            for b in black_blobs:
                black_number = black_number + 1
        uart.writechar(0x55)
        uart.writechar(0x02)
        uart.writechar(0x0D)
        uart.writechar(green_number)
        uart.writechar(red_number)
        uart.writechar(black_number)
        print(green_number,red_number,black_number)
        green_number =0
        red_number = 0
        black_number = 0
        color_flag=0
def Traffic_light(srcbuf):
    global Flaghld
    threshol = (90, 100, -128, 127, -128, 127)
    if Flaghld:
        img.gaussian(1)
        color = 0
        #red = [(0, 100, 48, 127, -128, 20)]
        #green = [(53, 97, -128, -26, -128, 127)]

        yellow = [(100, 86, -105, -12, -128, 84)]
        green = [(71, 100, -69, -21, 60, -25)]

        if img.find_blobs(yellow):
            color=1
        if img.find_blobs(green):
            color=2
        for blob in img.find_blobs(yellow):
            if blob.density()<0.8 and blob.density()>0.6:
                color=1
        for blob in img.find_blobs(green):
            if blob.density()<0.8 and blob.density()>0.6:
                color=2
        if color == 1 :
            uart.writechar(0x55)
            uart.writechar(0x02)
            uart.writechar(0x0E)
            uart.writechar(0x03)
            print(11)
        elif color == 2 :
            uart.writechar(0x55)
            uart.writechar(0x02)
            uart.writechar(0x0E)
            uart.writechar(0x02)
            print(22)
        else :
            uart.writechar(0x55)
            uart.writechar(0x02)
            uart.writechar(0x0E)
            uart.writechar(0x01)
            print(33)
        Flaghld=0
while(True):
    clock.tick()
    img = sensor.snapshot()
    area=(0,0,160,120)
    if(firstcheck==0):
        uart.writechar(0x12)
        uart.writechar(0x34)
        uart.writechar(0x56)
        uart.writechar(0x78)
        firstcheck=1
    green_number =0
    red_number = 0
    black_number = 0
    if(uart.any()):
        data = uart.read(8)
        if( len(data) >= 8):
            if((data[0] == 0x55)&(data[1] == 0x02)&(data[7] == 0xBB)):
                    if(data[3] == 0x01):
                        if(FlagOK == 0):
                            if(qrnumtime==2):
                                qrnumtime=0
                            FlagOK = 1
                            num = 2
                            print("开始识别")
                            tim.callback(tick)
                    if(data[3] == 0x03):
                        Flaghld=1
                        tim.deinit()
                    if(data[3] == 0x04):
                        for r in img.find_rects(threshold = 10000):
                            area=r.rect()
                            img.draw_rectangle(r.rect(), color = (255, 0, 0))
                    if(data[3] == 0x05):
                        color_flag=1;

    QR_Check(data)
    Color_data(data)
    Traffic_light(data)
    lcd.display(img)
