import os
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseBadRequest
from django.conf import settings
from .models import problem, submission, contest, User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def problemView(request, problem_id, contest_id=None):
    current_problem = get_object_or_404(problem,id=problem_id)
    samples = []
    try:
        for i in range(1,current_problem.samples+1):
            file_name = str(i)
            while len(file_name) < 3 :
                file_name = '0' + file_name
            file_name = 'test' + file_name
            with open(os.path.join(settings.STATIC_ROOT,'problems\\' + str(problem_id) + '\\'+ file_name+'.in')) as input_file:
                sample_input = input_file.readlines()
            with open(os.path.join(settings.STATIC_ROOT, 'problems\\' + str(problem_id) + '\\'+file_name+'.out')) as output_file:
                sample_output = output_file.readlines()
            samples.append({'input': sample_input,'output': sample_output})
        context = {'problem': current_problem,'samples': samples}
        return render(request, 'problem.html', context)
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def getSubmitView(request, problem_id, contest_id=None):
    if problem_id is not None:
        current_problem = get_object_or_404(problem, id=problem_id)
        if contest_id is not None and current_problem.contest_id != contest_id:
            return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    else:
        current_problem = {'id': 0, 'title': 'Custom test', 'time_limit': 100, 'memory_limit': 64}
    context = {'problem': current_problem}
    try:
        return render(request, 'submit.html', context)
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def postSubmitView(request,problem_id=None,contest_if=None):
    source_code = request.POST.get("source", "")
    if source_code is None or len(source_code) > 5000:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    # judge
    return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def submitView(request, problem_id=None, contest_id=None):
    if not request.user.is_authenticated :
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    if request.method == 'POST':
        return postSubmitView(request,problem_id,contest_id)
    return getSubmitView(request,problem_id,contest_id)


def submissionView(request, page_id=1, contest_id=None, user_id=None):
    if contest_id is not None:
        contestObj = get_object_or_404(contest,id=contest_id)
        if user_id is None:
            submissions_list = submission.objects.filter(contest__id=contest_id)
        else:
            submissions_list = submission.objects.filter(contest__id=contest_id, user__id=user_id)
    else:
        if user_id is None:
            submissions_list = submission.objects.all()
        else:
            submissions_list = submission.objects.filter(user__id=user_id)
        contestObj = None
    try:
        paginator = Paginator(submissions_list,20)
        try:
            submissions_list = paginator.page(page_id)
        except PageNotAnInteger:
            submissions_list = paginator.page(1)
        except EmptyPage:
            submissions_list = paginator.page(paginator.num_pages)
        return render(request, 'submissions.html', {'submissions' : submissions_list, 'contest': contestObj})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def dashboardView(request, contest_id):
    current_contest = get_object_or_404(contest,id=contest_id)
    problems = current_contest.problem_set.all()
    try:
        return render(request, 'dashboard.html', {'contest': current_contest, 'problems': problems})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def problemsView(request):
    problems = problem.objects.all()
    try:
        return render(request, 'problems.html', {'problems': problems})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def contestsView(request):
    contests = contest.objects.all()
    try:
        return render(request, 'contests.html', {'contests': contests})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


