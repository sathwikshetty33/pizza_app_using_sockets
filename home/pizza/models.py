import json
import random
import string
from secrets import choice

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from django.dispatch import receiver


# Create your models here.
class pizza(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=100)
    image = models.CharField(max_length=100)
    def __str__(self):
        return self.name
def random_string_generator(size=10, chars=string.ascii_lowercase+string.digits):
   return ''.join(random.choice(chars) for _ in range(size))
choices = (
    ("Order Received", "Order Received"),
    ("Baking", "Baking"),
    ("Baked", "Baked"),
    ("Out for delivery", "Out for delivery"),
    ("Order received", "Order received"),
)

class order(models.Model):
    pizza = models.ForeignKey(pizza, on_delete=models.CASCADE)
    user = models.ForeignKey(User,blank=True,null=True, on_delete=models.SET_NULL)
    order_id = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField(default=100)
    status = models.CharField(max_length=100, choices=choices, default="Order received")
    date = models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
        if not len(self.order_id):
            self.order_id = random_string_generator()
        super(order,self).save(*args,**kwargs)

    def __str__(self):
        return self.order_id

    @staticmethod
    def giver_order_details(order_id):
        instance = order.objects.filter(order_id=order_id).first()
        data = {}
        data["order_id"] = instance.order_id
        data["amount"] = instance.amount
        data["status"] = instance.status
        pg = 0
        if instance.status == 'Order Received':
            pg = 20
        if instance.status == 'Baking':
            pg = 40
        if instance.status == 'Baked':
            pg = 60
        if instance.status == 'Out for delivery':
            pg = 80
        if instance.status == 'Order received':
            pg = 100
        data['progress'] = pg
        return data

@receiver(post_save, sender = order)
def order_status_handler(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        data = {}
        data["order_id"] = instance.order_id
        data["amount"] = instance.amount
        data["status"] = instance.status
        pg = 0
        if instance.status == 'Order Received':
            pg = 20
        if instance.status == 'Baking':
            pg = 40
        if instance.status == 'Baked':
            pg = 60
        if instance.status == 'Out for delivery':
            pg = 80
        if instance.status == 'Order received':
            pg = 100
        data['progress'] = pg
        async_to_sync(channel_layer.group_send)(
            'order_%s' % instance.order_id,{
                'type' : 'order_status',
                'value' : json.dumps(data)
            }
        )