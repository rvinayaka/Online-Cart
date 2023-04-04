from flask import Flask, request, jsonify
from conn import connection
from settings import logger

app = Flask(__name__)


# Query
# create_query = (
#     """CREATE table cart( sno serial PRIMARY KEY,
#                         items VARCHAR(200) NOT NULL,
#                         quantity INTEGER NOT NULL,
#                         price INTEGER NOT NULL );"""
# )

# Table
#  sno | items  | quantity | price
# -----+--------+----------+-------
#    1 | Apples |        5 |   300
#    2 | Mango  |        6 |   800
#    3 | KIWI   |       10 |  1000


@app.route("/add", methods=["POST"])             # CREATE an item
def add_to_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add item in the cart")

    try:
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
        return jsonify({"message": "Item added to the cart"}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence item added, closing the connection")


@app.route("/", methods=["GET"])            # READ the cart list
def show_cart():
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display items in the cart")

    try:
        show_query = "SELECT * FROM cart;"
        cur.execute(show_query)
        data = cur.fetchall()
        # Log the details into logger file
        logger(__name__).info("Displayed list of all items in the cart")

        return jsonify({"message": data}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence items displayed, closing the connection")


@app.route("/cart/<int:sno>", methods=["PUT"])
def update_item_details(sno):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    try:
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
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence item updated, closing the connection")


@app.route("/cart/checkout", methods=["GET"])    # Calculate the total price
def checkout():
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to calculate the total price ")

    try:
        cur.execute("SELECT SUM(price*quantity) FROM cart "
                    "WHERE (save_for_later IS NULL OR save_for_later != 'TRUE') "
                    "AND (wishlist IS NULL OR wishlist != 'TRUE');")

        total_price = cur.fetchone()
        print(total_price)

        # Log the details into logger file
        logger(__name__).info(f"Total calculated {total_price}")
        return jsonify({"message": "Total calculated", "total": total_price}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence checkout done, closing the connection")

@app.route("/cart/save_for_later/<int:sno>", methods=["PUT"])
def item_saved_later(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item for later ")

    try:
        cur.execute("SELECT items from CART WHERE sno = %s", (sno, ))
        get_item = cur.fetchone()

        if not get_item:
            return jsonify({"message": "Item not found"}), 200

        query = "UPDATE cart SET save_for_later = TRUE WHERE sno = %s"
        cur.execute(query, (sno, ))

        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"{get_item} saved for later")
        return jsonify({"message": f"{get_item} saved for later"}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence item saved for later, closing the connection")


@app.route("/cart/wishlist/<int:sno>", methods=["PUT"])
def wishlist_item(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to save item in the wishlist ")

    try:
        cur.execute("SELECT items from CART WHERE sno = %s", (sno, ))
        get_item = cur.fetchone()

        if not get_item:
            return jsonify({"message": "Item not found"}), 200

        query = "UPDATE cart SET wishlist = TRUE WHERE sno = %s"
        cur.execute(query, (sno, ))

        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"{get_item} saved for later")
        return jsonify({"message": f"{get_item} saved for later"}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence item saved in wishlist, closing the connection")



@app.route("/cart/discount/<int:sno>", methods=["PUT"])
def get_discount(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection for discount")

    try:
        cur.execute("SELECT items from CART WHERE sno = %s", (sno, ))
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

        # commit to database
        conn.commit()

        # Log the details into logger file
        logger(__name__).info(f"updated: {updated_amount}, percent: {check_percent}%")
        return jsonify({"message": f"{updated_amount} final price after discount of {check_percent}%"}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence discount process completed, closing the connection")



@app.route("/delete/<int:sno>", methods=["GET", "DELETE"])      # DELETE an item from cart
def delete_items(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete the item from the cart")

    try:
        delete_query = "DELETE from cart WHERE sno = %s"
        cur.execute(delete_query, (sno,))
        conn.commit()

        # Log the details into logger file
        logger(__name__).info(f"Account no {sno} deleted from the table")
        return jsonify({"message": "Deleted Successfully", "item_no": sno}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts deleted, closing the connection")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
