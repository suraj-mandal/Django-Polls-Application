from django.contrib import admin
from .models import Question, Choice

# Register your models here.
admin.register(Question)
admin.register(Choice)