import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Simple stop words
stop_words = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "wasn't", 'won', "won't", 'wouldn', "wouldn't"
])

def preprocess(text):
    tokens = text.lower().split()
    tokens = [t for t in tokens if t.isalnum()]
    tokens = [t for t in tokens if t not in stop_words]
    return " ".join(tokens)

data = [
    {"question": "What room types are available?",
     "answer": "We offer Standard, Deluxe, Executive Suite, Family Suite."},

    {"question": "What is the price of standard room?",
     "answer": "Standard room costs 50 USD per night."},

    {"question": "What is the price of deluxe room?",
     "answer": "Deluxe room costs 80 USD per night."},

    {"question": "What amenities are available?",
     "answer": "We provide WiFi, AC, TV, Room Service, Breakfast."},

    {"question": "Is breakfast included?",
     "answer": "Yes, breakfast is free for all guests."},

    {"question": "How can I book a room?",
     "answer": "You can book through website or call reception."}
]

questions = [preprocess(item["question"]) for item in data]
answers = [item["answer"] for item in data]

model = SentenceTransformer("all-MiniLM-L6-v2")
question_vectors = model.encode(questions)

dimension = question_vectors.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(np.array(question_vectors))

def get_answer(query):
    query = preprocess(query)
    query_vec = model.encode([query])

    D, I = index.search(np.array(query_vec), k=1)

    return answers[I[0][0]]