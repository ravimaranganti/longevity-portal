from google.cloud import firestore
from datetime import datetime

# Initializes Firestore using default GCP project credentials
db = firestore.Client()

# --- USER OPERATIONS ---

def create_or_get_user(phone_number: str, pincode: str = None):
    """
    Finds a user by phone number or creates a new profile if they don't exist.
    """
    users_ref = db.collection("users")
    query = users_ref.where("phone_number", "==", phone_number).limit(1).get()

    if query:
        # Existing user
        doc = query[0]
        user_data = doc.to_dict()
        user_data["id"] = doc.id
        return user_data
    
    # New user creation
    new_user_data = {
        "phone_number": phone_number,
        "pincode": pincode,
        "full_name": "",
        "email": "",
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    
    doc_ref = users_ref.add(new_user_data)
    new_user_data["id"] = doc_ref[1].id
    return new_user_data


# --- ORDER OPERATIONS ---

def create_order(user_id: str, labstack_order_id: str, lab_partner: str, items: list):
    """
    Stores an order placed via LabStack attached to a specific user.
    """
    orders_ref = db.collection("orders")
    order_data = {
        "user_id": user_id,
        "labstack_order_id": labstack_order_id,
        "lab_partner": lab_partner,
        "items": items,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    doc_ref = orders_ref.add(order_data)
    return doc_ref[1].id

def get_user_orders(user_id: str):
    """
    Retrieves all orders for the dashboard view.
    """
    orders_ref = db.collection("orders")
    docs = orders_ref.where("user_id", "==", user_id).stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]
