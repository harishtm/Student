from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    age = models.CharField(max_length=255,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=255,blank=True,null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        url = '/student-list/'
        return url
