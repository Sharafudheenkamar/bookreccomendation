from django.urls import path
from .views import *

urlpatterns = [
    path("",LoginPage.as_view(),name='LoginPage'),
    path('signup/', SignupView.as_view(), name='signup'), 
    path("AdminPage",AdminPage.as_view(),name='AdminPage'),
    path('user-home/', UserHomeView.as_view(), name='user_home'),

    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/review/', BookReviewView.as_view(), name='book_review'),    # Review page

    path('chat/', chat_view, name='chat'),
    path('LogoutPage',LogoutPage.as_view(),name='LogoutPage'),
    path("chat/history/",chat_history,name='chathistory'),
    path('book/', BookRecommendationListView.as_view(), name='book_recommendation_list'),
    path('book/create/', BookRecommendationCreateView.as_view(), name='book_recommendation_create'),
    path('book/update/<int:pk>/', BookRecommendationUpdateView.as_view(), name='book_recommendation_update'),
    path('book/delete/<int:pk>/', BookRecommendationDeleteView.as_view(), name='book_recommendation_delete'),
    path('PredefinedQuestionListView', PredefinedQuestionListView.as_view(), name='predefined_question_list'),
    path('create/', PredefinedQuestionCreateView.as_view(), name='predefined_question_create'),
    path('update/<int:pk>/', PredefinedQuestionUpdateView.as_view(), name='predefined_question_update'),
    path('delete/<int:pk>/', PredefinedQuestionDeleteView.as_view(), name='predefined_question_delete'),
]
