from flask import Flask, render_template, request, jsonify
import re
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"NLTK download failed: {e}. Using basic processing.")

app = Flask(__name__)

# Hotel data
hotel_data = {
    "name": "PC Hotel",
    "description": "A luxurious 5-star hotel offering world-class amenities and exceptional service.",
    "rooms": {
        "single": {
            "description": "A cozy single room with basic amenities, perfect for solo travelers.",
            "price": 120,
            "capacity": 1,
            "features": ["Queen bed", "Work desk", "City view"]
        },
        "double": {
            "description": "A comfortable double room for two guests, ideal for couples.",
            "price": 180,
            "capacity": 2,
            "features": ["King bed", "Balcony", "Mini fridge"]
        },
        "deluxe": {
            "description": "A spacious deluxe room with premium features and modern decor.",
            "price": 250,
            "capacity": 2,
            "features": ["King bed", "Jacuzzi", "Ocean view", "Room service"]
        },
        "suite": {
            "description": "A luxurious suite with separate living area, perfect for extended stays.",
            "price": 400,
            "capacity": 4,
            "features": ["Master bedroom", "Living room", "Kitchenette", "Butler service"]
        }
    },
    "amenities": [
        "High-speed WiFi throughout the property",
        "Central air conditioning and heating",
        "Complimentary continental breakfast",
        "Valet parking and covered garage",
        "Olympic-sized swimming pool",
        "State-of-the-art fitness center",
        "24/7 room service",
        "Concierge services",
        "Business center",
        "Spa and wellness center"
    ],
    "booking": {
        "how_to_book": "You can book a room through our website, by calling our reservations team at (555) 123-4567, or visiting our front desk in person.",
        "check_availability": "To check availability, please provide your preferred dates and room type. Our team will assist you promptly.",
        "policies": "Check-in: 3:00 PM, Check-out: 11:00 AM. Cancellations must be made 24 hours in advance.",
        "contact": "Phone: (555) 123-4567 | Email: reservations@pchotel.com | Address: 123 Luxury Avenue, Downtown City, State 12345"
    },
    "location": "Located in the heart of downtown, just minutes from major attractions and business districts."
}

# NLP functions
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    try:
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
    except:
        # Fallback if NLTK fails
        tokens = text.split()
    return tokens

def classify_intent(tokens):
    # Special cases
    if "amenities" in tokens:
        return "amenities"
    if "goodbye" in tokens or "bye" in tokens:
        return "goodbye"
    if "available" in tokens and "room" in tokens and "amenities" not in tokens:
        return "booking"
    
    keywords = {
        "greeting": ["hello", "hi", "hey", "good", "morning", "afternoon", "evening", "welcome"],
        "prices": ["price", "prices", "cost", "how much", "rate", "rates", "expensive", "cheap", "affordable"],
        "amenities": ["amenities", "wifi", "internet", "ac", "air conditioning", "breakfast", "parking", "pool", "swimming pool", "gym", "fitness", "service", "concierge", "spa", "business center", "available"],
        "booking": ["book", "booking", "reserve", "reservation", "availability", "available", "check", "contact", "how to", "phone", "email", "policies", "check-in", "check-out", "are", "do you have"],
        "room_types": ["room", "rooms", "single", "double", "deluxe", "suite", "types", "options"],
        "location": ["location", "where", "address", "near", "close", "distance"],
        "goodbye": ["bye", "goodbye", "see you", "thanks", "thank you"]
    }
    
    intent_scores = {}
    for intent, keys in keywords.items():
        score = sum(1 for token in tokens if any(key in token for key in keys))
        intent_scores[intent] = score
    
    best_intent = max(intent_scores, key=intent_scores.get)
    return best_intent if intent_scores[best_intent] > 0 else "general"

def generate_response(intent, tokens, original_text):
    if intent == "greeting":
        return f"Hello! Welcome to {hotel_data['name']}. I'm here to assist you with information about our hotel. How can I help you today?"
    
    elif intent == "room_types":
        rooms = hotel_data["rooms"]
        response = f"At {hotel_data['name']}, we offer the following room types:\n\n"
        for room, details in rooms.items():
            response += f"• **{room.capitalize()} Room**: {details['description']}\n"
            response += f"  - Capacity: {details['capacity']} guest(s)\n"
            response += f"  - Price: ${details['price']} per night\n"
            response += f"  - Features: {', '.join(details['features'])}\n\n"
        response += "All rooms include complimentary WiFi and access to our full range of amenities."
        return response.strip()
    
    elif intent == "prices":
        rooms = hotel_data["rooms"]
        response = f"Here are our current room rates at {hotel_data['name']}:\n\n"
        for room, details in rooms.items():
            response += f"• {room.capitalize()} Room: ${details['price']} per night\n"
        response += "\nPrices are subject to change based on season and availability. Please contact us for the best rates."
        return response.strip()
    
    elif intent == "amenities":
        amenities = hotel_data["amenities"]
        response = f"{hotel_data['name']} offers a comprehensive range of amenities to ensure your stay is comfortable and enjoyable:\n\n"
        for amenity in amenities:
            response += f"• {amenity}\n"
        return response
    
    elif intent == "booking":
        booking = hotel_data["booking"]
        response = ""
        if any(word in original_text.lower() for word in ["how to", "book", "reserve"]):
            response = booking["how_to_book"]
        elif any(word in original_text.lower() for word in ["available", "availability"]) and any(word in original_text.lower() for word in ["room", "rooms", "are", "do you have"]) and "amenities" not in original_text.lower():
            response = "Yes, we have rooms available! Please contact our reservations team to check availability for your preferred dates and make a booking."
        elif "availability" in original_text.lower() or "check" in original_text.lower():
            response = booking["check_availability"]
        elif "policies" in original_text.lower() or "check-in" in original_text.lower() or "check-out" in original_text.lower():
            response = booking["policies"]
        elif "contact" in original_text.lower() or "phone" in original_text.lower() or "email" in original_text.lower():
            response = booking["contact"]
        else:
            response = f"For booking assistance, please contact our reservations team at {booking['contact'].split(' | ')[0].split(': ')[1]} or visit our website."
        return response
    
    elif intent == "location":
        return f"{hotel_data['name']} is {hotel_data['location']} For detailed directions, please visit our website or contact us at {hotel_data['booking']['contact'].split(' | ')[0].split(': ')[1]}."
    
    elif intent == "goodbye":
        return f"Thank you for considering {hotel_data['name']}. We look forward to welcoming you soon! If you have any other questions, feel free to ask."
    
    else:
        return "I'm sorry, I didn't quite understand your question. I'm here to help with information about our rooms, prices, amenities, booking, and location. Could you please rephrase your question?"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    tokens = preprocess_text(user_message)
    intent = classify_intent(tokens)
    response = generate_response(intent, tokens, user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)