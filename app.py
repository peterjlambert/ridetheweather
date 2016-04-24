from flask import Flask, render_template
import forecastio
from datetime import datetime, timedelta
import datetime
import time
from pytz import timezone
import pytz
import geocoder

app = Flask(__name__)

optLat = 53.9591
optLng = -1.0815
optLocation = "York, UK"
optUnits = 'uk'

def getTheWeather(optLat, optLng, optUnits, club=''):
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
    # ride_time_diff = 123

    def rideTime(): 
        day = whatdayisit()
        current_time = local_datetime
        if club == "vcyork":
            if day == 'Tuesday' or day == 'Thursday':
                ride_time = local_datetime.replace(hour=18, minute=00, second=00)
            elif day == 'Saturday' or day == 'Sunday':
                ride_time = local_datetime.replace(hour=9, minute=00, second=00)
        else:
            ride_time = current_time
        
        ride_time_seconds = ride_time.astimezone(local_timezone).replace(tzinfo=None)
        current_time_seconds = current_time.astimezone(local_timezone).replace(tzinfo=None)
        ride_time_diff = current_time_seconds - ride_time_seconds
        ride_time_diff = ride_time_diff.total_seconds()
        
        if ride_time_diff > 60: 
            ride_time = current_time
        return ride_time

    def rideStart(): 
        day = whatdayisit()
        ride_time = rideTime()     
        current_time = local_datetime
        if ride_time.strftime('%b %d %Y %H:%M:%S') != current_time.strftime('%b %d %Y %H:%M:%S'):   
            if day == 'Tuesday' or day == 'Thursday':
                ride_start = "Today's ride leaves %s from B&Q. " % ride_time.strftime(fmt)
            elif day == 'Saturday' or day == 'Sunday':
                ride_start = "Today's ride leaves %s from the shelter. " % ride_time.strftime(fmt)
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
        return directions[int((bearing+d/2)/d)] 
    
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
            tempDescription = 'a frost-bitey ' + readableTemperature(temp) + '. #stayindoors'
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
        
        
    def showTheWeather():

        theWeather = rideStart()
        theWeather = theWeather + "The forecast is %s and %s" % (weatherSummary, temperature)
        theWeather = theWeather + "The wind will blow from the %s at %s." % (windBearing, strWindSpeed)
        if tailWind:
            theWeather = theWeather + tailWind
        return theWeather

    # Forecast.io API
    api_key = 'f7633fa443a2ce17a8d66a1eb771941e'
    lat = optLat
    lng = optLng
    units = optUnits
    current_time = local_datetime.isoformat()
    ride_time = rideTime()
    forecast = forecastio.load_forecast(api_key, lat, lng, time=ride_time, units=units)

    #Get the weather
    byCurrently = forecast.currently()
    weatherSummary = byCurrently.summary.lower()
    temperature = temp_description(byCurrently.temperature)
    windBearing = winddir_text(byCurrently.windBearing)
    windSpeed = byCurrently.windSpeed
    strWindSpeed = str(int(round(byCurrently.windSpeed))) +  'mph'
    weatherIcon = weather_emoji(byCurrently.icon)
    tailWind = tail_wind(windSpeed, windBearing)
        
    return showTheWeather()
    

############
## Routes ##
############

@app.route("/")
def main():
    location = geocoder.google(optLocation)
    locationLatLng = location.latlng
    locationName = location.city + ', ' + location.country 
    locationLat = locationLatLng[0]
    locationLng = locationLatLng[1]
    weather = getTheWeather(locationLat, locationLng, optUnits)
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=locationName, locationLat=locationLat, locationLng=locationLng)
    
    
@app.route("/location/<location>")
def local(location):
    location = geocoder.google(location)
    locationLatLng = location.latlng
    if location.city:
        locationName = location.city + ', ' + location.country
    elif location.state_long:
        locationName = location.state_long + ', ' + location.country
    elif location.country_long:
        locationName = location.country_long
    else:
        locationName = "" 
        
    locationLat = locationLatLng[0]
    locationLng = locationLatLng[1]
    weather = getTheWeather(locationLat, locationLng, optUnits)
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=locationName, locationLat=locationLat, locationLng=locationLng)
    
    
@app.route("/club/<clubname>")
def club(clubname):
    if clubname == "vcyork":
        location = geocoder.google('York, UK')
    else:
        location = geocoder.google('Paris, France')
    locationLatLng = location.latlng
    locationName = location.city + ', ' + location.country
    locationLat = locationLatLng[0]
    locationLng = locationLatLng[1]
    weather = getTheWeather(locationLat, locationLng, optUnits, clubname)
    charcount = len(weather)
    return render_template('index.html', weather=weather, charcount=charcount, locationName=clubname, locationLat=locationLat, locationLng=locationLng)
    
    
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)