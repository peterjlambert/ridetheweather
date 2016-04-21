#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import forecastio
from datetime import datetime, timedelta
import datetime
from pytz import timezone
import pytz
import emoji



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

lat = 53.9591
lng = -1.0815
units = 'uk'

def rideTime(): 
    day = whatdayisit()
    if day == 'Tuesday' or day == 'Thursday':
        ride_time = local_datetime.replace(hour=18, minute=00, second=00)
    elif day == 'Saturday' or day == 'Sunday':
        ride_time = local_datetime.replace(hour=9, minute=00, second=00)
    else:
        ride_time = utcnow()    
    return ride_time


def rideStart(): 
    day = whatdayisit()
    ride_time = rideTime()
    if day == 'Tuesday' or day == 'Thursday':
        ride_start = "Today's ride leaves %s from B&Q." % ride_time.strftime(fmt)
    elif day == 'Saturday' or day == 'Sunday':
        ride_start = "Today's ride leaves %s from the shelter." % ride_time.strftime(fmt)
    else:
        ride_start = 'Riding now?'
    return ride_start


# Forecast.io API
api_key = 'f7633fa443a2ce17a8d66a1eb771941e'
lat = 53.9591
lng = -1.0815
units = 'uk'
current_time = local_datetime.isoformat()
ride_time = rideTime()
forecast = forecastio.load_forecast(api_key, lat, lng, time=ride_time, units=units)


# Format Temperature
def readableTemperature( temp ):
  return '%dC' % (temp)
  
  
# Format compass bearing as textual compass point  
_winddir_text_array = None
def winddir_text(pts):
    "Convert wind direction from 0..15 to compass point text"
    global _winddir_text_array
    if pts is None:
        return None
    #if not isinstance(pts, int):
    pts = int(pts + 0.5) % 16
    if not _winddir_text_array:
        # _ = _Localisation.translation.gettext
        # _ = None
        _winddir_text_array = (
            'North', 'NNE', 'NE', 'ENE',
            'East', 'ESE', 'SE', 'SSE',
            'South', 'SSW', 'SW', 'WSW',
            'West', 'WNW', 'NW', 'NNW',
            )
    return _winddir_text_array[pts]
    
def tail_wind(speed, direction):
    tuesdayTailwinds = ['North', 'WNW', 'NW', 'NNW']
    thursdayTailwinds = ['East', 'ENE', 'ESE', 'SE']
    if whatdayisit() == 'Tuesday' and speed > 7:
        if windBearing in tuesdayTailwinds:
            return 'Tailwind home!'
        else:
            return
    elif whatdayisit() == 'Thursday' and speed > 7:
        if windBearing in thursdayTailwinds:
            return 'Tailwind home!'
        else:
            return
    else:
        return
            
    
    

def temp_description(temp):
    if temp <= 2:
        tempDescription = 'a chilling ' + readableTemperature(temp) + '.'
    elif temp > 2 and temp <= 7:
        tempDescription = "a blummin' nippy " + readableTemperature(temp) + '.'
    elif temp > 7 and temp <= 11:
        tempDescription = "a cheeky " + readableTemperature(temp) + '.'
    elif temp > 11 and temp <= 14:
        tempDescription = "a comfortable " + readableTemperature(temp) + '.'
    elif temp > 14 and temp <= 17:
        tempDescription = "a balmy " + readableTemperature(temp) + '. Shorts!'
    elif temp > 17 and temp <= 21:
        tempDescription = "a toasty " + readableTemperature(temp) + ". #sunsoutgunsout!"
    elif temp > 21 and temp <= 24:
        tempDescription = "a crazy " + readableTemperature(temp)   + '.'  
    elif temp > 24:
        tempDescription = readableTemperature(temp) + '. Wow! Melting tarmac.'
    else:
        tempDescription = readableTemperature(temp) + '.'
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
    
    
    
    

#Get the weather
byCurrently = forecast.currently()
weatherSummary = byCurrently.summary.lower()
temperature = temp_description(byCurrently.temperature)
windBearing = winddir_text(byCurrently.windBearing)
windSpeed = byCurrently.windSpeed
strWindSpeed = str(int(round(byCurrently.windSpeed))) +  'mph'
weatherIcon = weather_emoji(byCurrently.icon)
tailWind = tail_wind(windSpeed, windBearing)

# print "It's %s!" % whatdayisit()
print rideStart()
print "The forecast is %s and %s" % (weatherSummary, temperature)
print "Wind will be %s from the %s." % (strWindSpeed, windBearing)
# print weatherIcon
print tailWind