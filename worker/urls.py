from django.urls import path
from . import views


urlpatterns = [
    path('dashbord/',views.dashboard,name='dashboard'),
    path('',views.home,name='about'),


    path('workers/', views.add_delete_worker_view, name='add_worker'),
    path('workers/delete/<int:worker_id>/', views.delete_worker_view, name='delete_worker'),
    path('attendance/', views.mark_attendance_view, name='mark_attendance'),
    path('monthly-salary/', views.monthly_salary_view, name='monthly_salary'),
    path('mark-paid/<int:worker_id>/', views.mark_paid_view, name='mark_paid'),




]
