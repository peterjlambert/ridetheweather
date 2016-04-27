from __future__ import print_function # In python 2.7
import sys
from flask import Flask, render_template
import forecastio
from datetime import datetime, timedelta
import datetime
import time
from pytz import timezone
import pytz
import geocoder
import random

app = Flask(__name__)

# Returns the UTC date
def utcnow():
    return datetime.datetime.now()

def whatdayisit():
    now = utcnow()
    return now.strftime("%A")

fmt = '%-I%p'
local_timezone = timezone('GMT')
local_datetime = local_timezone.localize(utcnow())
local_datetime_readable = local_timezone.localize(utcnow()).strftime(fmt)

def rideTime(club): 
    day = whatdayisit()
    current_time = local_datetime
    ride_time = current_time
    if club == "vcyork":
        if day == 'Tuesday' or day == 'Thursday':
            ride_time = local_datetime.replace(hour=18, minute=00, second=00)
        elif day == 'Saturday' or day == 'Sunday':
            ride_time = local_datetime.replace(hour=9, minute=00, second=00)
    
    ride_time_seconds = ride_time.astimezone(local_timezone).replace(tzinfo=None)
    current_time_seconds = current_time.astimezone(local_timezone).replace(tzinfo=None)
    ride_time_diff = current_time_seconds - ride_time_seconds
    ride_time_diff = ride_time_diff.total_seconds()
    
    print(ride_time, file=sys.stderr)
    
    if ride_time_diff > 60: 
        ride_time = current_time
    return ride_time

def getRandomLocation():
    magic_locations = ['Tourmalet, France', 'Gavia, Italy', 'Roubaix Velodrome, Belgium', 
                       "L'Alpe d'Huez, France", 'Mont Ventoux, France', 
                       'Col du Galibier, France', 'Tan Hill, UK', 'Buttertubs, UK', 
                       'Holme Moss, UK', 'Rosedale Chimney, UK', 'Liege, Belgium']
    return random.choice(magic_locations)

optLat = 53.9591
optLng = -1.0815
optLocation = getRandomLocation()
optUnits = 'uk'



def getTheWeather(optLat=optLat, optLng=optLng, optUnits=optUnits, optStartTime=None, optStartLocationName='', club=''):
    

    def rideStart(): 
        ride_start = ''
        if optStartTime and club:
            day = whatdayisit()
            ride_time = optStartTime
            rideStartLocationName = optStartLocationName 
            current_time = local_datetime 
            
            if ride_time.strftime('%b %d %Y %H:%M:%S') != current_time.strftime('%b %d %Y %H:%M:%S'):   
                if day == 'Tuesday' or day == 'Thursday':
                    ride_start = "Today's ride: %s from B&Q. " % ride_time.strftime(fmt)
                elif day == 'Saturday' or day == 'Sunday':
                    ride_start = "Today's ride: %s from the shelter. " % ride_time.strftime(fmt)
        else:
            ride_start = 'Riding now? '
        return ride_start
        

     # Format Temperature
    def readableTemperature( temp ):
        return '%dC' % (temp)
   
   
    # Format compass bearing as textual compass point  
    directions = ["N", "NNE", "ENE", "E", "ESE", "SSE", "S", "SSW", "WSW", "W", "WNW", "NNW"]
    def bearing_to_direction(bearing):
        d = 360. / 12.
        return directions[int(((bearing+d/2)/d)-1)] 
    
    def winddir_text(pts):
        "Convert wind direction from 0..15 to compass point text"        
        if pts is None:
            return None
        wind_direction = bearing_to_direction(pts)
                
        return wind_direction
        
    def tail_wind(speed, direction):
        tuesdayTailwinds = ['North', 'WNW', 'NW', 'NNW']
        thursdayTailwinds = ['East', 'ENE', 'ESE', 'SE']
        if whatdayisit() == 'Tuesday' and speed > 7:
            if windBearing in tuesdayTailwinds:
                return ' Tailwind home!'
            else:
                return
        elif whatdayisit() == 'Thursday' and speed > 7:
            if windBearing in thursdayTailwinds:
                return ' Tailwind home!'
            else:
                return
        else:
            return

    def temp_description(temp):
        if temp <= 2:
            tempDescription = 'a frost-bitey ' + readableTemperature(temp) + '. #stayindoors! '
        elif temp > 2 and temp <= 7:
            tempDescription = "a blummin' nippy " + readableTemperature(temp) + '. '
        elif temp > 7 and temp <= 11:
            tempDescription = "a cheeky " + readableTemperature(temp) + '. '
        elif temp > 11 and temp <= 14:
            tempDescription = "a comfortable " + readableTemperature(temp) + '. '
        elif temp > 14 and temp <= 17:
            tempDescription = "a balmy " + readableTemperature(temp) + '. Shorts! '
        elif temp > 17 and temp <= 21:
            tempDescription = "a toasty " + readableTemperature(temp) + ". #sunsoutgunsout! "
        elif temp > 21 and temp <= 24:
            tempDescription = "a crazy " + readableTemperature(temp)   + '.'  
        elif temp > 24:
            tempDescription = readableTemperature(temp) + '. Wow! Melting tarmac. '
        else:
            tempDescription = readableTemperature(temp) + '. '
        return tempDescription

    def weather_emoji(icon):
        if icon == 'clear-day':
            weatherIcon = ':sunny:'
        elif icon == 'clear-night': 
            weatherIcon = ':crescent_moon:'
        elif icon == 'rain': 
            weatherIcon = ':rain:'
        elif icon == 'snow': 
            weatherIcon = ':snowman:'
        elif icon == 'sleet': 
            weatherIcon = ':snow:'
        elif icon == 'wind': 
            weatherIcon = ':dash:'
        elif icon == 'fog': 
            weatherIcon = ':tea:'
        elif icon == 'cloudy': 
            weatherIcon = ':cloud:'
        elif icon == 'partly-cloudy-day': 
            weatherIcon = ':partly_sunny:'
        elif icon == 'partly-cloudy-night': 
            weatherIcon = ':crescent_moon: :cloud:'
        else:
            weatherIcon = ''
        return weatherIcon
        
        
    def showTheWeather(tailWind=None):
        theWeather = rideStart()
        theWeather = theWeather + "The forecast is %s and %s" % (weatherSummary, temperature)
        theWeather = theWeather + "Wind is from the %s at %s." % (windBearing, strWindSpeed)
        if tailWind:
            theWeather = theWeather + tailWind
        return theWeather

    # Forecast.io API
    api_key = 'f7633fa443a2ce17a8d66a1eb771941e'
    lat = optLat
    lng = optLng
    units = optUnits
    current_time = local_datetime
    if optStartTime:
        ride_time = optStartTime
    else:
        rideTime = current_time
    forecast = forecastio.load_forecast(api_key, lat, lng, time=ride_time, units=units)

    #Get the weather
    byCurrently = forecast.currently()
    weatherSummary = byCurrently.summary.lower()
    temperature = temp_description(byCurrently.temperature)
    windBearing = winddir_text(byCurrently.windBearing)
    windSpeed = byCurrently.windSpeed
    strWindSpeed = str(int(round(byCurrently.windSpeed))) +  'mph'
    weatherIcon = weather_emoji(byCurrently.icon)
    tailWind = None
    if club == 'vcyork':
        tailWind = tail_wind(windSpeed, windBearing)
        
    return showTheWeather(tailWind=tailWind)
    
        
def getLatLng(location):
    location = geocoder.google(location)
    
    if location.city:
        locationName = location.city + ', ' + location.country
    elif location.state_long:
        locationName = location.state_long + ', ' + location.country
    elif location.country_long:
        locationName = location.country_long
    else:
        locationName = ""
    
    locationLatLng = location.latlng 
    if locationLatLng:
        locationLat = locationLatLng[0]
        locationLng = locationLatLng[1]
        return (locationName, locationLat, locationLng);
    else: 
        location = getLatLng(getRandomLocation())
        return (location[0], location[1], location[2])   

############
## Routes ##
############

@app.route("/")
def main():
    location = getLatLng('York, UK')
    weather = getTheWeather(location[1], location[2], optUnits, local_datetime)
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=location[0], locationLat=location[1], locationLng=location[2])
    
    
@app.route("/location/<location>")
def local(location):
    location = getLatLng(location)
    weather = getTheWeather(location[1], location[2], optUnits, local_datetime)
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=location[0], locationLat=location[1], locationLng=location[2])
    
    
@app.route("/club/<clubname>")
def club(clubname):
    if clubname == "vcyork":
        location = getLatLng('York, UK')
        startLocation = "B&Q"
        startTime = rideTime(clubname)
        weather = getTheWeather(location[1], location[2], optUnits, startTime, startLocation, clubname)  
    else:
        location = getLatLng(getRandomLocation())
        weather = getTheWeather(location[1], location[2], optUnits, local_datetime)
    
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=location[0], locationLat=location[1], locationLng=location[2])
    
    
@app.errorhandler(404)
def page_not_found(e):
    location = getLatLng(getRandomLocation())
    weather = getTheWeather(location[1], location[2], optUnits, local_datetime)
    charcount = len(weather)
    return render_template('error.html', weather=weather, charcount=charcount, locationName=location[0], locationLat=location[1], locationLng=location[2]), 404
    
@app.errorhandler(500)
def server_error(e):
    location = getLatLng(getRandomLocation())
    weather = getTheWeather(location[1], location[2], optUnits, local_datetime)
    charcount = len(weather)
    return render_template('error.html', weather=weather, charcount=charcount, locationName=location[0], locationLat=location[1], locationLng=location[2]), 500
    
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)