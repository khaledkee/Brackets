import os

from datetime import datetime
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseBadRequest
from django.conf import settings
from .models import problem, submission, contest, userinfo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .judge import start_judge
from django.db.models import Q


# Create your views here.
def problemView(request, problem_id, contest_id=None):
    current_problem = get_object_or_404(problem, id=problem_id)
    samples = []
    try:
        for i in range(1, current_problem.samples + 1):
            file_name = str(i)
            while len(file_name) < 3:
                file_name = '0' + file_name
            file_name = 'test' + file_name
            print(settings.STATIC_ROOT + 'problems\\' + str(problem_id) + '\\' + file_name + '.in')
            with open(settings.STATIC_ROOT + '/problems/' + str(problem_id) + '/' + file_name + '.in') as input_file:
                sample_input = input_file.readlines()
            with open(settings.STATIC_ROOT + '/problems/' + str(problem_id) + '/' + file_name + '.out') as output_file:
                sample_output = output_file.readlines()
            samples.append({'input': sample_input, 'output': sample_output})
        context = {'problem': current_problem, 'samples': samples}
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


def postSubmitView(request, problem_id=None, contest_id=None):
    if problem_id is not None:
        current_problem = get_object_or_404(problem, id=problem_id,  start_date__lte=datetime.now())
        if contest_id is not None and current_problem.contest_id != contest_id:
            return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    else:
        current_problem = {'id': 0, 'title': 'Custom test', 'time_limit': 100, 'memory_limit': 64}
    source_code = request.POST.get("source", "")
    if source_code is None or len(source_code) > 5000:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    current_userinfo = get_object_or_404(userinfo, UserModel__id=request.user.id)
    not_judges_submissions = len(submission.objects.filter(status='QU', user__id=request.user.id))
    if not_judges_submissions >= 5 or (current_userinfo.last_submit is not None and (
            current_userinfo.last_submit - datetime.now()).total_seconds() > -30):
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    current_userinfo.last_submit = datetime.now()
    current_userinfo.save()
    new_submission = submission.objects.create(user_id=request.user.id, problem_id=problem_id, status='QU',
                                               code=source_code, problem=current_problem)
    new_submission.save()
    start_judge(new_submission)
    try:
        return redirect(('%s/user/' + str(request.user.id) + '/submissions') % (
        '/contest/' + str(contest_id) if contest_id is not None else ''))
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def submitView(request, problem_id=None, contest_id=None):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    if request.method == 'POST':
        return postSubmitView(request, problem_id, contest_id)
    return getSubmitView(request, problem_id, contest_id)


def submissionView(request, page_id=1, contest_id=None, user_id=None):
    if contest_id is not None:
        contestObj = get_object_or_404(contest, id=contest_id, start_date__lte=datetime.now())
        if user_id is None:
            submissions_list = submission.objects.filter(problem__contest__id=contest_id)
        else:
            submissions_list = submission.objects.filter(problem__contest__id=contest_id, user__id=user_id)
    else:
        if user_id is None:
            submissions_list = submission.objects.all()
        else:
            submissions_list = submission.objects.filter(user__id=user_id)
        contestObj = None
    submissions_list = submissions_list.order_by('submitted').reverse()
    try:
        paginator = Paginator(submissions_list, 20)
        try:
            submissions_list = paginator.page(page_id)
        except PageNotAnInteger:
            submissions_list = paginator.page(1)
        except EmptyPage:
            submissions_list = paginator.page(paginator.num_pages)
        return render(request, 'submissions.html', {'submissions': submissions_list, 'contest': contestObj})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def dashboardView(request, contest_id):
    current_contest = get_object_or_404(contest, id=contest_id, start_date__lte=datetime.now())
    problems = current_contest.problem_set.all()
    try:
        return render(request, 'dashboard.html', {'contest': current_contest, 'problems': problems})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')


def problemsView(request):
    problems = problem.objects.filter(Q(contest=None) | Q(contest__start_date__lte=datetime.now()))
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

def get_acs(user_dict):
    num_ac = 0
    for _, score in user_dict.items():
        num_ac += 1 if score > 0 else 0
    return num_ac


def sort_on_acs(user_dict):
    return user_dict[1]['bracketsscore']


def scoreboardView(request, contest_id):
    current_contest = get_object_or_404(contest,id = contest_id)
    problems = problem.objects.filter(contest_id=contest_id)
    submissions = submission.objects.filter(problem__contest_id = contest_id).order_by('submitted')
    users_dict = {}
    for user_submission in submissions:
        if str(user_submission.user) not in users_dict:
            users_dict[str(user_submission.user)] = {}
        if str(user_submission.problem) not in users_dict[str(user_submission.user)]:
            users_dict[str(user_submission.user)][str(user_submission.problem)] = 0
        if users_dict[str(user_submission.user)][str(user_submission.problem)] > 0:
            continue
        if user_submission.status == 'AC':
            users_dict[str(user_submission.user)][str(user_submission.problem)] = abs(users_dict[str(user_submission.user)][str(user_submission.problem)]) + 1
        else:
            users_dict[str(user_submission.user)][str(user_submission.problem)] -= 1
    for user_name, user_dict in users_dict.items():
        users_dict[user_name]['bracketsscore'] = get_acs(user_dict)
    users_dict = dict(sorted(users_dict.items(), key=sort_on_acs, reverse=True))
    try:
        return render(request, 'scoreboard.html', {'contest': current_contest, 'problems': problems, 'scoreboard': users_dict})
    except:
        return HttpResponseBadRequest('Your request is bad and you should feel bad!')
    
    