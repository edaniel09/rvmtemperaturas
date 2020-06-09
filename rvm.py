import cv2
import numpy as np
import random
import requests#para llamar el API: usado para mandar requests a cualquier URL

import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

print(available_ports)


def kelvintocelsius(temp):
    return round((temp - 273.15),2)

def temperatura(ciudad):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+ciudad+'&appid=6f5dcd364e5b8af8a4f872eae141fe7d')
    json_res = r.json()
    temp_k = float(json_res['main']['temp'])
    return temp_k

def weather(ciudad):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+ciudad+'&appid=6f5dcd364e5b8af8a4f872eae141fe7d')
    json_res = r.json()
    temp_k = int(np.ceil(kelvintocelsius(json_res['main']['temp'])))
    pressure = int(json_res['main']['pressure'])
    humidity = int(json_res['main']['humidity'])
    windspeed = int(json_res['wind']['speed'])
    #winddirection = int(json_res['wind']['deg'])
    clouds = int(json_res['clouds']['all'])
    temp_list = []
    temp_list.append(temp_k)
    temp_list.append(pressure)
    temp_list.append(humidity)
    temp_list.append(windspeed)
    #temp_list.append(winddirection)
    temp_list.append(clouds)
    return temp_list

def round_up_to_odd(number):
    if(number <= 0):
        return 1
    return int(np.ceil(number) // 2 * 2 + 1)

def filtro_erosion(image, mask):
    mask = round_up_to_odd(mask)
    kernel = np.ones((mask, mask), np.uint8)
    output = cv2.erode(image, kernel, 3)
    return output

def filtro_brillo(image, val):
    return image + val*2

def filtro_blur(image, mask):
    mask = round_up_to_odd(mask)
    return cv2.blur(image, (mask, mask))

def filtro_flickeo(image, val):
    if(val%2):
        image = np.ones((image.shape[0], image.shape[1]), np.uint8)
        return image
    else:
        return image

def filtro_tophat(image, mask):
    mask = round_up_to_odd(mask)
    kernel = np.ones((mask, mask), np.uint8)
    tophat = cv2.morphologyEx(frame, cv2.MORPH_TOPHAT, kernel)
    tophatres = frame*tophat + frame
    return tophatres    

class Info_ciudad:
    def __init__(self, city, temperature, pressure, humidity, windspeed, clouds):
        self.city = city
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.windspeed = windspeed
        #self.winddir = winddir
        self.clouds = clouds

if available_ports:
    midiout.open_port(1)
else:
    midiout.open_virtual_port("My virtual output")


cap = cv2.VideoCapture(0)

kernel = np.ones((5, 5), np.uint8)

iteration = 1
ibefore = -1

infolist = []

#lista de ciudades de las que se obtendra la info meteorologica
ciudades = ["Guayaquil", "Quito", "Ambato", "Brasilia", "Dublin", "Moscow", "Tokyo", "Tripoli", "Cairo", "Tunes", "Nairobi", "Paris",
"Berlin", "Amsterdam", "Bangkok", "Tianjin", "Manila", "Miami", "York", "Caracas", "Bagdad", "Bangui", 
"Damasco", "Brazzaville", "Kinshasa", "Mayak", "Hanford"]
# "Niamey", "Antananarivo",

for ciudad in ciudades:
    
    weatherinfo = weather(ciudad)
    print(ciudad)
    info = Info_ciudad(ciudad, int(weatherinfo[0]), int(weatherinfo[1]), int(weatherinfo[2]), int(weatherinfo[3]), int(weatherinfo[4]))
    infolist.append(info)

_, frame = cap.read()

erosion = filtro_erosion(frame, random.randint(0, 40))
suma = filtro_brillo(frame, random.randint(0, 40))
blurred = filtro_blur(frame, random.randint(0, 40))
tophatres = filtro_tophat(frame, random.randint(0, 40))

counter = 1
indice = 0

inforciudad = ""
ciudadnombre = ""
ciudadtemp = ""
ciudadhum = ""
ciudadnubes = ""
ciudadviento = ""

while(1):

    counter = counter + 1

    """if(counter == 100):
        if(indice+1 == len(infolist)):
            indice = 0
        else:
            indice = indice + 1
            print("Ciudad: "+infolist[indice].city+" Temperatura: "+str(infolist[indice].temperature)+" Humedad: "+str(infolist[indice].humidity)+" Nubes: "+str(infolist[indice].clouds)+" Viento: "
            +str(infolist[indice].windspeed))
        counter = 0"""

    _, frame = cap.read()

    #for item in infolist:
    """weatherinfo = weather(ciudad)
    erosion = filtro_erosion(frame, int(weatherinfo[0]))
    suma = filtro_brillo(frame, int(weatherinfo[0]))
    blurred = filtro_blur(frame, int(weatherinfo[0]))
    flick = filtro_flickeo(frame, random.randint(1, 10))    
    tophatres = filtro_tophat(frame, int(weatherinfo[0]))"""


    suma = filtro_brillo(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), infolist[indice].temperature)
    crop_suma = suma[0:int(suma.shape[0]/2), 0:int(suma.shape[1]/2)]
    crop_sumaS = cv2.resize(crop_suma, (suma.shape[1], suma.shape[0]))
    
    erosion = filtro_erosion(frame, infolist[indice].humidity)
    crop_erosion = erosion[0:int(erosion.shape[0]/2), int(erosion.shape[1]/2):erosion.shape[1]]
    crop_erosionS = cv2.resize(crop_erosion, (erosion.shape[1], erosion.shape[0]))
    
    blurred = filtro_blur(frame, infolist[indice].clouds)
    crop_blurred = blurred[int(blurred.shape[0]/2):blurred.shape[0], 0:int(blurred.shape[1]/2)]
    crop_blurredS = cv2.resize(crop_blurred, (blurred.shape[1], blurred.shape[0]))

    tophatres = filtro_tophat(frame, infolist[indice].windspeed)
    crop_tophat = tophatres[int(tophatres.shape[0]/2):tophatres.shape[0], int(tophatres.shape[1]/2):tophatres.shape[1]]
    crop_tophatS = cv2.resize(crop_tophat, (tophatres.shape[1], tophatres.shape[0]))

    

    if iteration==255:
        iteration = 0


    """cv2.imshow('suma', suma)
    cv2.imshow('erosion', erosion)
    cv2.imshow('blurred', blurred)
    cv2.imshow('tophatres', tophatres)"""

    #cv2.imshow("out", out)
    #row1 = cv2.hconcat([suma, erosion])
    #row2 = cv2.hconcat([blurred, tophatres])
    #final = cv2.vconcat([row1, row2])

    #finalS = cv2.resize(final, (1080, 680))

    row1 = np.concatenate((crop_sumaS, crop_erosionS), axis=1)
    row2 = np.concatenate((crop_blurredS, crop_tophatS), axis=1)
    final = np.concatenate((row1, row2), axis=0)
    finalS = cv2.resize(final, (1380, 820))

    if(counter == 100):
        if(indice+1 == len(infolist)):
            indice = 0
        else:
            indice = indice + 1
            inforciudad = ("Ciudad: "+infolist[indice].city+" Temperatura: "+str(infolist[indice].temperature)+" Humedad: "+str(infolist[indice].humidity)+" Nubes: "+str(infolist[indice].clouds)+" Viento: "+str(infolist[indice].windspeed))
            ciudadnombre = ("Ciudad: "+infolist[indice].city)
            ciudadtemp = ("Temperatura: "+str(infolist[indice].temperature)+ " (Celsius)")
            ciudadhum = ("Humedad: "+str(infolist[indice].humidity) + " (%)")
            ciudadnubes = ("Nubes: "+str(infolist[indice].clouds) + " (%)")
            ciudadviento = ("Viento: "+str(infolist[indice].windspeed) + "Km/s")
            print(inforciudad)
            note_on = [0x90, abs(infolist[indice].temperature) * 3, 112] # channel 1, middle C, velocity 112
            print(note_on)
            midiout.send_message(note_on)

            #cv2.putText(finalS, inforciudad, (int(finalS.shape[1]/2), int(finalS.shape[0]/2) + indice), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        counter = 0
    #cv2.putText(finalS, inforciudad, (int(finalS.shape[1]/2 + 50), int(finalS.shape[0]/2 + 50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    #cv2.putText(finalS, ciudadnombre, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(finalS, ciudadnombre, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(finalS, ciudadtemp, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(finalS, ciudadhum, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(finalS, ciudadnubes, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(finalS, ciudadviento, (int(finalS.shape[1]/2) + 50, int(finalS.shape[0]/2) + 250), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Output", finalS)


    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        cap.release()
        break
    if k == ord('q'):
        print(iteration)
        iteration = iteration + 1


cv2.destroyAllWindows()