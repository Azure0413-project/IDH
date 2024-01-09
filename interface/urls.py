from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:area>', views.index, name='index'),
    path('get_detail/<str:area>/<str:bed>/<int:idh>', views.get_detail, name='get_detail'),
    path('get_nurse_detail/<str:bed>/<int:idh>', views.get_nurse_detail, name='get_nurse_detail'),
    path('get_record/<int:shift>', views.get_record, name='get_record'),
    path('post_feedback/', views.post_feedback, name='post_feedback'),
    path('warningFeedback/', views.warning_feedback, name='warningFeedback'),
    path('export_file/', views.export_file, name='export_file'),
]