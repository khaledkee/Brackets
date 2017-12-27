from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class userinfo(models.Model):
    UserModel = models.ForeignKey(User,on_delete=models.CASCADE)
    rate = models.IntegerField()
    def __str__(self):
        return self.UserModel.username


class contest(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    def __str__(self):
        return self.name


class problem(models.Model):
    title = models.CharField(max_length=50)
    time_limit = models.IntegerField(default=100)
    memory_limit = models.IntegerField(default=64)
    statement = models.CharField(max_length=500)
    input_section = models.CharField(max_length=200)
    output_section = models.CharField(max_length=200)
    samples = models.IntegerField(default=1)
    notes = models.CharField(max_length=200, blank=True, null=True)
    added = models.DateField(auto_now_add=True, blank=True)
    contest = models.ForeignKey(contest, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.title


class submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.IntegerField(null=True,blank=True)
    memory = models.IntegerField(null=True,blank=True)
    submitted = models.DateTimeField(auto_now_add=True, blank=True)
    judged = models.DateTimeField(null=True,blank=True)
    contest = models.ForeignKey(contest,on_delete=models.SET_NULL,null=True,blank=True)
    STATUSES = [
        ('AC', 'Accepted'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('WA', 'Wrong Answer'),
        ('RTE', 'Run Time Error'),
        ('QU', 'In queue'),
    ]
    status = models.CharField(max_length=50, choices=STATUSES, null=True,blank=True)
    score = models.IntegerField(null=True,blank=True)
    code = models.TextField(default="")
    def __str__(self):
        return str(self.id)

