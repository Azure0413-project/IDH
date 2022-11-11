from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_detail/<str:bed>', views.get_detail, name='get_detail'),
]