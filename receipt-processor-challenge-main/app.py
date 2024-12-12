from flask import Flask, request, jsonify
import uuid
import math
from datetime import datetime

app = Flask(__name__)

# In-memory storage for receipts and their points
receipts = {}

# Utility function to calculate points
def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    retailer_name = receipt.get("retailer", "")
    points += sum(1 for c in retailer_name if c.isalnum())

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = float(receipt.get("total", 0))
    if total.is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    items = receipt.get("items", [])
    points += (len(items) // 2) * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3, calculate points
    for item in items:
        description = item.get("shortDescription", "").strip()
        price = float(item.get("price", 0))
        if len(description) % 3 == 0:
            points += math.ceil(price * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = receipt.get("purchaseDate", "")
    if purchase_date:
        day = int(purchase_date.split("-")[-1])
        if day % 2 != 0:
            points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = receipt.get("purchaseTime", "")
    if purchase_time:
        time_obj = datetime.strptime(purchase_time, "%H:%M").time()
        if datetime.strptime("14:00", "%H:%M").time() < time_obj < datetime.strptime("16:00", "%H:%M").time():
            points += 10

    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    receipt = request.get_json()

    if not receipt:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Generate a unique ID for the receipt
    receipt_id = str(uuid.uuid4())

    # Calculate points and store in memory
    points = calculate_points(receipt)
    receipts[receipt_id] = points

    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    points = receipts.get(receipt_id)

    if points is None:
        return jsonify({"error": "Receipt ID not found"}), 404

    return jsonify({"points": points}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    print("Server is running on http://0.0.0.0:5000")

