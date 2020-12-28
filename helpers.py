import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


import requests
from bs4 import BeautifulSoup

import smtplib


from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import random


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"




    ################## My functions ##################



def amazon_query(URL):
    """Use the URL and return values"""
    UserAgentList = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1', 'Mozilla/5.0 (Linux; Android 5.1; AFTS Build/LMY47O) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/41.99900.2250.0242 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.04 Chromium/17.0.963.65 Chrome/17.0.963.65 Safari/535.11']
    headers = {"User-Agent": random.choice(UserAgentList)}

    page = requests.get(str(URL), headers = headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    soup.encode('utf-8')

    product_name = soup.find(id = "productTitle").getText().strip()

    product_price = soup.find(id = "priceblock_ourprice")
    
    if not product_price:
        product_price = soup.find(id = "priceblock_dealprice").getText().strip()
        return product_price, product_name

    return product_price.getText().strip(), product_name

    # Product_name, product_price, product_url, user_email, user_name
def sendemail(string1, string2, string3, string4, string5):
    # Storing the admin email and password
    admin = os.environ.get("EMAIL_ID")
    password = os.environ.get("EMAIL_PASSWORD")

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart()
    msg['Subject'] = "Price drop!"
    msg['From'] = admin
    msg['To'] = string4

    html = """\
           <html>
            <head></head>
                <body>
                    <div><h2>Hey """+string5+""",</h2></div><br></br>
                    <div><p>Price fell down for the product named: """+string1+""".<br>
                    Current price: ₹"""+str(string2)+""".<br>
                    Hurry up!, before price goes up.</p></div><br>
                    <div>Click <a href="""+string3+""">here</a> to check it out.</div>
                    <p>&nbsp;</p>
                </body>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
                <footer>
                <p>Your Sincerely,<br>
                CS50: Tracker</p>
                </footer>
           </html>
           """

    msg.attach(MIMEText(html, "html"))

    # Start the email server and send the otp to the user through email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(admin, password)

    user_email = string4   

    server.sendmail(admin, user_email, msg.as_string())

    server.quit()   

def weather_api(city):

    api_key = os.environ.get("WEATHER_API_KEY")

    urladdress = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+api_key

    # Contact api and get the wheather
    contactapi = requests.get(urladdress)

    apidata = contactapi.json()

    # Error Checking
    if int(apidata["cod"]) == 404:
        return None
    else:
        return apidata
    
def nasa_api(today = "today"):

    api_key = os.environ.get("NASA_API_KEY")

    urladdress = "https://api.nasa.gov/planetary/apod?api_key="+api_key+"&date="+today

    # Contact api and get the picture of the day
    contactapi = requests.get(urladdress)

    apidata = contactapi.json()
    return apidata

def seller(url):
    # Generate a dictionary of the required url's
    urls = {'Amazon': 'https://www.amazon.in',
              'Flipkart': 'https://www.flipkart.com'  ,
              'Myntra': 'https://www.myntra.com'
             }

    # Slice the url provided as per our desired url's size
    url1 = url[0:21]
    url2 = url[0:24]
    url3 = url[0:22]

    # Generate a list with sliced urls's
    url_match =[url1, url2, url3]

    # Iterate through the url's dictionary and get the key
    for i in url_match:
        for key, value in urls.items():
            if i == value:
                return key

def flipkart_query(URL):
    """Use the URL and return values"""
    headers = {"User-Agent":'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}

    page = requests.get(URL, headers = headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    soup.encode('utf-8')

    product_name = soup.find("span", attrs = {"class", "B_NuCI"}).getText().strip()
    product_price = soup.find("div", attrs = {"class", "_30jeq3 _16Jk6d"}).getText().strip()

    return product_price, product_name