from django.db import models
from django.contrib.auth.models import User
from core.models import Customer, Agent


class Profile(models.Model):
    ROLES = [('Customer', 'Customer'),
             ('Agent', 'Agent'),
             ('Owner', 'Owner')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    customer = models.OneToOneField(Customer, 
                                    on_delete=models.PROTECT,
                                    null=True,
                                    blank=True,
                                    related_name='profile')

    agent = models.OneToOneField(Agent,
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True,
                                 related_name='profile')
    

    role = models.CharField(choices=ROLES,
                            max_length=10,
                            default='Customer')

    def __str__(self):
        return self.user.username