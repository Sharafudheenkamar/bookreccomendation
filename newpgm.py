import os
import django
import random
import requests
from faker import Faker
from myapp.models import BookRecommendation  # Change 'myapp' to your actual app name
from django.core.files.base import ContentFile

# Initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # Change 'myproject' to your project name
django.setup()

# Initialize Faker
fake = Faker()

# Predefined genres
GENRES = ['Fiction', 'Mystery', 'Science Fiction', 'Fantasy', 'Romance', 'Horror', 'Biography', 'History', 'Self-Help']

# Predefined sentiments
SENTIMENTS = ['positive', 'negative', 'neutral']

# Function to fetch a random book cover image
def get_random_image():
    try:
        response = requests.get("https://picsum.photos/200/300", stream=True)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"book_{random.randint(1,1000)}.jpg")
    except Exception as e:
        print(f"Error fetching image: {e}")
    return None

# Generate and save 100 book records
for _ in range(100):
    book = BookRecommendation(
        sentiment=random.choice(SENTIMENTS),
        book_title=fake.sentence(nb_words=4),  # Generate a random book title
        genre=random.choice(GENRES),
        author=fake.name(),
        description=fake.paragraph(nb_sentences=5),
        review=round(random.uniform(1.0, 5.0), 1),  # Random float between 1.0 and 5.0
    )

    # Fetch and attach an image
    image_file = get_random_image()
    if image_file:
        book.bookcoverimage.save(image_file.name, image_file, save=False)

    book.save()

print("✅ 100 books successfully created!")
