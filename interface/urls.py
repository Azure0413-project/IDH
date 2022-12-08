from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:area>', views.index, name='index'),
    path('get_detail/<str:area>/<str:bed>/<int:idh>', views.get_detail, name='get_detail'),
    path('get_record/', views.get_record, name='get_record'),
    path('get_record/<str:bed>', views.get_detail_idh, name='get_detail_idh'),
]