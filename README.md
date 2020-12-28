# CS50 Tracker

A Simple web app tracks tracks prices of e-commerce websites along with Weather and NASA's picture of the day

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need at minimum and how to install them.

Assuming your on linux-based system

1. Python Software (latest version is always recommended)
```
   $ sudo apt-get install python3.8
```
2. Virtual environment module
```
   $ python3 -m pip install --user virtualenv
```

### Installing

A step by step series of examples that tell you how to get a development env running

1. Clone the respiratory using

```
   git clone
```

1. Assuming you're in the cloned directory, Create a virtual environment as below to install

   new modules seperately from system modules

```
   $ python3 -m venv env
```

2. Activate your virtual environment that you have just created
```
   $ source env/bin/activate
```

3. Install the following python modules (aka Libraries)

   (1). Flask Web Framework
   ```
      $ pip3 install Flask
   ```
   Note: If you don't have pip installed refer python documentation to install it.

   (2). cs50, Flask-Session, requests, bs4, smtplib, datetime,
   MIMEMultipart, MIMEText, random
   ```
     $ pip3 install <module-name>
   ```

## Explanation on using and working

   CS50 Tracker basically allows users to

      1. Register

      2. Login

      3. Add Amazon or Flipkart products by adding their url's

      4. Add a Desired price for the product, that the user wants to get notified

         if the price fell down less than or equal to the desired price

      5. Modify the Desired price

      6. Get the Wheather of a city using Openweather's api in the backend

      7. Get the NASA's Picture of the Day using NASA's api in the backend

      8. To Reset the user's password afther verification if the user is not logged in


   There is a webscrap.py script running in the backend that always checks the current prices of the

   products that were added by the users. Basically webscraping the websites by accessing the url's from the database.

   If anytime Current price is less than the Desired price then this webscrap.py script sends
   
   an email to the respective user.

   And the weather is brought by making Openweather api call.

   Finally picture of the day is brought by making Nasa's api call.

## Deployment

Before running the web app, all the api keys and email-id and also email-password has to be

provided as follows:

```
   $ export EMAIL-ID=example@gmail.com
```

```
   $ export EMAIL-PASSWORD=example@password
```

```
   $ export WEATHER_API_KEY='Openweather's_api_key'
```

```
   $ export NASA_API_KEY='Nasa's_api_key'
```

Note: Get the api keys from respective api service provider



## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) - The template engine used
* [Sqlite3](https://www.sqlite.org/index.html) - Used as the database
* [Openweather's_API](https://openweathermap.org/api) - Used for getting weather of a particular city
* [NASA's_API](https://api.nasa.gov/) - Used for getting picture of the day

## License

Open Source

## Acknowledgments

* Hat tip to every online resource that helped me move on when i'm struck building this.
* Thanks to CS50's finance distrubution code.
