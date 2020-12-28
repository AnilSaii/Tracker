import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd, amazon_query, weather_api, nasa_api, seller, flipkart_query

import datetime

import random

import smtplib

import requests

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Make sure API Keys, email, password is set

if not os.environ.get("WEATHER_API_KEY") or not os.environ.get("NASA_API_KEY") or not os.environ.get("EMAIL_ID") or not os.environ.get("EMAIL_PASSWORD"):
    raise RuntimeError("All the Credentials were not provided.")



@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Bring the url's list of dictionaries
    details = db.execute("SELECT url FROM products WHERE id = :id ORDER BY product_id DESC", id = session["user_id"])
    empty_list = []
    if details == empty_list:
        return render_template("welcome.html")

    for i in details:
        # Access the url of the product
        url = i["url"]
        # Determine the seller name and call the respective function
        seller_site = seller(url)
        if seller_site == "Amazon":
            amazon_queryList = amazon_query(url)
            actual_price = amazon_queryList[0]
        elif seller_site == "Flipkart":
            flipkart_queryList = flipkart_query(url)
            actual_price = flipkart_queryList[0]

        # Update the products table with the current information that the function brings
        db.execute("UPDATE products SET actual_price = :actual_price WHERE url = :url AND id = :id", actual_price = actual_price, url = url, id = session["user_id"])

        # Bring the updated list of dictionaries
        updated_details = db.execute("SELECT * FROM products WHERE id = :id ORDER BY product_id DESC", id = session["user_id"])
        return render_template("index.html", updated_details = updated_details)


@app.route("/history")
@login_required
def history():
    # Check wheather the user email is verified
    email = db.execute("SELECT status FROM users WHERE id = :id", id = session["user_id"])
    if email[0]["status"] == "no":
        return redirect("/otp")


    """Show history of transactions"""
    tmplist = db.execute("SELECT * FROM history WHERE id = :id ORDER BY timestamp DESC", id = session["user_id"])
    return render_template("history.html", tmplist = tmplist)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("password(config)"):
            return apology("must enter password again", 403)

        elif request.form.get("password") != request.form.get("password(config)"):
            return apology("passwords should match", 403)

        # Query database for username
        rows0 = db.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username is not taken
        if rows0:
            return apology("Sorry, Username has taken", 403)

        # Register the user
        db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)", username = request.form.get("username"), hash = generate_password_hash(request.form.get("password")), email = request.form.get("email"))

        # Send the user to the login page
        return redirect("/login")


        ########################"""Routes that i added"""##########################

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Check wheather the user email is verified
    email = db.execute("SELECT status FROM users WHERE id = :id", id = session["user_id"])
    if email[0]["status"] == "no":
        return redirect("/otp")

    
    """Add the product details"""
    if request.method == "GET":
        return render_template("add.html")
    
    else:
        # Error Checking
        if not request.form.get("url"):
            return apology("Url must be provided", 404)

        if not request.form.get("price"):
            return apology("Amount must be provided", 404)

        if int(request.form.get("price")) < 1:
            return aplology("Invalid amount", 404)

        result = db.execute("SELECT url FROM products WHERE id = :id", id = session["user_id"])
        for i in result:
            if i["url"] == request.form.get("url"):
                return apology("Product already added", 404)

        # Bring the Seller name and call the respective function
        seller_name = seller(request.form.get("url"))
        if seller_name == "Amazon":
            queryList = amazon_query(request.form.get("url"))
        elif seller_name == "Flipkart":
            queryList = flipkart_query(request.form.get("url"))

        # Insert everything about the product into products table
        db.execute("INSERT INTO products (product_name, url, actual_price, desired_price, seller, id) VALUES (:product_name, :url, :actual_price, :desired_price, :seller, :id)", product_name = queryList[1], url = request.form.get("url"), actual_price = queryList[0], desired_price = request.form.get("price"), seller = seller_name, id = session["user_id"])

        # Insert everything about the product into history table for history purposes
        db.execute("INSERT INTO history (product_name, desired_price, timestamp, seller, id) VALUES (:product_name, :desired_price, :timestamp, :seller, :id)", product_name = queryList[1], desired_price = request.form.get("price"), seller = seller_name, timestamp = datetime.datetime.now(), id = session["user_id"])

        flash("Item added successfully!")

        return redirect("/")



@app.route("/otp", methods = ["GET", "POST"])
@login_required
def otp():
    if request.method == "GET":
        # Get the user email address and render a template for otp
        email = db.execute("SELECT email FROM users WHERE id = :id", id = session["user_id"])
        email_address = email[0]["email"]
        return render_template("otp.html", email = email_address)

    else:
        # If user opts to verify his email, generate an otp and send to his email address

        # Storing the admin email and password
        admin = os.environ.get("EMAIL_ID")
        password = os.environ.get("EMAIL_PASSWORD")

        # Get the user email address
        email = db.execute("SELECT email FROM users WHERE id = :id", id = session["user_id"])
        user_email = email[0]["email"]

        # Generate a four digit random number for otp
        random_number = random.randint(100000, 999999)

        # Store the random number in the database
        db.execute("UPDATE users SET otp = :otp WHERE id = :id", otp = generate_password_hash(str(random_number)), id = session["user_id"])

        # Start the email server and send the otp to the user through email
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(admin, password)

        subject = 'OTP Request'
        body = 'your otp for activating your account is '+ str(random_number)
        msg = f'subject: {subject}\n\n{body}'

        server.sendmail(admin, user_email, msg)

        server.quit()

        # Redirect the user to the verify route
        return redirect("/verify")



@app.route("/verify", methods = ["GET", "POST"])
@login_required
def verify():
    if request.method == "GET":
        verify = db.execute("SELECT email FROM users WHERE id = :id", id = session["user_id"])
        email = verify[0]["email"]
        return render_template("verify.html", email = email)
    else:
        # Bring in the user OTP
        otp = request.form.get("otp")

        # Bring in the otp stored in the database
        data_base = db.execute("SELECT otp FROM users WHERE id = :id", id = session["user_id"])
        database_otp = data_base[0]["otp"]

        # Compare wheather they both match
        if check_password_hash(database_otp, otp):

            # Update the user status column to yes
            db.execute("UPDATE users SET status = :status WHERE id = :id", status = "yes", id = session["user_id"])

            # Flash a email verified message
            flash("email verified successfully!")

            # Redirect user to the index page
            return redirect("/")

        else:
            # Return an apology
            return apology("Sorry, OTP isn't seems to be right.", 403)



@app.route("/resetpswd", methods = ["GET", "POST"])
@login_required
def resetpswd():
    """Reset user password"""
    if request.method == "GET":
        verify = db.execute("SELECT email FROM users WHERE id = :id", id = session["user_id"])
        email = verify[0]["email"]
        return render_template("resetpswd.html", email = email)

    else:
        password = request.form.get("password")
        password_config = request.form.get("password(config)")

        # Error Checking.
        if not password:
            return apology("Must provide password", 404)

        if not password_config:
            return apology("Must provide password again", 404)
        
        if password != password_config:
            return apology("Passwords didn't match", 404)

        # Update new password into the users table.
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = generate_password_hash(password_config), id = session["user_id"])

        return redirect("/login")



@app.route("/forgotpswd", methods = ["GET", "POST"])
def forgetpswd():
    """Verify the user and redirect him to the resetpswd route"""
    if request.method == "GET":
        return render_template("forgetpswd.html")

    else:
        # Get the user's email and username and check if exists
        username = request.form.get("username")
        if not username:
            return apology("Username must be provided", 404)
        email = request.form.get("email")
        if not email:
            return apology("Email Address must be provided", 404)
        
        # Check against the database for the username and email
        database = db.execute("SELECT id FROM users WHERE username = :username AND email = :email", username = username, email = email)
        if len(database) != 1:
            return apology("Invalid Username and Email Address", 404)

        return render_template("requestotp.html", email = email, id = database)


@app.route("/forgotpswdotp/<int:user_id>", methods = ["POST"])
def forgotpswdotp(user_id):
    if request.method == "POST":
        # Storing the admin email and password
        admin = os.environ.get("EMAIL_ID")
        password = os.environ.get("EMAIL_PASSWORD")

        # Get the user email address
        email = db.execute("SELECT email FROM users WHERE id = :id", id = user_id)
        user_email = email[0]["email"]

        # Generate a four digit random number for otp
        random_number = random.randint(100000, 999999)

        # Store the random number in the database
        db.execute("UPDATE users SET otp = :otp WHERE id = :id", otp = generate_password_hash(str(random_number)), id = user_id)

        # Start the email server and send the otp to the user through email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(admin, password)

        subject = 'Password Reset'
        body = 'your otp for resetting your passworrd is '+ str(random_number)+'.'
        msg = f'subject: {subject}\n\n{body}'

        server.sendmail(admin, user_email, msg)

        server.quit()

        database = {}
        database["id"] = user_id

        # Redirect the user to the verify route
        return render_template("forgotpswdverify.html", id = database, email = user_email)



@app.route("/forgotpswdverify/<int:user_id>", methods = ["GET", "POST"])
def forgotpswdverify(user_id):
    if request.method == "GET":
        verify = db.execute("SELECT email FROM users WHERE id = :id", id = user_id)
        email = verify[0]["email"]
        return render_template("resetpswdverify.html", email = email)
    else:
        # Bring in the user OTP
        otp = request.form.get("otp")

        # Bring in the otp stored in the database
        data_base = db.execute("SELECT otp FROM users WHERE id = :id", id = user_id)
        database_otp = data_base[0]["otp"]

        # Compare wheather they both match
        if check_password_hash(database_otp, otp):

            # Flash a email verified message
            flash("email verified successfully.")

            database = {}
            database["id"] = user_id

            # Redirect user to the index page
            return render_template("forgotresetpswd.html", id = database)

        else:
            # Return an apology
            return apology("Sorry, OTP isn't seems to be right.", 403)

@app.route("/forgotresetpswd/<int:user_id>", methods = ["GET", "POST"])
def forgotresetpswd(user_id):
    if request.method == "POST":
        """Reset user password"""
        password = request.form.get("password")
        password_confirm = request.form.get("password(confirm)")

        # Error Checking.
        if not password:
            return apology("Must provide password", 404)

        if not password_confirm:
            return apology("Must provide password again", 404)
        
        if password != password_confirm:
            return apology("Passwords didn't match", 404)

        # Update new password into the users table.
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = generate_password_hash(password_confirm), id = user_id)

        return redirect("/login")

@app.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete(product_id):
    if request.method == "POST":
        db.execute("DELETE FROM products WHERE product_id = :product_id", product_id = product_id)
        flash('Item deleted Successfully!')
        return redirect("/")


@app.route("/weather", methods = ["GET", "POST"])
@login_required
def wheather():
    if request.method == "GET":
        return render_template("weather.html")
    else:
        # Bring in the city name
        city_name = request.form.get("city")
        if not city_name:
            return apology("City name must be provided", 404)

        city_weather = weather_api(city_name)

        # Error Checking
        if city_weather == None:
            return apology("Sorry, We couldn't get the details. Please enter a nearby city name instead.", 404)
        else:
            return render_template("weather_response.html", city_weather = city_weather)


@app.route("/nasa", methods = ["GET", "POST"])
@login_required
def nasa():
    if request.method == "GET":
        return render_template("astrology.html")
    else:
        today = request.form.get("date")
        apidata = nasa_api(today)
        if len(apidata) == 3:
            return apology("Not yet decided!")
        tmp = "copyright"
        if not tmp in apidata:
            apidata["copyright"] = "NASA"
        return render_template("pod.html", apidata = apidata)


@app.route("/modify/<int:product_id>", methods = ["GET", "POST"])
@login_required
def modify(product_id):

    if request.method == "GET":
        tmpdict = db.execute("SELECT * FROM products WHERE product_id = :product_id", product_id = product_id)
        return render_template("modify.html", product_id = product_id, tmpdict = tmpdict)
    else:
        # Get the desired price and update the database
        if request.form.get("price") == None:
            return apology("Desired price can't be empty")
        desired_price = request.form.get("price")
        db.execute("UPDATE products SET desired_price = :desired_price WHERE product_id = :product_id", desired_price = desired_price, product_id = product_id)
        tmplist = db.execute("SELECT product_name, seller FROM products WHERE product_id = :product_id", product_id = product_id)
        db.execute("INSERT INTO history(product_name, desired_price, timestamp, seller, id) VALUES (:product_name, :desired_price, :timestamp, :seller, :id)", product_name = tmplist[0]["product_name"]+" (Modified)", desired_price = desired_price, timestamp = datetime.datetime.now(), seller = tmplist[0]["seller"], id = session["user_id"])
        flash("Modified Successfully!")
        return redirect("/")


        

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
    
