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
        try:
            login_obj=Login.objects.get(username=username,password=password)
            request.session['userid']=login_obj.id
            if login_obj.usertype=="admin":
                return HttpResponse ('''<script>alert("welcome to adminhome");window.location="/AdminPage"</script>''')
            elif login_obj.usertype=="user":
                return HttpResponse ('''<script>alert("welcome to adminhome");window.location="/user-home/"</script>''')
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
# Initialize Google Gemini API
genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)

def get_gemini_response(prompt):
    """Generates chatbot response using Google Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip() if response else "Sorry, I couldn't process that."
    except Exception as e:
        return f"Error: {str(e)}"
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
    sentiment = blob.sentiment
    return f"Sentiment: Polarity={sentiment.polarity}, Subjectivity={sentiment.subjectivity}"
def recommend_books(sentiment):
    """ Recommend books based on sentiment """
    # Map sentiment to genres
    sentiment_to_genre = {
        "positive": ["Motivational", "Self-Help", "Inspirational"],
        "negative": ["Self-Help", "Inspirational", "Psychology"],
        "neutral": ["Fiction", "Non-Fiction", "Bestseller"]
    }

    # Get genres for the given sentiment
    genres = sentiment_to_genre.get(sentiment, ["Fiction"])  # Default to Fiction if sentiment is unknown

    # Query books in the recommended genres
    recommended_books = BookRecommendation.objects.filter(genre__in=genres).order_by('-review')[:5]  # Top 5 books
    return recommended_books
def chat_view(request):
    if request.method == 'POST':
        try:
            # Parse the JSON payload
            user_message = json.loads(request.body)
            # Extract the 'message' key from the dictionary
            message = user_message.get('message', '')
            print(message)
            
            if not message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Initialize or update session data
            if 'responses' not in request.session:
                request.session['responses'] = []
            
            # Append the user's response to the session
            request.session['responses'].append(message)
            request.session.modified = True  # Ensure the session is saved
            
            # Check if 4 responses have been collected
            if len(request.session['responses']) >= 4:
                # Analyze sentiment for all responses
                combined_responses = " ".join(request.session['responses'])
                sentiment = analyze_sentiment(combined_responses)
                
                # Clear the session after analysis
                del request.session['responses']
                
                # Save the final response to the Chat model
                if request.session['userid']:
                    user=Login.objects.get(id=request.session['userid'])
                    Chat.objects.create(
                        user=user,
                        message=combined_responses,
                        response=sentiment
                    )
                            # Get recommended books based on sentiment
                recommended_books = recommend_books(sentiment)
                book_titles = [book.book_title for book in recommended_books]
                # Return the sentiment analysis result
                            # Return the sentiment analysis result and recommended books
                bot_response = f"Thank you for your responses. Based on your sentiment ({sentiment}), we recommend: {', '.join(book_titles)}"
                return JsonResponse({'response': bot_response})
            
            else:
                # Fetch the next predefined question
                questions = PredefinedQuestion.objects.all()
                next_question_index = len(request.session['responses'])
                if next_question_index < questions.count():
                    next_question = questions[next_question_index].text
                else:
                    next_question = "Thank you for your responses. We will analyze them shortly."
                
                # Save the user's response and bot's question to the Chat model
                if request.session['userid']:
                    user=Login.objects.get(id=request.session['userid'])
                    Chat.objects.create(
                        user=user,
                        message=message,
                        response=next_question
                    )
                
                return JsonResponse({'response': next_question})
        
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