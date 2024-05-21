import requests
from datetime import datetime, timezone
import smtplib
import time
import os
from dotenv import load_dotenv

load_dotenv(".env")

# Access the environment variables
from_email = os.getenv('from_email')
password = os.getenv('password')
to_email = os.getenv('to_email')


MY_LAT = 52.070499
MY_LONG = 4.300700

parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0
}


def is_dark():
    # Sunrise and sunset times being gotten from this API
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()

    # convert the sunrise and sunset to strings with HH:MM in the 24h time format
    sunrise_time_str = ":".join(data["results"]["sunrise"].split("T")[1].split(":")[0:2])
    sunset_time_str = ":".join(data["results"]["sunset"].split("T")[1].split(":")[0:2])

    # convert the time strings to datetime objects
    sunrise_time = datetime.strptime(sunrise_time_str, '%H:%M').time()
    sunset_time = datetime.strptime(sunset_time_str, '%H:%M').time()

    # Get current time
    time_now = datetime.now(timezone.utc).time()
    print(time_now)

    # Check if time now is between sunset and sunrise, i.e. it is dark
    return (sunset_time <= time_now) or (time_now <= sunrise_time)


def is_ISS_close():
    # receive ISS location data
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()

    # extract coordinates of ISS at time of call
    iss_longitude = float(response.json()['iss_position']['longitude'])
    iss_latitude = float(response.json()['iss_position']['latitude'])

    # coordinates check with 5 error
    return ((iss_latitude - 5 <= MY_LAT <= iss_latitude + 5) and
            (iss_longitude - 5 <= MY_LONG <= iss_longitude + 5))


while True:

    if is_dark() and is_ISS_close():
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()  # securing the connection, messages sent will be encrypted
            connection.login(user=from_email, password=password)

            message = "The International Space Station just flew above you right now, take a look!"

            connection.sendmail(
                from_addr=from_email,
                to_addrs=to_email,
                msg=f"Subject:ISS is above you now, look!\n\n {message}"
            )

    print("Check performed")
    time.sleep(60)
