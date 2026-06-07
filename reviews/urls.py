from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='list'),
    path('create/<int:booking_id>/', views.review_create, name='create'),
]
