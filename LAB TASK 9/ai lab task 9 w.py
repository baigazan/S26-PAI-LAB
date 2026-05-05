from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

texts = [
    "I love this product",
    "This is bad",
    "Amazing experience",
    "Not good",
    "Very happy",
    "I am sad",
    "I am feeling bad",
    "Not feeling well",
    "I hate this",
    "Worst experience ever",
    "I am very sad and depressed"
]

labels = [
    "positive",
    "negative",
    "positive",
    "negative",
    "positive",
    "negative",
    "negative",
    "negative",
    "negative",
    "negative",
    "negative"
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)


model = MultinomialNB()
model.fit(X, labels)

while True:
    user_input = input("\nEnter a sentence (or type 'exit' to stop): ")

    if user_input.lower() == "exit":
        print("Program stopped.")
        break

    test_vec = vectorizer.transform([user_input])

    prediction = model.predict(test_vec)

    print("Sentiment:", prediction[0])