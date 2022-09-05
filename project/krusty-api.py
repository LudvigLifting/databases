from os import error
from typing import Dict, List
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import sqlite3
import hashlib
import datetime
import re
from urllib.parse import quote, unquote


def make_json(keys, data):
    ret = []
    for d in data:
        ret.append(dict(zip(keys, d)))
    return ret


def hash(msg):
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()


conn = sqlite3.connect("krusty.db", check_same_thread=False)
c = conn.cursor()

#c.execute("pragma foreign_keys = on;") # why??

app = FastAPI()

# Classes


class Ingredient(BaseModel):
    ingredient: str
    unit: str


class Delivery(BaseModel):
    deliveryTime: str
    quantity: int


class RecipeEntry(BaseModel):
    ingredient: str
    amount: int


class Cookie(BaseModel):
    name: str
    recipe: List[RecipeEntry]


class Customer(BaseModel):
    name: str
    address: str


class Pallet(BaseModel):
    cookie : str

# Emil

@app.get("/")
def index():
    return "This is not the response you are looking for."


@app.post("/reset")
def reset(response : Response):
    create_database_script = open("./create-schema.sql").read()
    try:
        c.executescript(create_database_script)
        response.status_code = 205
        conn.commit()
    except (sqlite3.Error) as e:
        print (e)
        response.status_code = 500
    return {"location": "/"}


@app.post("/cookies")
def post_cookies(cookie: Cookie, response: Response):
    q = """
    INSERT INTO products(product_name)
    VALUES (?)
    """
    try:
        c.execute(q, (cookie.name,))
        response.status_code = 201
    except (sqlite3.Error) as e:
        print(e)
        response.status_code = 422

    q = """
    INSERT INTO recipes(product_name, ingredient, recipe_amount)
    VALUES (?, ?, ?)
    """
    try:
        for i in range(len(cookie.recipe)):
            c.execute(q, (cookie.name, cookie.recipe[i].ingredient, cookie.recipe[i].amount))
        response.status_code = 201
    except (sqlite3.Error) as e:
        print(e)
        response.status_code = 422
    conn.commit()
    return {"location": f"/cookies/{quote(cookie.name)}"}


@app.get("/cookies")
def get_cookies(response: Response):
    # Show the number of unblocked pallets we have with the cookie in store
    q = """
    SELECT product_name, count(pallet_id)
    FROM products
    LEFT OUTER JOIN pallets USING (product_name)
    LEFT OUTER JOIN blocks USING (product_name)
    GROUP BY product_name
    ORDER BY product_name
    """
    try:
        c.execute(q)
        response.status_code = 200
    except (sqlite3.Error) as e:
        print(e)
        response.status_code = 500
    res = c.fetchall()
    return {"data": make_json(("name", "pallets"), res)}


@app.get("/cookies/{name}/recipe")
def get_cookie_recipe(name, response: Response):
    q = """
    SELECT ingredient, recipe_amount, ingredient_unit 
    FROM recipes
    JOIN ingredients
    USING (ingredient)
    WHERE product_name = ?
    """
    try:
        c.execute(q, name)
        res = c.fetchall()
        response.status_code = 200
        return {"data": make_json(("ingredient", "amount", "unit"), res)}
    except (sqlite3.Error) as e:
        print(e)
        response.status_code = 404
    return {"data": []}


@app.post("/customers")
def post_customers(customer: Customer, response: Response):
    q = """
    INSERT INTO customers
    (customer_name, customer_address)
    VALUES (?, ?)
    """
    try:
        c.execute(q, (customer.name, customer.address))
        conn.commit()
        response.status_code = 201
    except (sqlite3.Error) as e:
        print (e)
        response.status_code = 400

    return { "location": f"/customers/{quote(customer.name)}" }

# Johannes

# list all customers


@app.get("/customers")
def get_customers(response: Response):
    q = """
    SELECT customer_name, customer_address FROM customers
    """
    c.execute(q)
    res = c.fetchall()
    response.status_code = 200
    return {"data": make_json(("name", "address"), res)}

# add an ingredient by name and unit from json POST body
# return the new resource such as { location: "/ingredients/breadcrumbs" }


@app.post("/ingredients")
def post_ingredients(ing: Ingredient, response: Response):
    q = """
    INSERT INTO ingredients (ingredient, ingredient_unit) 
    VALUES (?, ?)
    """
    try:
        c.execute(q, (ing.ingredient, ing.unit))
        response.status_code = 201
    except error as e:
        print(e)
        response.status_code = 400
    conn.commit()
    return {"location": f"/ingredients/{quote(ing.ingredient)}"}

# add delivery with { deliveryTime, quantity }
# returns { ingredient, quantity, unit }


@app.post("/ingredients/{ingredient}/deliveries")
def post_ingredients_delivery(ingredient, delivery: Delivery, response: Response):
    q = """
    INSERT INTO ingredient_deliveries
    (ingredient, ingredient_delivery_datetime, ingredient_amount)
    VALUES (?, ?, ?)
    """
    try:
        c.execute(q, (ingredient, delivery.deliveryTime, delivery.quantity))
        response.status_code = 201
    except error as e:
        print(e)
        response.status_code = 400
    conn.commit()

    q2 = """
    SELECT ingredient, quantity, ingredients.ingredient_unit
    FROM ingredients
    JOIN ingredients_in_stock USING (ingredient)
    WHERE ingredient = ?
    """
    try:
        c.execute(q2, (ingredient,))
    except error as e:
        print(e)
        response.status_code = 400
    res = c.fetchall()
    return {"data": make_json(("ingredient", "quantity", "unit"), res)}


@app.get("/ingredients")
def get_ingredients():
    q = """
    SELECT ingredient, quantity, ingredients.ingredient_unit
    FROM ingredients
    JOIN ingredients_in_stock USING (ingredient)
    """
    try:
        c.execute(q)
    except error as e:
        print(e)
    res = c.fetchall()
    return {"data": make_json(('ingredient', 'quantity', 'unit'), res)}

# Ludvig


@app.post("/pallets")
def post_pallets(pallet: Pallet, response: Response):
    location = ""
    q = """
    INSERT INTO pallets(product_name, production_datetime)
    VALUES (?, ?)
    """

    response.status_code = 201
    location = ""

    try:
        c.execute(q, (pallet.cookie, datetime.datetime.now()))
        conn.commit()
        c.execute("SELECT pallet_id FROM pallets WHERE rowid = last_insert_rowid()")
        res = c.fetchone()
        location = "/pallets/" + res[0]
    except (sqlite3.Error) as err:
        print (err)
        response.status_code=422

    return { "location": location }

@ app.get("/pallets")
def get_pallets(response: Response, cookie: str = "", before: str = "", after: str = ""):

    params=[]
    q="""
    SELECT pallet_id, product_name, production_datetime,
    CASE 
        WHEN production_datetime > from_datetime AND production_datetime < to_datetime 
        THEN 1 
        ELSE 0 
    END blocked
    FROM pallets 
    LEFT OUTER JOIN blocks USING (product_name)
    WHERE 1=1
    """
    if cookie != "":
        q += "AND cookie_name = ?"
        params.append(cookie)
    if before != "":
        q += "AND production_datetime < ?"
        params.append(before)
    if after != "":
        q += "AND production_datetime > ?"
        params.append(after)

    try:
        if len(params) == 0:
            c.execute(q)
        else:
            c.execute(q, params)
    except (sqlite3.Error) as err:
        print (err)
        response.status_code=400

    res=c.fetchall()
    response.status_code=200
    return {"data": make_json(("id", "cookie", "productionDate", "blocked"), res)}

@ app.post("/cookies/{name}/block", response_class=PlainTextResponse)
def post_cookie_block(name, response: Response, before: str = "", after: str = "3000-12-12 23:59:59"):
    q = """
    INSERT INTO blocks (product_name, from_datetime, to_datetime)
    VALUES (?, ?, ?)
    """
    try:
        c.execute(q, (name, before, after))
    except (sqlite3.Error) as err:
        print (err)
        response.status_code=400

    response.status_code=205
    return ""

@ app.post("/cookies/{name}/unblock", response_class=PlainTextResponse)
def post_cookie_unblock(name, response: Response):
    q = """
    UPDATE blocks
    SET to_datetime = ?
    WHERE product_name = ? AND rowid = last_insert_rowid()
    """
    try:
        c.execute(q, (datetime.datetime.now(), name))
    except (sqlite3.Error) as err:
        print (err)
        response.status_code=400

    response.status_code=205
    return ""
