from .models import Course, Enrollment, Question, Choice, Submission
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

# Helper function to extract selected choice IDs from the POST request
def extract_answers(request):
    submitted_choices = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            try:
                choice_id = int(value)
                submitted_choices.append(choice_id)
            except ValueError:
                pass
    return submitted_choices

# Submit view
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    choice_ids = extract_answers(request)
    for choice_id in choice_ids:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)
        
    submission_id = submission.id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,)))

# Exam result view
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()

    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = choices.filter(question=question)

        if set(correct_choices) == set(selected_choices):
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)