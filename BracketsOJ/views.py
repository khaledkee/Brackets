import os

from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from .models import problem, submission, contest, userinfo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .judge import start_judge
from django.db.models import Q


# Create your views here.
def problemView(request, problem_id, contest_id=None):
    current_problem = get_object_or_404(problem, id=problem_id)
    if contest_id is not None and current_problem.contest_id != contest_id:
        raise SuspiciousOperation()
    samples = []
    try:
        for i in range(1, current_problem.samples + 1):
            file_name = str(i)
            while len(file_name) < 3:
                file_name = '0' + file_name
            file_name = 'test' + file_name
            with open(settings.STATIC_ROOT + '/problems/' + str(problem_id) + '/' + file_name + '.in') as input_file:
                sample_input = input_file.readlines()
            with open(settings.STATIC_ROOT + '/problems/' + str(problem_id) + '/' + file_name + '.out') as output_file:
                sample_output = output_file.readlines()
            samples.append({'input': sample_input, 'output': sample_output})
        context = {'problem': current_problem, 'samples': samples}
        return render(request, 'problem.html', context)
    except:
        raise SuspiciousOperation()


def getSubmitView(request, current_problem):
    context = {'problem': current_problem}
    try:
        return render(request, 'submit.html', context)
    except:
        raise SuspiciousOperation()


def postSubmitView(request, current_problem):
    source_code = request.POST.get("source", "")
    if source_code is None or len(source_code) > 5000:
        raise SuspiciousOperation()
    current_userinfo, created = userinfo.objects.get_or_create(UserModel_id=request.user.id)
    not_judges_submissions = len(submission.objects.filter(status='QU', user__id=request.user.id))
    if not_judges_submissions >= 5 or (current_userinfo.last_submit is not None and abs((
            current_userinfo.last_submit - datetime.now()).total_seconds()) <= 15):
        raise SuspiciousOperation()
    current_userinfo.last_submit = datetime.now()
    current_userinfo.save()
    new_submission = submission.objects.create(user_id=request.user.id, problem_id=current_problem.id, status='QU',
                                               code=source_code)
    new_submission.save()
    start_judge(new_submission)
    try:
        return redirect(('%s/user/' + str(request.user.id) + '/submissions') % (
        '/contest/' + str(current_problem.contest_id) if current_problem.contest_id is not None else ''))
    except:
        raise SuspiciousOperation()


def submitView(request, problem_id=None, contest_id=None):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    if problem_id is not None:
        current_problem = get_object_or_404(problem, id=problem_id)
        if contest_id is not None and current_problem.contest_id != contest_id:
            raise SuspiciousOperation()
    else:
        current_problem = {'id': 0, 'title': 'Custom test', 'time_limit': 100, 'memory_limit': 64}
    if request.method == 'POST':
        return postSubmitView(request, current_problem)
    return getSubmitView(request, current_problem)


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
        raise SuspiciousOperation()


def dashboardView(request, contest_id):
    current_contest = get_object_or_404(contest, id=contest_id, start_date__lte=datetime.now())
    problems = current_contest.problem_set.all()
    try:
        return render(request, 'dashboard.html', {'contest': current_contest, 'problems': problems})
    except:
        raise SuspiciousOperation()


def problemsView(request):
    problems = problem.objects.filter(Q(contest=None) | Q(contest__start_date__lte=datetime.now()))
    try:
        return render(request, 'problems.html', {'problems': problems})
    except:
        raise SuspiciousOperation()


def contestsView(request):
    contests = contest.objects.all()
    try:
        return render(request, 'contests.html', {'contests': contests})
    except:
        raise SuspiciousOperation()

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
    submissions = submission.objects.filter(problem__contest_id = contest_id,submitted__lte=current_contest.end_date,submitted__gte=current_contest.start_date).order_by('submitted')
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
        raise SuspiciousOperation()
    
    