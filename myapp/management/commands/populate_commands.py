from django.core.management.base import BaseCommand
from myapp.models import BookRecommendation

class Command(BaseCommand):
    help = 'Populate BookRecommendation table with sample data'

    def handle(self, *args, **kwargs):
        BookRecommendation.objects.create(
            sentiment="positive",
            book_title="The Power of Positive Thinking",
            author="Norman Vincent Peale",
            description="A guide to positive thinking and success."
        )

        BookRecommendation.objects.create(
            sentiment="negative",
            book_title="Feeling Good: The New Mood Therapy",
            author="David D. Burns",
            description="A cognitive therapy approach to overcoming depression."
        )

        BookRecommendation.objects.create(
            sentiment="neutral",
            book_title="Thinking, Fast and Slow",
            author="Daniel Kahneman",
            description="An exploration of how humans think and make decisions."
        )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with book recommendations.'))
