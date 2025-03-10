from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BookRecommendation, Login, PredefinedQuestion
import google.generativeai as genai
from textblob import TextBlob
import json
from django.views import View




class LoginPage(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self,request):
        username=request.POST['username']
        password=request.POST['password']
        print(username,password)
        try:
            login_obj=Login.objects.filter(username=username,password=password).first()
            print(login_obj)
            print(login_obj.usertype)
            request.session['userid']=login_obj.id
            if login_obj.usertype=="admin":
                return HttpResponse ('''<script>alert("welcome to adminhome");window.location="/AdminPage"</script>''')
            elif login_obj.usertype=="user":
                return HttpResponse(f'''<script>alert("Welcome to {login_obj.username}");window.location="/user-home/"</script>''')        
        except:
            return HttpResponse ('''<script>alert("invalid user");window.location="/"</script>''')

from django.contrib.auth import logout
class SignupView(View):
    template_name = 'signup.html'

    def get(self, request):
        form = SignupForm()  # Display an empty form for GET requests
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)  # Bind form data for POST requests
        if form.is_valid():
            # Save the user to the database
            user = Login(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],  # In a real app, hash the password

            )
            user.save()
            return redirect('LoginPage')  # Redirect to the login page after successful signup
        return render(request, self.template_name, {'form': form})
class LogoutPage(View):
    def get(self, request):
        logout(request)
        return HttpResponse('''<script>alert("Logged out successfully");window.location="/"</script>''')
class UserHomeView(View):
    template_name = 'user_home.html'

    def get(self, request):
        return render(request, self.template_name)


class AdminPage(View):
    def get(self, request):
        return render(request, "adminhomepage.html")
# # Initialize Google Gemini API
# genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)

# def get_gemini_response(prompt):
#     """Generates chatbot response using Google Gemini API"""
#     try:
#         model = genai.GenerativeModel("gemini-pro")
#         response = model.generate_content(prompt)
#         return response.text.strip() if response else "Sorry, I couldn't process that."
#     except Exception as e:
#         return f"Error: {str(e)}"
import json
from django.shortcuts import render
from django.http import JsonResponse
from textblob import TextBlob
from django.contrib.auth.models import User
from .models import PredefinedQuestion, Chat

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text using TextBlob.
    """
    if not text:
        return "No text provided for sentiment analysis."
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Get polarity score (-1 to 1)

    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"
# def recommend_books(sentiment):
#     """ Recommend books based on sentiment """
#     # Map sentiment to genres
#     sentiment_to_genre = {
#         "positive": ["Motivational", "Self-Help", "Inspirational"],
#         "negative": ["Self-Help", "Inspirational", "Psychology"],
#         "neutral": ["Fiction", "Non-Fiction", "Bestseller"]
#     }

#     # Get genres for the given sentiment
#     genres = sentiment_to_genre.get(sentiment, ["Fiction"])  # Default to Fiction if sentiment is unknown

#     # Query books in the recommended genres
#     recommended_books = BookRecommendation.objects.filter(genre__in=genres).order_by('-review')[:5]  # Top 5 books
#     return recommended_books

def recommend_books(sentiment):
    """Recommend books based on sentiment."""
    print("sentiment")
    sentiment_to_genre = {
        "positive": ["Motivational", "Self-Help", "Inspirational"],
        "negative": ["Self-Help", "Inspirational", "Psychology"],
        "neutral": ["Fiction", "Non-Fiction", "Bestseller"]
    }

    genres = sentiment_to_genre.get(sentiment, ["Fiction"])  # Default to Fiction if sentiment is unknown

    recommended_books = BookRecommendation.objects.filter(genre__in=genres).first()
    print(recommended_books)



    # # Convert to JSON-friendly format
    # books_data = [
    #     {
    #         "title": book.book_title,
    #         "author": book.author,
    #         "description": book.description,
    #         "review": book.review,
    #         "cover_image": book.bookcoverimage.url if book.bookcoverimage else None
    #     }
    #     for book in recommended_books
    # ]
    return recommended_books
def recommended_books_view(request):
    sentiment = request.GET.get('sentiment', 'neutral')  
    print(f"🔍 Sentiment received in view: {sentiment}")  # Debugging  

    books = recommend_books(sentiment)  
    # print(f"📚 Books fetched from DB: {list(books.values('book_title', 'genre', 'review'))}")  # Debugging  

    return render(request, 'recommended_books.html', {'books': books, 'sentiment': sentiment})
import google.generativeai as genai
import os

# Load your Gemini API key (Ensure you set it in your environment variables)


# os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
# Configure Gemini API

# model = genai.GenerativeModel("gemini-pro")
GEMINI_API_KEY = "AIzaSyAFUPQxrIFWVoN71Uru0OoNRuuovKH7wYI"
genai.configure(api_key=GEMINI_API_KEY)
# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_question(user_message, last_recommended_book=None):
    """
    Generates a follow-up question based on the user's message and last recommended book.
    """
    try:
        prompt = f"""
        The user said: "{user_message}".
        If a book was recommended, ask a related question about it.
        Otherwise, ask a general question about books and mood.
        Recommended Book: {last_recommended_book if last_recommended_book else 'None'}
        """
        
        response = model.generate_content(prompt)

        if response and response.candidates:
            generated_text = response.candidates[0].content.parts[0].text
            return generated_text.strip()
        else:
            return "Can you tell me more about that book?"
    
    except Exception as e:
        print(f"Error generating question: {e}")
        return "I didn't quite get that. Could you elaborate?"

def chat_view(request):
    if request.method == 'POST':
            try:
                user_message = json.loads(request.body)
                message = user_message.get('message', '')

                if not message:
                    return JsonResponse({'error': 'No message provided'}, status=400)

                if 'responses' not in request.session:
                    request.session['responses'] = []

                request.session['responses'].append(message)
                request.session.modified = True  

                # Set the required number of responses dynamically
                required_responses = 4  # Adjust as needed

                if len(request.session['responses']) >= required_responses:
                    combined_responses = " ".join(request.session['responses'])
                    sentiment = analyze_sentiment(combined_responses)
                    del request.session['responses']  

                    if request.session.get('userid'):
                        user = Login.objects.get(id=request.session['userid'])
                        Chat.objects.create(user=user, message=combined_responses, response=sentiment)

                    # recommended_books = recommend_books(sentiment)
                    # book_titles = [book.book_title for book in recommended_books]
                    # bot_response = f"Based on your sentiment ({sentiment}), we recommend: {', '.join(book_titles)}"

                    # return JsonResponse({'response': bot_response})
                    # recommended_books = recommend_books(sentiment)
                    return JsonResponse({"redirect_url": f"/recommended-books/?sentiment={sentiment}"})


                    return JsonResponse({'sentiment': sentiment, 'books': recommended_books})
                    

                
                else:
                    # Generate next question using Gemini
                    next_question = get_gemini_question(message)
                    print("vvv",next_question)

                    if request.session.get('userid'):
                        user = Login.objects.get(id=request.session['userid'])
                        Chat.objects.create(user=user, message=message, response=next_question)

                    return JsonResponse({'message': next_question})

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    else:
        # Fetch the first predefined question
        first_question = PredefinedQuestion.objects.first()
        bot_response = first_question.text if first_question else "Hello!"
        
        # Fetch chat history for the logged-in user
        chat_history = []
        if request.session['userid']:
            user=Login.objects.get(id=request.session['userid'])
            chat_history = Chat.objects.filter(user=user).order_by('created_at')
        
        return render(request, 'chat.html', {
            'bot_response': bot_response,
            'chat_history': chat_history
        })


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import BookRecommendation
from .forms import BookRecommendationForm, SignupForm

class BookRecommendationCreateView(View):
    template_name = 'book_recommendation_form.html'

    def get(self, request):
        form = BookRecommendationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = BookRecommendationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_recommendation_list')
        return render(request, self.template_name, {'form': form})

class BookRecommendationUpdateView(View):
    template_name = 'book_recommendation_formedit.html'

    def get(self, request, pk):
        book = get_object_or_404(BookRecommendation, pk=pk)
        form = BookRecommendationForm(instance=book)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        book = get_object_or_404(BookRecommendation, pk=pk)
        form = BookRecommendationForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_recommendation_list')
        return render(request, self.template_name, {'form': form})

class BookRecommendationDeleteView(View):
    template_name = 'book_delete.html'

    def get(self, request, pk):
        book = get_object_or_404(BookRecommendation, pk=pk)
        return render(request, self.template_name, {'book': book})

    def post(self, request, pk):
        book = get_object_or_404(BookRecommendation, pk=pk)
        book.delete()
        return redirect('book_recommendation_list')
    
    # views.py
class BookRecommendationListView(View):
   

    def get(self, request):
        books = BookRecommendation.objects.all()
        return render(request,'book_recommendation_list.html', {'books': books})
    

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import PredefinedQuestion
from .forms import PredefinedQuestionForm

class PredefinedQuestionListView(View):
    def get(self, request):
        questions = PredefinedQuestion.objects.all()
        return render(request, 'predefined_question_list.html', {'questions': questions})

class PredefinedQuestionCreateView(View):
    def get(self, request):
        form = PredefinedQuestionForm()
        return render(request, 'predefined_question_form.html', {'form': form})

    def post(self, request):
        form = PredefinedQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('predefined_question_list')
        return render(request, 'predefined_question_form.html', {'form': form})

class PredefinedQuestionUpdateView(View):
    def get(self, request, pk):
        question = get_object_or_404(PredefinedQuestion, pk=pk)
        form = PredefinedQuestionForm(instance=question)
        return render(request, 'predefined_question_form.html', {'form': form})

    def post(self, request, pk):
        question = get_object_or_404(PredefinedQuestion, pk=pk)
        form = PredefinedQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('predefined_question_list')
        return render(request, 'predefined_question_form.html', {'form': form})

class PredefinedQuestionDeleteView(View):
    def get(self, request, pk):
        question = get_object_or_404(PredefinedQuestion, pk=pk)
        return render(request, 'predefined_delete.html', {'question': question})

    def post(self, request, pk):
        question = get_object_or_404(PredefinedQuestion, pk=pk)
        question.delete()
        return redirect('predefined_question_list')
    

# View to fetch chat history
def chat_history(request):
        # Fetch chat history for the logged-in user
        user=request.session['userid']
        chats = Chat.objects.filter(user__id=user).order_by('created_at')
        history = []
        for chat in chats:
            history.append({
                'sender': 'user',
                'message': chat.message
            })
            history.append({
                'sender': 'bot',
                'message': chat.response
            })
        return JsonResponse({'history': history})


from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import BookRecommendation, Review
from .forms import ReviewForm

class BookListView(View):
    template_name = 'book_list.html'

    def get(self, request, *args, **kwargs):
        books = BookRecommendation.objects.all()
        return render(request, self.template_name, {'books': books})

class BookReviewView(View):
    template_name = 'book_review.html'

    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(BookRecommendation, id=book_id)
        form = ReviewForm()
        return render(request, self.template_name, {'book': book, 'form': form})

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(BookRecommendation, id=book_id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user  # Assuming the user is authenticated
            review.save()
            return redirect('book_list')  # Redirect to the book list page after submission
        return render(request, self.template_name, {'book': book, 'form': form})


import pandas as pd
from django.shortcuts import render
from django.views import View
import pickle
import numpy as np
popular_df = pd.read_pickle('popular.pkl')
pt=pd.read_pickle('pt.pkl')
books=pd.read_pickle('books.pkl')
similarity_scores=pd.read_pickle('similarity_scores.pkl')
# Load pickle files
# popular_df = pickle.load(open('popular.pkl', 'rb'))
# pt = pickle.load(open('pt.pkl', 'rb'))
# books = pickle.load(open('books.pkl', 'rb'))
# similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
class IndexView(View):
    def get(self, request):
        books_data = zip(
            popular_df['Book-Title'].values,
            popular_df['Book-Author'].values,
            popular_df['Image-URL-M'].values,
            popular_df['num_ratings'].values,
            popular_df['avg_rating'].values
        )
        
        context = {'books_data': books_data}
        return render(request, 'index.html', context)
class RecommendView(View):
    def get(self, request):
        return render(request, 'recommend.html')

    def post(self, request):
        user_input = request.POST.get('user_input')

        if user_input not in pt.index:
            return render(request, 'recommend.html', {'error': 'Book not found in database'})

        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
            data.append({
                'title': temp_df['Book-Title'].values[0],
                'author': temp_df['Book-Author'].values[0],
                'image': temp_df['Image-URL-M'].values[0]
            })

        return render(request, 'recommend.html', {'data': data})


    from django.shortcuts import render, redirect
from django.views import View
from .models import PuzzleGame

class PuzzleView(View):
    def get(self, request, level=1):
        """Render the puzzle game page."""
        puzzle, created = PuzzleGame.objects.get_or_create(level=level)
        return render(request, "puzzle.html", {"level": level})

    def post(self, request, level):
        """Handle puzzle completion & redirect to next level."""
        puzzle = PuzzleGame.objects.get(level=level)
        puzzle.completed = True
        puzzle.save()
        return redirect("puzzle", level=level + 1)

from django.shortcuts import render, redirect
from django.views import View
from .models import Review
from .forms import ReviewForm

class ReviewView(View):
    def get(self, request):
        form = ReviewForm()
        reviews = Review.objects.all()
        return render(request, 'reviews.html', {'form': form, 'reviews': reviews})

    def post(self, request):
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('review_page')  # Redirect to the same page after submission
        reviews = Review.objects.all()
        return render(request, 'reviews.html', {'form': form, 'reviews': reviews})
