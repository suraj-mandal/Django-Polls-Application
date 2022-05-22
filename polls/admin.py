from django.contrib import admin
from .models import Question, Choice

# Register your models here.
# register the models to the django admin
admin.site.register(Question)
admin.site.register(Choice)
