from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Question, Choice, PollUser
from .forms import NewUserForm


# register the user
def register_user(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # creating the poll user simultaneously
            # this design is bad
            # needs an overhaul completely
            # creates the PollUser, once the user has been created successfully
            PollUser.objects.create(user=user, email=user.email)
            login(request, user)
            messages.success(request, "Registration successful")
        messages.error(request, "Unsuccessful registration. Invalid information")
    form = NewUserForm()
    return render(request, 'polls/register.html', {'register_form': form})


# login the user into the application
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login Successful")
                print("Hello")
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                return redirect('polls:index')
            messages.error(request, "User doesn't exist")
    form = AuthenticationForm()
    return render(request, 'polls/login.html', {'login_form': form})


# logout the user from the application
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out")
    return redirect('polls:index')


# generic view that displays the list of questions in the poll index
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = 'latest_question_list'
    # implementing pagination here
    paginate_by = 2

    def get_paginate_by(self, queryset):
        # if paginate_by key is not found then set default to the current value
        return self.request.GET.get('paginate_by', self.paginate_by)

    # get the list of query set
    def get_queryset(self):
        """
        Return the last 5 published questions
        """
        return Question.objects.exclude(choice__isnull=True).filter(pub_date__lte=timezone.now()) \
                   .order_by('-pub_date')[:5]


# detail view that displays details of the current question
def question_detail(request, pk):
    question = get_object_or_404(
        Question.objects.exclude(choice__isnull=True).filter(pub_date__lte=timezone.now()), pk=pk)
    if request.user.is_authenticated:
        return render(request, 'polls/detail.html', {'question': question})
    else:
        return redirect(reverse('polls:results', args=(question.id,)))


# results view that shows results of the current poll application
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/result.html'

    def get_queryset(self):
        """
        Excludes future questions
        """
        return Question.objects.exclude(choice__isnull=True).filter(pub_date__lte=timezone.now())


# will display votes for a particular question
# for this function to work the user should be logged in
@login_required(login_url='polls:login')
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice"
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
