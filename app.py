from flask import Flask, request, jsonify, make_response
from settings import connection, logger, handle_exceptions

# Creating Flask instance
app = Flask(__name__)


# Query
# create_query = (
#     """CREATE table cart( sno serial PRIMARY KEY,
#                         items VARCHAR(200) NOT NULL,
#                         quantity INTEGER NOT NULL,
#                         price INTEGER NOT NULL );"""
# )

# Table
#  sno | items  | quantity | price | save_for_later | wishlist | discount
# -----+--------+----------+-------+----------------+----------+----------
#    4 | Orange |       12 |   400 |                |          |
#    1 | Apples |        5 |   300 | t              |          |
#    3 | KIWI   |       10 | 650.0 |                | t        |
#    2 | Mango  |        6 | 640.0 |                | t        |      160




@app.route("/add", methods=["POST"])             # CREATE an item
@handle_exceptions
def add_to_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add item in the cart")

    items = request.json["items"]
    quantity = request.json["quantity"]
    price = request.json["price"]

    # input_format = {
    #     "items": "KIWI",
    #     "quantity": 10,
    #     "price": 1000
    # }

    # insert query
    add_query = """INSERT INTO cart(items, 
                                quantity, price) VALUES (%s, %s, %s)"""

    # Insert values in the query
    values = (items, quantity, price)

    # execute query
    cur.execute(add_query, values)

    # commit to database
    conn.commit()
    response = make_response(jsonify({"message": f"{items} added to the cart"}), 200)

    logger(__name__).info(f"{items} added in the cart, Status code - {response.status_code}")

    # close the database connection
    logger(__name__).warning("Hence item added, closing the connection")

    return response


@app.route("/", methods=["GET"], endpoint='show_cart')            # READ the cart list
@handle_exceptions
def show_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display items in the cart using pagination")

    # Get page number from the user -> page
    page = request.args.get('page', 1, type=int)

    # how many records to show per page i.e (LIMIT) -> per_page
    per_page = request.args.get('perPage', 5, type=int)


    # Fetch all the user accounts in the table
    cur.execute("SELECT COUNT(*) FROM cart")
    total_accounts = cur.fetchone()[0]

    # Calculate the total number of pages
    total_pages = int(total_accounts / per_page) + (total_accounts % per_page > 0)

    # Retrieve the records for the current page i.e (OFFSET)
    offset = (page - 1) * per_page  # Calculate the offset for the current page
    cur.execute('SELECT * FROM cart LIMIT %s OFFSET %s', (per_page, offset))
    data = cur.fetchall()

    # Log the details into logger file
    logger(__name__).info(f"Displayed list of {per_page} accounts having total of {total_pages} pages")
    return jsonify({"message": f"Displayed list of {per_page} accounts having total of {total_pages} pages",
                    "details": data}), 200



@app.route("/cart/<int:sno>", methods=["PUT"], endpoint='update_item_details')
@handle_exceptions
def update_item_details(sno):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    cur.execute("SELECT items from cart where sno = %s", (sno,))
    get_item = cur.fetchone()

    if not get_item:
        return jsonify({"message": "Item not found"}), 200
    data = request.get_json()
    items = data.get('items')
    quantity = data.get('quantity')
    price = data.get('price')

    if items:
        cur.execute("UPDATE cart SET items = %s WHERE sno = %s", (items, sno))
    elif quantity:
        cur.execute("UPDATE cart SET quantity = %s WHERE sno = %s", (quantity, sno))
    elif price:
        cur.execute("UPDATE cart SET price = %s WHERE sno = %s", (price, sno))

    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Item updated: {data}")
    return jsonify({"message": "Item updated", "Details": data}), 200

@app.route("/cart/checkout", methods=["GET"], endpoint='checkout')    # Calculate the total price
@handle_exceptions
def checkout():
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to calculate the total price ")

    cur.execute("SELECT SUM(price*quantity) FROM cart "
                "WHERE (save_for_later IS NULL OR save_for_later != 'TRUE') "
                "AND (wishlist IS NULL OR wishlist != 'TRUE');")

    total_price = cur.fetchone()
    print(total_price)

    # Log the details into logger file
    logger(__name__).info(f"Total calculated {total_price}")
    return jsonify({"message": "Total calculated", "total": total_price}), 200

@app.route("/cart/save_for_later/<int:sno>", methods=["PUT"], endpoint='item_saved_later')
@handle_exceptions
def item_saved_for_later(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item in the wishlist ")

    # Get item details from the cart with mentioned serial number
    cur.execute("SELECT * from CART WHERE sno = %s", (sno,))
    get_item = cur.fetchone()
    print(get_item)

    # If not present then return not found message
    if not get_item:
        return jsonify({"message": "Item not found"}), 200

    # If found then unpack all the values from the fetched data
    item_id = get_item[0]
    items = get_item[1]
    quantity = get_item[2]
    price = get_item[3]

    # Initially show that item is in the wishlist
    # Update that item as true in the wishlist column
    update_query = "UPDATE cart SET save_for_later = TRUE WHERE sno = %s"
    cur.execute(update_query, (sno,))

    # Then insert the values into the wishlist table
    insert_query = """INSERT INTO saved_later(item_id, items, quantity, price) VALUES (%s, %s, %s, %s);"""
    insert_values = (item_id, items, quantity, price)

    cur.execute(insert_query, insert_values)

    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"{get_item} saved for later")
    return jsonify({"message": f"{get_item} saved for later"}), 200


@app.route("/cart/wishlist/<int:sno>", methods=["POST"], endpoint='wishlist_item')
@handle_exceptions
def adding_to_wishlist(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item in the wishlist ")

    # Get item details from the cart with mentioned serial number
    cur.execute("SELECT * from CART WHERE sno = %s", (sno,))
    get_item = cur.fetchone()
    print(get_item)

    # If not present then return not found message
    if not get_item:
        return jsonify({"message": "Item not found"}), 200

    # If found then unpack all the values from the values
    item_id = get_item[0]
    items = get_item[1]
    quantity = get_item[2]
    price = get_item[3]

    # Initially show that item is in the wishlist
    # Update that item as true in the wishlist column
    update_query = "UPDATE cart SET wishlist = TRUE WHERE sno = %s"
    cur.execute(update_query, (sno,))

    # Then insert the values into the wishlist table
    insert_query = """INSERT INTO wishlist(item_id, items, quantity, price) VALUES (%s, %s, %s, %s);"""
    insert_values = (item_id, items, quantity, price)

    cur.execute(insert_query, insert_values)

    # Commit the changes in the both tables
    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"{items} saved for later")
    return jsonify({"message": f"{items} saved in wishlist", "details": get_item}), 200

@app.route("/cart/discount/<int:sno>", methods=["PUT"], endpoint='get_discount')
@handle_exceptions
def get_discount(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection for discount")

    cur.execute("SELECT items from CART WHERE sno = %s", (sno,))
    get_item = cur.fetchone()

    if not get_item:
        return jsonify({"message": "Item not found"}), 200

    discount_list = {
        "DISC10": 0.1,
        "DISC20": 0.20,
        "DISC35": 0.35,
        "DISC60": 0.60
    }

    # get price of item
    cur.execute("SELECT price FROM cart WHERE sno = %s", (sno,))
    get_price = cur.fetchone()
    print("get amount", get_price[0])

    amount = float(get_price[0])

    # get discount code from the user
    find_disc = request.json["discount"]
    print("check correct code", find_disc)

    if not find_disc:
        return jsonify({"message": "Invalid code, please try again"}), 200

    # check the user entered correct discount code
    check_percent = discount_list[find_disc]
    print("percentage", check_percent)

    check_cut = amount * check_percent
    print("cut", check_cut)

    updated_amount = amount - check_cut
    print("Updated amount", amount, check_percent, check_cut, updated_amount)

    query = "UPDATE cart SET price = %s WHERE sno = %s"
    cur.execute(query, (updated_amount, sno))

    cur.execute("UPDATE cart SET disc_percent = %s WHERE sno = %s", (check_cut, sno))

    # commit to database
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"updated: {updated_amount}, percent: {check_percent}%")
    return jsonify({"message": f"{updated_amount} final price after discount of {check_percent}%"}), 200



@app.route("/delete/<int:sno>", methods=["DELETE"], endpoint='delete_items')      # DELETE an item from cart
@handle_exceptions
def delete_items(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete the item from the cart")

    delete_query = "DELETE from cart WHERE sno = %s"
    cur.execute(delete_query, (sno,))
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Item no {sno} deleted from the cart")
    return jsonify({"message": "Deleted Successfully", "item_no": sno}), 200


@app.route("/search/<string:item>", methods=["GET"], endpoint='search_items_in_cart')      # DELETE an item from cart
@handle_exceptions
def search_items_in_cart(item):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to search item in the cart")

    query = "SELECT * FROM cart WHERE items = %s"
    cur.execute(query, (item,))
    get_item = cur.fetchone()

    if not get_item:
        # Log the details into logger file
        logger(__name__).info(f"{item} is not available in the cart")
        return jsonify({"message": f"{item} not found in the cart"}), 200
    else:
        # Log the details into logger file
        logger(__name__).info(f"{item} is available in the cart")
        return jsonify({"message": f"{item} found in the cart",
                        "details": get_item}), 200

@app.route("/empty_cart", methods=["DELETE"], endpoint='empty_cart')      # DELETE all items from cart
@handle_exceptions
def empty_the_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to EMPTY the cart")

    # Execute delete query to remove all the items from the table
    cur.execute("DELETE FROM cart")

    # Commit the change to this table
    # conn.commit()

    # Log the details into logger file
    logger(__name__).info("Emptying the cart successful")
    return jsonify({"message": "Emptying the cart successful"}), 200


@app.route("/pagination", methods=["GET"], endpoint='usage_of_pagination')
@handle_exceptions
def usage_of_pagination():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display list of items using pagination")

    # Get page number from the user
    page = request.args.get('page', 1, type=int)
    """page = argument
        1 = default value
        type = type of value"""

    # how many records to show per page i.e (LIMIT)
    per_page = request.args.get('page', 1, type=int)

    # Fetch all the user accounts in the table
    cur.execute("SELECT COUNT(*) FROM cart")
    total_items = cur.fetchone()[0]

    # Calculate the total number of pages
    total_pages = int(total_items / per_page) + (total_items % per_page > 0)

    # Retrieve the records for the current page i.e (OFFSET)
    offset = (page - 1) * per_page      # Calculate the offset for the current page
    cur.execute('SELECT * FROM cart LIMIT %s OFFSET %s', (per_page, offset))
    data = cur.fetchall()

    # Log the details into logger file
    logger(__name__).info(f"Displayed list of {total_items} accounts having total of {total_pages} pages")

    return jsonify({"message": f"Displayed list of {total_items} accounts having total of {total_pages} pages",
                    "details": data}), 200



if __name__ == "__main__":
    app.run(debug=True, port=5000)
