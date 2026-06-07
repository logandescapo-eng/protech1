from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from bookings import views as booking_views
from escrow import views as escrow_views
from reviews import views as review_views
from users import views as user_views

from . import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', project_views.health, name='health'),

    path('', user_views.home, name='index'),
    path('auth/', user_views.auth_view, name='auth'),
    path('logout/', user_views.logout_view, name='logout'),
    path('user/dashboard/', user_views.user_dashboard, name='user_dashboard'),
    path('worker/dashboard/', user_views.worker_dashboard, name='worker_dashboard'),
    path('workers/', user_views.browse_workers, name='browse_workers'),
    path('workers/<int:worker_id>/', user_views.worker_profile, name='worker_profile'),
    path('start/client/', user_views.start_client, name='start_client'),
    path('start/worker/', user_views.start_worker, name='start_worker'),
    path('contact/', user_views.contact_submit, name='contact_submit'),
    path('pricing/', user_views.landing_pricing, name='landing_pricing'),
    path('faq/', user_views.landing_faq, name='landing_faq'),
    path('support/', user_views.landing_support, name='landing_support'),
    path('privacy/', user_views.landing_privacy, name='landing_privacy'),
    path('terms/', user_views.landing_terms, name='landing_terms'),
    path('careers/', user_views.landing_careers, name='landing_careers'),
    path('blog/', user_views.landing_blog, name='landing_blog'),
    path('success-stories/', user_views.landing_success_stories, name='landing_success_stories'),
    path('resources/', user_views.landing_resources, name='landing_resources'),
    path('notifications/', user_views.notifications_page, name='notifications_page'),
    path('messages/', user_views.messages_page, name='messages_page'),
    path('reviews/', user_views.reviews_page, name='reviews_page'),
    path('favorites/', user_views.favorites_page, name='favorites_page'),
    path('profile/', user_views.profile_page, name='profile_page'),
    path('settings/', user_views.settings_page, name='settings_page'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.txt',
        subject_template_name='registration/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),

    path('book/<int:worker_id>/', booking_views.book_worker, name='book_worker'),
    path('bookings/', booking_views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', booking_views.booking_detail, name='booking_detail'),
    path('booking/<int:booking_id>/status/', booking_views.update_booking, name='update_booking'),

    path('wallet/', escrow_views.wallet_page, name='wallet_page'),
    path('booking/<int:booking_id>/escrow/', escrow_views.escrow_pay, name='escrow_pay'),

    path('review/<int:booking_id>/', review_views.review, name='review'),
]
