from cs50 import SQL
from helpers import amazon_query, flipkart_query, sendemail, seller
from re import sub
from decimal import Decimal
import time

db = SQL('sqlite:///database.db')

def lookup():
    tmp = db.execute("select * from products")
    for i in tmp:
        product_name = i['product_name']
        desired_price = i['desired_price']
        url = i['url']
        seller_name = seller(url)
        user_id = i['id']

        # Bring in the user email address and his name
        user_info = db.execute('select email, username from users where id = :id', id = user_id)

        # Bring in the current price of the product
        if seller_name == "Amazon":
            tmp_price = amazon_query(url)
        elif seller_name == "Flipkart":
            tmp_price = flipkart_query(url)
        current_price = Decimal(sub(r'[^\d.]', '', tmp_price[0]))
        if desired_price >= current_price:
            sendemail(product_name, current_price, url, user_info[0]["email"], user_info[0]["username"])
            print("Email Sent!")
        else:
            print("Requirements not met!")

while (True):
    lookup()
    time.sleep(20)
