pragma foreign_keys = off;

drop table if exists products;
create table products (
	product_name text primary key
);

drop table if exists recipes;
create table recipes (
	product_name text,
	ingredient text,
	recipe_amount int,
	primary key (product_name, ingredient),
	foreign key (product_name) references products (product_name),
	foreign key (ingredient) references ingredients (ingredient)
);

drop table if exists customers;
create table customers (
	customer_name text primary key,
	customer_address text
);

drop table if exists orders;
create table orders (
	order_id text primary key default (lower(hex(randomblob(16)))),
	customer_name text,
	order_datetime text,
	foreign key (customer_name) references customers (customer_name)
);

drop table if exists pallets;
create table pallets (
	pallet_id text primary key default (lower(hex(randomblob(16)))),
	product_name text,
	production_datetime text,
	order_id text,
	loaded_datetime text,
	delivered_datetime text,
	foreign key (order_id) references orders (order_id),
	foreign key (product_name) references products (product_name)
);

drop table if exists order_items;
create table order_items (
	order_id text,
	product_name text,
	order_amount int,
	primary key (order_id, product_name),
	foreign key (order_id) references orders (order_id),
	foreign key (product_name) references products (product_name)
);

drop table if exists ingredient_deliveries;
create table ingredient_deliveries (
	ingredient text,
	ingredient_delivery_datetime text,
	ingredient_amount int,
	primary key (ingredient, ingredient_delivery_datetime),
	foreign key (ingredient) references ingredients (ingredient)
);

drop table if exists blocks;
create table blocks (
	product_name text,
	from_datetime text,
	to_datetime text,
	primary key (product_name, from_datetime, to_datetime),
	foreign key (product_name) references products (product_name)
);

-- ny
drop table if exists ingredients;
create table ingredients (
	ingredient text primary key,
	ingredient_unit text
);

drop view if exists ingredients_in_stock;
create view ingredients_in_stock (ingredient, quantity, ingredient_unit) as
	with used_ingredients (ingredient, used_amount) as (
			select ingredient, sum(recipe_amount)*54 as used_amount
			from pallets
			join recipes using (product_name)
			group by ingredient
	),
	delivered_ingredients (ingredient, delivered_amount) as (
			select ingredient, sum(ingredient_amount) as delivered_amount
			from ingredient_deliveries
			group by ingredient
	)
	select ingredient, (delivered_amount - used_amount) as quantity, ingredient_unit
	from ingredients
	join used_ingredients using (ingredient)
	join delivered_ingredients using (ingredient);

create trigger if not exists ingredient_check
before insert on pallets
when
	(
		select min(quantity - 54*recipe_amount) as smallest_amount
		from ingredients
		join ingredients_in_stock using (ingredient)
		join recipes using (ingredient)
		where product_name = NEW.product_name
	) < 0
	begin
		select raise (abort, 'Not enough ingredients')
	end;
end;


pragma foreign_keys = on;
