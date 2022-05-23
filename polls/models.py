import datetime

from django.db import models
from django.contrib import admin
from django.utils import timezone


# Create your models here.

# question model here represents a question in the poll
class Question(models.Model):
    question_text = models.CharField(max_length=200, null=False)
    pub_date = models.DateTimeField('date published')

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published Recently',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - timezone.timedelta(days=1) <= self.pub_date <= now

    def __repr__(self):
        return self.question_text.lower()

    def __str__(self):
        return self.question_text


# list of choices for each question in the poll"
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, null=False)
    votes = models.IntegerField(default=0)

    def __repr__(self):
        return self.choice_text.lower()

    def __str__(self):
        return self.choice_text
