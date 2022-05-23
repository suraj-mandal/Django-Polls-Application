from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


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
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes future questions
        """
        return Question.objects.exclude(choice__isnull=True).filter(pub_date__lte=timezone.now())


# results view that shows results of the current poll application
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/result.html'


# will display votes for a particular question
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
