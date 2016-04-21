from flask import Flask, render_template
import gettheweather
app = Flask(__name__)

@app.route("/")
def main():
    # weather = str(getTheWeather())
    print getTheWeather()
    weather = "The weather goes here"
    return render_template('index.html', weather=weather)
    
if __name__ == "__main__":
    app.run()