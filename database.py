import datetime
from google.cloud import firestore

# Initialize Firestore DB client
db = firestore.Client()

def create_or_get_user(phone_number: str, pincode: str = "", full_name: str = "", email: str = ""):
    users_ref = db.collection("users")
    # Using FieldFilter to keep query clean and modern
    query = users_ref.where(filter=firestore.FieldFilter("phone_number", "==", phone_number)).limit(1).get()

    if query:
        user_doc = query[0]
        user_data = user_doc.to_dict()
        user_id = user_doc.id

        # Update full_name/pincode if missing on existing user
        update_fields = {}
        if full_name and not user_data.get("full_name"):
            update_fields["full_name"] = full_name
        if pincode and not user_data.get("pincode"):
            update_fields["pincode"] = pincode
            
        if update_fields:
            users_ref.document(user_id).update(update_fields)
            user_data.update(update_fields)

        return {"id": user_id, **user_data}

    # Create new user document
    new_user_data = {
        "phone_number": phone_number,
        "full_name": full_name,
        "pincode": pincode,
        "email": email,
        "status": "active",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    _, doc_ref = users_ref.add(new_user_data)
    
    return {"id": doc_ref.id, **new_user_data}


def create_order(user_id: str, labstack_order_id: str, lab_partner: str, items: list):
    orders_ref = db.collection("orders")
    
    new_order_data = {
        "user_id": user_id,
        "labstack_order_id": labstack_order_id,
        "lab_partner": lab_partner,
        "items": items,
        "status": "scheduled",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    _, doc_ref = orders_ref.add(new_order_data)
    
    return doc_ref.id


def get_user_orders(user_id: str):
    """
    Retrieves all orders for a user to display on their dashboard view.
    """
    orders_ref = db.collection("orders")
    docs = orders_ref.where(filter=firestore.FieldFilter("user_id", "==", user_id)).stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]