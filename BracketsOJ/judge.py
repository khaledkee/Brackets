import os
from threading import Thread, Lock
from BracketsOJ import parser
from django.conf import settings
from datetime import datetime
from .models import user_score, contest


#checkers
def exact_cmp(input_stream, ans, out):
    return str(ans).strip() == str(out).strip()


locks = [Lock() for i in range(0,100)]
checkers = {'ecmp': exact_cmp}


class asyncJudge(Thread):
    def __init__(self, new_submission):
        self.submission = new_submission
        super(asyncJudge, self).__init__()

    def run(self):
        locks[self.submission.problem_id].acquire()
        problem = self.submission.problem
        tl = problem.time_limit
        ml = problem.memory_limit
        code = self.submission.code
        checker = checkers[problem.checker]
        if checker is None:
            raise EnvironmentError("Checker not found")
        self.submission.time = 0
        self.submission.memory = 0
        test_index = 0
        while True:
            test_index += 1
            file_name = str(test_index)
            while len(file_name) < 3 :
                file_name = '0' + file_name
            file_name = 'test' + file_name
            if os.path.isfile(settings.STATIC_ROOT + '\\problems\\' + str(problem.id) + '\\'+ file_name+'.in'):
                with open(os.path.join(settings.STATIC_ROOT,
                                       'problems\\' + str(problem.id) + '\\'+ file_name+'.in')) as input_file:
                    input_stream = '\n'.join(input_file.readlines())

                    new_parser = parser.Parser(code, tl, ml, input_stream)
                    verdict = new_parser.Start()
                    self.submission.time = max(self.submission.time, new_parser.Instructions)
                    self.submission.memory = max(self.submission.time, len(new_parser.Memory_data_segment) + len(new_parser.Code_segment))
                    if verdict == 'TL':
                        self.submission.status = 'TL'
                        break
                    elif verdict == 'ML':
                        self.submission.status = 'ML'
                        break
                    elif verdict is False:
                        self.submission.status = 'CE'
                        break
                    with open(os.path.join(settings.STATIC_ROOT,
                                           'problems\\' + str(problem.id) + '\\' + file_name + '.out')) as output_file:
                        ans = ''.join(output_file.readlines())
                        if checker(input_stream, ans, verdict[2]):
                            self.submission.status = 'AC'
                        else:
                            self.submission.status = 'WA'
                            break
            else:
                break
        locks[self.submission.problem_id].release()
        self.submission.judged = datetime.now()
        self.submission.save()
        if self.submission.status == 'AC':
            current_contest = contest.objects.get(contest__id=problem.contest_id)
            if (datetime.now() - current_contest.start_date).total_seconds() > 0 and (current_contest.end_date - datetime.now()).total_seconds() > 0:
                new_score = user_score.objects.get_or_create(user__id=self.submission.user_id, contest__id=current_contest.id)
                new_score.solved += 1
                new_score.save()



def start_judge(submission):
    t = asyncJudge(submission)
    t.daemon = True
    t.start()
