from django.urls import path
from . import views

app_name = 'escrow'

urlpatterns = [
    path('wallet/', views.wallet_view, name='wallet'),
    path('fund/<int:booking_id>/', views.fund_escrow, name='fund'),
    path('release/<int:booking_id>/', views.release_escrow, name='release'),
    path('refund/<int:booking_id>/', views.refund_escrow, name='refund'),
]
