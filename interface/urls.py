from django.urls import path
from interface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('NurseArea/NurseList', views.NurseList, name='NurseList'),
    path('NurseArea/DeleteNurse', views.DeleteNurse, name='DeleteNurse'),
    path('<str:area>', views.index, name='index'),
    path('NASearch/<str:nurseId>/<str:bedList>', views.NurseAreaSearch, name='NurseAreaSearch'),
    path('NAadjust/<str:nurseId>', views.NurseAreaAdjust, name='NurseAreaSearch'),
    path('get_detail/<str:area>/<str:bed>/<int:idh>', views.get_detail, name='get_detail'),
    path('get_nurse_detail/<str:nurseId>/<str:bed>/<int:idh>', views.get_nurse_detail, name='get_nurse_detail'),
    path('get_record/<int:shift>', views.get_record, name='get_record'),
    path('post_feedback/', views.post_feedback, name='post_feedback'),
    path('warning_click/<str:bed>/<int:name>', views.warning_click, name='warning_click'),
    path('warningFeedback/', views.warning_feedback, name='warningFeedback'),
    path('export_file/', views.export_file, name='export_file'),
]