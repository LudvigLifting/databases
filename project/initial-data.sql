insert into customers 
(customer_name, customer_address) 
values
("Johannes", "Tunavägen 33"),
("Ludvig", ""),
("Emil", "");

insert into products 
(product_name)
values
("Chokladkaka"),
("Vaniljkaka"),
("Jordgubbskaka");

insert into ingredients 
(ingredient_name, ingredient_unit)
values
("socker", "g"),
("mjöl", "g"),
("choklad", "g"),
("vanilj", "ml"),
("jordgubb", "st");

insert into recipes
(product_name, ingredient_name, recipe_amount)
values
("Chokladkaka",   "mjöl",     1),
("Vaniljkaka",    "mjöl",     2),
("Jordgubbskaka", "mjöl",     1),
("Chokladkaka",   "socker",   3),
("Vaniljkaka",    "socker",   1),
("Jordgubbskaka", "socker",   2),
("Chokladkaka",   "choklad",  1),
("Vaniljkaka",    "vanilj",   1),
("Jordgubbskaka", "jordgubb", 1);

insert into ingredient_deliveries
(ingredient_name, ingredient_delivery_datetime, ingredient_amount)
values
("mjöl",     "2020-12-31 23:59:59", 100),
("mjöl",     "2021-01-01 15:00:00", 200),
("mjöl",     "2021-02-01 14:00:00", 150),
("socker",   "2020-12-24 23:59:59", 20),
("socker",   "2021-01-03 15:00:00", 10),
("socker",   "2021-02-05 14:00:00", 15),
("vanilj",   "2020-12-24 22:59:59", 200),
("choklad",  "2021-03-03 15:00:00", 34),
("jordgubb", "2021-02-06 14:00:00", 11);

insert into pallets 
(product_name, production_datetime)
values
("Chokladkaka", "2021-01-01 00:00"),
("Vaniljkaka", "2021-01-01 00:00"),
("Jordgubbskaka", "2021-01-01 00:00"),
("Chokladkaka", "2021-01-01 00:01");
