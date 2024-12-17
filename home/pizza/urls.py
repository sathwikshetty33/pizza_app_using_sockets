from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('order/<order_id>',views.orderview,name='orders'),
    path('ordercreate/', views.order_create, name='ordercreate'),
]
