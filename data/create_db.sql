drop table if exists Payment_Methods cascade;
drop table if exists Members cascade;
drop table if exists Customers cascade;
drop table if exists Items_soldIn_Shops cascade;
drop table if exists Have_Discounts cascade;
drop table if exists Shopping_Carts cascade;
drop table if exists Orders_ordered cascade;
drop table if exists ShoppingCarts_contain_items cascade;

create table Payment_Methods(
    cc_number varchar(16),
    cvv varchar(3),
    expiration_date date,
    street_address varchar(128),
    city varchar(32),
    state varchar(2),
    zip varchar(5),
    primary key(cc_number, cvv, expiration_date)
);

create table Members(
    loyalty_number varchar(8) primary key,
    firstname varchar(16),
    lastname varchar(16),
    dob date
);

create table Customers(
    loyalty_number varchar(8) unique not null,
    cc_number varchar(16),
    cvv varchar(3),
    expiration_date date,
    primary key(loyalty_number, cc_number, cvv, expiration_date),
    foreign key (cc_number, cvv, expiration_date) references Payment_Methods(cc_number, cvv, expiration_date),
    foreign key (loyalty_number) references Members(loyalty_number)
);

create table Items_soldIn_Shops(
    id integer,
    item_name varchar(32),
    price decimal,
    item_description varchar(128),
    shop_id integer not null,
    shop_name varchar(32),
    shop_location varchar(32),
    primary key(id, shop_id)
);

create table Have_Discounts(
    begin_date date,
    end_date date,
    item_id integer,
    shop_id integer,
    percent integer,
    foreign key(item_id, shop_id) references Items_soldIn_Shops(id, shop_id),
    primary key(begin_date, end_date, item_id, shop_id)
);

create table Shopping_Carts(
    id integer primary key
);

create table ShoppingCarts_contain_Items(
    cart_id integer,
    item_id integer,
    shop_id integer,
    quantity integer,
    primary key(item_id, cart_id),
    foreign key(item_id, shop_id) references Items_soldIn_Shops(id, shop_id),
    foreign key(cart_id) references Shopping_Carts(id)
);

create table Orders_ordered(
    order_id integer primary key,
    order_date date,
    street_address varchar(128),
    city varchar(32),
    state varchar(2),
    zip varchar(5),
    cart_id integer unique,
    loyalty_number varchar(8),
    cc_number varchar(16),
    cvv varchar(3),
    expiration_date date,
    foreign key (cart_id) references Shopping_Carts(id),
    foreign key (loyalty_number, cc_number, cvv, expiration_date) references Customers(loyalty_number, cc_number, cvv, expiration_date)
);
