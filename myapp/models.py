from django.db import models
from django.db.models import Avg

class Login(models.Model):

  username = models.CharField(max_length=255,null=True,blank=True)
  password= models.CharField(max_length=255,null=True,blank=True)
  usertype=models.CharField(max_length=255,null=True,blank=True,default='user')


class BookRecommendation(models.Model):
    sentiment = models.CharField(max_length=20, choices=[
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral')
    ])
    book_title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100,null=True,blank=True)  
    author = models.CharField(max_length=255)
    description = models.TextField()
    review = models.FloatField(default=0.0)
    bookcoverimage = models.FileField(upload_to='bookcoverimage',null=True,blank=True)  # Stores the average rating

    def update_review(self):
        """ Update the average rating of the book """
        avg_rating = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        self.review = avg_rating if avg_rating else 0.0
        self.save()

    def __str__(self):
        return self.book_title
    def __str__(self):
        return self.book_title
# chat/models.py
from django.db import models

class PredefinedQuestion(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:50]
from django.db import models

class Review(models.Model):
    # book = models.ForeignKey(BookRecommendation, on_delete=models.CASCADE, related_name="reviews",null=True,blank=True)
    bookname=models.CharField(max_length=100,null=True,blank=True) 
    user = models.CharField(max_length=255) 
    # You can link this to a User model if using Django's auth system
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     """ Override save method to update book's review rating """
    #     super().save(*args, **kwargs)
    #     self.book.update_review()

    # def delete(self, *args, **kwargs):
    #     """ Override delete method to update book's review rating """
    #     super().delete(*args, **kwargs)
    #     self.book.update_review()



    def __str__(self):
        return f"Review for {self.book.book_title} by {self.user}"

class Chat(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"
    

from django.db import models

class PuzzleGame(models.Model):
    level = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Puzzle Level {self.level}"