# Get items that were purchased on discount and purchased price
SELECT o.order_id, o.order_date, iss.item_name, iss.shop_name, d.percent, (100 - d.percent)*iss.price*0.01 as purchased_price
FROM items_soldIn_shops iss
JOIN shoppingcarts_contain_items sci ON (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
JOIN orders_ordered o ON o.cart_id = sci.cart_id
LEFT JOIN have_discounts d ON (d.item_id, d.shop_id) = (iss.id, iss.shop_id)
WHERE d.begin_date <= o.order_date AND d.end_date >= o.order_date;

# Get the orders that contain items on discount
SELECT o.order_id
FROM items_soldIn_shops iss
JOIN shoppingcarts_contain_items sci ON (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
JOIN orders_ordered o ON o.cart_id = sci.cart_id
LEFT JOIN have_discounts d ON (d.item_id, d.shop_id) = (iss.id, iss.shop_id)
WHERE d.begin_date <= o.order_date AND d.end_date >= o.order_date
GROUP BY o.order_id;

# Get the orders that did not have any discounts
SELECT order_id
FROM orders_ordered
EXCEPT
SELECT o.order_id
FROM items_soldIn_shops iss
JOIN shoppingcarts_contain_items sci ON (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
JOIN orders_ordered o ON o.cart_id = sci.cart_id
LEFT JOIN have_discounts d ON (d.item_id, d.shop_id) = (iss.id, iss.shop_id)
WHERE d.begin_date <= o.order_date AND d.end_date >= o.order_date;

# Get # of items purchased on sale at some point
SELECT COUNT(DISTINCT iss.id)
FROM items_soldIn_shops iss
JOIN shoppingcarts_contain_items sci ON (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
JOIN orders_ordered o ON o.cart_id = sci.cart_id
LEFT JOIN have_discounts d ON (d.item_id, d.shop_id) = (iss.id, iss.shop_id)
WHERE d.begin_date <= o.order_date AND d.end_date >= o.order_date;

# Get # of items never purchased on sale
SELECT COUNT(*)
FROM items_soldIn_shops
WHERE id IN (SELECT id
			FROM items_soldIn_shops
			EXCEPT 
			SELECT DISTINCT iss.id
			FROM items_soldIn_shops iss
			JOIN shoppingcarts_contain_items sci ON (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
			JOIN orders_ordered o ON o.cart_id = sci.cart_id
			LEFT JOIN have_discounts d ON (d.item_id, d.shop_id) = (iss.id, iss.shop_id)
			WHERE d.begin_date <= o.order_date AND d.end_date >= o.order_date);