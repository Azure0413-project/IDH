from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_detail/<str:bed>/<int:idh>', views.get_detail, name='get_detail'),
    path('get_record', views.get_record, name='get_record'),
]