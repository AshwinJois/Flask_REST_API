import os
import psycopg2
from flask import Flask, request, jsonify      # flask is a package, Flask is a class
from dotenv import load_dotenv


CREATE_CARDS_TABLE = """CREATE TABLE IF NOT EXISTS cards (card_id SERIAL PRIMARY KEY, Card_type TEXT, Bank TEXT, Gultig_bis TEXT)"""

CREATE_ROOMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS shopping (id SERIAL, date TEXT, super_markt TEXT, Cost_in_Euros REAL, Payment_Method INTEGER REFERENCES cards(card_id));" #, UNIQUE(Payment_Method)
)

INSERT_ROOM_RETURN_ID = "INSERT INTO shopping (date, super_markt, Cost_in_Euros, Payment_Method) VALUES (%s, %s, %s, %s) RETURNING id;"

INSERT_CARD_DETAILS = (
    "INSERT INTO cards (Card_type, Bank, Gultig_bis) VALUES (%s, %s, %s)  RETURNING card_id;"
)
UPDATE_USER_BY_ID = "UPDATE shopping SET date=%s, super_markt=%s, Cost_in_Euros=%s WHERE id = %s;"
Total_Expenses = "SELECT SUM(cost_in_euros::numeric) FROM shopping;"
Table_contents = "SELECT * FROM shopping WHERE id = %s:"  

load_dotenv()

app = Flask(__name__) # Creating an instnace of the Flask class
url = os.getenv("Database_URL")
connection = psycopg2.connect(url)


@app.route("/api/grocery", methods=["POST"])
def create_room():
    data = request.get_json()
    date = data["date"]
    super_markt = data["super_markt"]
    Cost_in_Euros = data["Cost_in_Euros"]
    Payment_Method = data["Payment_Method"]

    if(Payment_Method=="1" or Payment_Method=="2"):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_ROOMS_TABLE)
                cursor.execute(INSERT_ROOM_RETURN_ID, (date, super_markt, Cost_in_Euros, Payment_Method))
                room_id = cursor.fetchone()[0]
        return {"id": room_id, "message": f"Expenditure on {date} created."}, 201
    else:
        return jsonify({"error": f"Invalid payment method"}), 404

@app.route("/api/grocery/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    data = request.get_json()
    date = data["date"]
    super_markt = data["super_markt"]
    Cost_in_Euros = data["Cost_in_Euros"]    

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(UPDATE_USER_BY_ID, (date, super_markt, Cost_in_Euros,room_id))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {room_id} not found."}), 404
    return jsonify({"id": room_id, "message": f"Expenditure on {date} updated."})


@app.route("/api/total", methods=["GET"])
def get_total_expenses():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(Total_Expenses)            
            total = cursor.fetchone()[0]
            cursor.close()
    return jsonify({"Message": f"The total of {total} euros is spent till now"}) 


@app.route("/api/output", methods=["GET"])
def get_output():
    return ("Hey, the docker is working perfectly")

@app.route("/api/search/<int:room_id>", methods=["GET"])
def get_table(room_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM shopping WHERE id = %s", (room_id,))            
            contents = cursor.fetchone()
            if contents:
                return jsonify({"id": contents[0], "date": contents[1], "super_markt": contents[2], "cost_in_euros": contents[3]})
            else:    
                return jsonify({"error": f"User with ID {room_id} not found."}), 404
            

@app.route("/api/delete/<int:room_id>", methods=["DELETE"])
def delete_entry(room_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM rooms WHERE id = %s;", (room_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {room_id} not found."}), 404
    return jsonify({"message": f"User with ID {room_id} deleted."})


@app.route("/api/card", methods=["POST"])
def create_card():
    data = request.get_json()
    #card_id = data["card_id"]
    Card_type = data["Card_type"]
    Bank = data["Bank"]
    Gultig_bis = data["Gultig_bis"]
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_CARDS_TABLE)
            cursor.execute(INSERT_CARD_DETAILS, (Card_type, Bank, Gultig_bis))
            #room_id = cursor.fetchone()[0]
    return {"message": f"Information on {Card_type} created."}, 201

if __name__ == "__main__":
    app.run(debug=True, port=4000) # .run is called to start the development server
                                   # The .py file that contains .run is the main file, this file cannot be run
                                   # by importing it in a different python file/python module

                                   # When debug mode is turned ON, the server restarts on its own after making
                                   # any changes in the code