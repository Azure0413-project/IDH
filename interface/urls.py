from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:area>', views.index, name='index'),
    path('NASearch/<str:nurseId>/<str:bedList>', views.NurseAreaSearch, name='NurseAreaSearch'),
    path('get_detail/<str:area>/<str:bed>/<int:idh>', views.get_detail, name='get_detail'),
    path('get_nurse_detail/<str:nurseId>/<str:bed>/<int:idh>', views.get_nurse_detail, name='get_nurse_detail'),
    path('get_record/<int:shift>', views.get_record, name='get_record'),
    path('post_feedback/', views.post_feedback, name='post_feedback'),
    path('warningFeedback/', views.warning_feedback, name='warningFeedback'),
]