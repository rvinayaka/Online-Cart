from flask import Flask, request, jsonify
from conn import connection
from settings import logger, handle_exceptions
import psycopg2
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
    logger(__name__).info(f"{items} added in the cart")

    # close the database connection
    logger(__name__).warning("Hence item added, closing the connection")

    return jsonify({"message": "Item added to the cart"}), 200


@app.route("/", methods=["GET"], endpoint='show_cart')            # READ the cart list
@handle_exceptions
def show_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display items in the cart")

    show_query = "SELECT * FROM cart;"
    cur.execute(show_query)
    data = cur.fetchall()
    # Log the details into logger file
    logger(__name__).info("Displayed list of all items in the cart")

    return jsonify({"message": data}), 200


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
def item_saved_later(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item for later ")

    cur.execute("SELECT items from CART WHERE sno = %s", (sno,))
    get_item = cur.fetchone()

    if not get_item:
        return jsonify({"message": "Item not found"}), 200

    query = "UPDATE cart SET save_for_later = TRUE WHERE sno = %s"
    cur.execute(query, (sno,))

    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"{get_item} saved for later")
    return jsonify({"message": f"{get_item} saved for later"}), 200


@app.route("/cart/wishlist/<int:sno>", methods=["PUT"], endpoint='wishlist_item')
@handle_exceptions
def wishlist_item(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item in the wishlist ")

    cur.execute("SELECT items from CART WHERE sno = %s", (sno,))
    get_item = cur.fetchone()

    if not get_item:
        return jsonify({"message": "Item not found"}), 200

    query = "UPDATE cart SET wishlist = TRUE WHERE sno = %s"
    cur.execute(query, (sno,))

    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"{get_item} saved for later")
    return jsonify({"message": f"{get_item} saved for later"}), 200

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



@app.route("/delete/<int:sno>", methods=["GET", "DELETE"], endpoint='delete_items')      # DELETE an item from cart
@handle_exceptions
def delete_items(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete the item from the cart")

    delete_query = "DELETE from cart WHERE sno = %s"
    cur.execute(delete_query, (sno,))
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Account no {sno} deleted from the table")
    return jsonify({"message": "Deleted Successfully", "item_no": sno}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
