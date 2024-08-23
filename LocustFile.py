import calendar
import datetime
from urllib import response, parse
import uuid
from locust import HttpUser , task , between , SequentialTaskSet , LoadTestShape , TaskSet , log , user , constant, log
import re
import random
from http import HTTPStatus
import yaml
import yaml 
import random
import csv
import pandas as pd
#from cognito_login import login_srp




#Import yaml file containing product data
with open('products.yaml' , 'r') as file:
    data = yaml.safe_load(file)
    
#Function to get random page ID
def get_random_pageID(data):
    products_ids = [item['id'] for item in data]
    page_id = random.choice(products_ids) 
    return parse(page_id)
#Get associated category with ID    
def get_category(page_id) :
    for item in data:
        if str(item['id']) == str(page_id) :
            page_category= item['category']

    return page_category
#Get product name
def get_name(page_id) :
    for item in data:
        if str(item['id']) == str(page_id) :
            product_name= item['name']

    return product_name

#Get price
def get_price(page_id) :
    for item in data:
        if str(item['id']) == str(page_id) :
            product_price= item['price']

    return product_price
    

#Function to load random product page
class scenario_load_random_productpage(SequentialTaskSet) :
    def on_start(self):
        self.userId=str(uuid.uuid4())
    
    @task(1)
    def load_random_page(self):
        theID = get_random_pageID(data)
        theCategory = get_category(theID)
        with self.client.get("/products/id/" +theID, json={"username" : self.userId} , catch_response=True, name="/products/*") as response:
            print(response.status_code)
            
            
            
            

#Function to add product to basket
class scenario_addto_basket(SequentialTaskSet) :
    def on_start(self):
        self.userId=str(uuid.uuid4())
        self.productId = get_random_pageID(data)

    @task(1)
    def load_product(self) :
        self.client.get("/products/id/" + self.productId , name="/products/*")
        print("loading product page")

    @task(2)
    def create_cart(self):
        with self.client.post("/carts" , json={"username" : self.userId} , catch_response=True) as response: # type: ignore
            if response.status_code == 201:
                response.success()
                json_response=response.json()
                self.cart_id=json_response["id"]
                print("initialised")
            else:
                print('FailedToCreateBasket')
                print(response.status_code)
                print(response.text)

    @task(3)
    def add_to_basket(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        future_timestamp =  calendar.timegm(future.timetuple())
        print("another" , self.productId)       
        cart_request = {
            'id': self.cart_id,
            'username': self.userId,# type: ignore
            'ttl': future_timestamp, # type: ignore
            'items': [{
                    "product_id":self.productId,
                    "product_name":get_name(self.productId),
                    "price":get_price(self.productId),
                    "quantity":1
                }]
        }
        
        with self.client.put("/carts/" + self.cart_id , json= cart_request, catch_response=True, name="/carts/*") as response:
            if response.status_code == 200:
                response.success()
                print("YES")
            else:
                response.failure("Could not add to basket")
                print("NO")
                print(response.status_code)
                print(response.text)
                print(response.request)
                print(cart_request)
    @task(3)
    def load_cart(self) :
        self.client.get("/carts/" + self.cart_id , name="/carts/*")


#Function to load test specific 'Brush' search
class scenario_search_page(TaskSet):
    

    @task
    def search_page(self):
        with self.client.get("/search/products?searchTerm=brush&size=25&offset=0" , catch_response=True) as response:
            if response.status_code==200:
                response.success()
                print("Searching through products")
            else:
                print(response.status_code , " ,  Something has gone wrong")



#Checkout load test
class checkout(SequentialTaskSet) :
    def on_start(self):
        self.userId=str(uuid.uuid4())

    
    @task(1)
    def load_product(self) :
        self.client.get("/products/id/" + self.productId , name="/products/*")
        print("loading product page")

    @task(2)
    def create_cart(self):
        with self.client.post("/carts" , json={"username" : self.userId} , catch_response=True) as response: # type: ignore
            if response.status_code == 201:
                response.success()
                json_response=response.json()
                self.cart_id=json_response["id"]
                print("initialised")
            else:
                print('FailedToCreateBasket')
                print(response.status_code)
                print(response.text)
    @task(3)
    def add_to_basket(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        future_timestamp =  calendar.timegm(future.timetuple())
        print("another" , self.productId)       
        cart_request = {
            'id': self.cart_id,
            'username': self.userId,# type: ignore
            'ttl': future_timestamp, # type: ignore
            'items': [{
                    "product_id":self.productId,
                    "product_name":get_name(self.productId),
                    "price":get_price(self.productId),
                    "quantity":1
                }]
        }
        
        with self.client.put("/carts/" + self.cart_id , json= cart_request, catch_response=True, name="/carts/*") as response:
            if response.status_code == 200:
                response.success()
                print("YES")
            else:
                response.failure("Could not add to basket")
                print("NO")
                print(response.status_code)
                print(response.text)
                print(response.request)
                print(cart_request)
    @task(3)
    def load_cart(self) :
        self.client.get("/carts/" + self.cart_id , name="/carts/*")

    @task(3)
    def check_out(self):
        with self.client.post("https://ywdr5m0n0k.execute-api.eu-west-1.amazonaws.com/carts", json={"username" : self.userId} , catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                print("Checkout successfull")
            else:
                response.failure("Checkout failed")
        self.client.cookies.clear()
class assume_persona(SequentialTaskSet):
    def on_start(self):
        self.userId=str(uuid.uuid4())
    @task
    def persona(self):
        with self.client.get("https://pn56wi5ih0.execute-api.eu-west-1.amazonaws.com/users/random", json={"username" : self.userId} , catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print("Successfully assumed a random persona")
            else:
                response.failure("Oops")
#Login load test
# class login_function(SequentialTaskSet):
#     def on_start(self):
#         self.userId=str(uuid.uuid4())
#     wait_time = constant(1)
#     @task
#     def startLogin(self):
#         self.client.cookies.clear()
#         url = "https://d3ifjlvnyf94hl.cloudfront.net/auth"
#         filename ="bulk-user-create/users.csv"
#         data = {"username":"", "email":"", "password":""}

#         df = pd.read_csv(filename)
        
#         randomRow = df.sample(n=1).iloc[0]
#         username = randomRow["username"]
#         password = randomRow["password"]
        
#         # with open(filename, newline="") as csvfile:
#         #     reader = list(csv.DictReader(csvfile))
#         #     i = random.randint(1, 450)
#         #     print(reader[i])
#         #     data = reader[i]
       
       
#         response = login_srp(username, password, "752k3ujqcta9phcdi7o8vcg4di", "6ElEj2uQj")
#         #with self.client.post(login_srp(data["username"], data["password"], "752k3ujqcta9phcdi7o8vcg4di", "6ElEj2uQj"), json={"username" : self.userId} , catch_response=True) as response:
#             # print(response.text)
#         if response["status_code"] == 200:
#             print("Success")
#         else:
#             print("Failure")
#         self.client.get("/", name = self.on_start.__name__)
#         self.client.get("https://pn56wi5ih0.execute-api.eu-west-1.amazonaws.com/users/random")
#         if "id" in response:
#             print("Success")
class user_test_1(HttpUser) :
    wait_time = between(1,2)
    headless=True
    #host = "https://pn56wi5ih0.execute-api.eu-west-1.amazonaws.com"
    host = "https://ywdr5m0n0k.execute-api.eu-west-1.amazonaws.com"
    tasks=[scenario_addto_basket, checkout, scenario_load_random_productpage, assume_persona]






    



