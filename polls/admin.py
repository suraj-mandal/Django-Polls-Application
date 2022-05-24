from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Question, Choice, PollUser


# Register your models here.
# register the models to the django admin

class PollUserInline(admin.StackedInline):
    model = PollUser
    can_delete = False
    verbose_name_plural = "poll users"


class UserAdmin(BaseUserAdmin):
    inlines = (PollUserInline,)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'user', 'pub_date', 'was_published_recently']
    list_filter = ['pub_date', 'user']
    search_fields = ['question_text']
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date Information', {'fields': ['pub_date']})
    ]
    inlines = [ChoiceInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Question, QuestionAdmin)
