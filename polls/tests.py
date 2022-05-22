import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice


def create_question_with_choices(question_text, days):
    time = timezone.now() + timezone.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    question.choice_set.create(choice_text='First choice', votes=0)
    question.choice_set.create(choice_text='Second choice', votes=0)
    question.choice_set.create(choice_text='Third choice', votes=0)
    return question


def create_question_without_choices(question_text, days):
    time = timezone.now() + timezone.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Create your tests here.
# testing the Question model here
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was published_recently() returns False for the questions
        whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was published_recently() returns True for the questions
        whose pubdate is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """
        was published_recently() returns Fasle for the questions
        whose pub_date is more than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        question = create_question_with_choices("This is the past question", -2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        question = create_question_with_choices("This is future question", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_and_future_question(self):
        question = create_question_with_choices("This is the past question", -2)
        create_question_with_choices("This is future question", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_past_two_questions(self):
        question1 = create_question_with_choices("This is the past question", -2)
        question2 = create_question_with_choices("This is the past question", -5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [question1, question2])

    def test_questions_without_choices(self):
        question = create_question_without_choices("Question without choices", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_questions_with_choices(self):
        question = create_question_with_choices("Question with choices", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])


class QuestionDetailViewTests(TestCase):
    def test_with_invalid_question_id(self):
        question = create_question_with_choices("Delete question", days=-5)
        question_id = question.id
        question.delete()
        response = self.client.get(reverse('polls:detail', args=(question_id,)))
        self.assertEqual(response.status_code, 404)

    def test_with_future_question_id(self):
        question = create_question_with_choices("Future question", days=6)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_with_question_without_choices(self):
        question = create_question_without_choices("Question without choices", days=-5)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_with_past_question_with_choices(self):
        question = create_question_with_choices("Question with choices", days=-5)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['question'].question_text, 'Question with choices')
        self.assertEqual(response.context['question'].id, question.id)

    def test_with_future_question_with_choices(self):
        question = create_question_with_choices("Question with choices", days=5)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 404)
