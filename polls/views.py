from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from .models import Question, Choice


# generic view that displays the list of questions in the poll index
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = 'latest_question_list'

    # get the list of query set
    def get_queryset(self):
        return Question.objects.order_by('pub_date')[:5]


# detail view that displays details of the current question
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


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
