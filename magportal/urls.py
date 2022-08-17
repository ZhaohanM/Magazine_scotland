
from django.urls import path
from magportal import views

app_name = 'magportal'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('magazines/', views.browse_magazines, name='browse_magazines'),
    path('contact/', views.contact, name='contact'),
    path('magportal/<slug:mag_name_Slug>/favourite/', views.favourite, name='favourite'),
    path('magportal/<slug:mag_name_Slug>/unfavourite/', views.unfavourite, name='unfavourite'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name = 'login'),
    path('logout/', views.user_logout, name = 'logout'),
    path('create_magazine/', views.add_magazine, name = 'add_magazine'),
    path('', views.home, name='magportal'),
    path('category/<slug:category_Name_Slug>/', views.browse_category, name='browse_category'),
    path('users/<slug:username>/', views.view_profile, name='view_profile'),
    path('users/<slug:username>/edit', views.edit_profile, name='edit_profile'),
    path('member/membership/', views.membership, name='membership'),
    path('member/cancel_membership/', views.cancel_membership, name='cancel_membership'),
    path('config/', views.stripe_config, name='config'),
    path('create-checkout-session/', views.create_checkout_session, name='checkout'),
    path('create-checkout-session-6/', views.create_checkout_session_6, name='checkout'),
    path('create-checkout-session-year/', views.create_checkout_session_year, name='checkout'),
    path('membership/cancelled/', views.CancelledView.as_view()), 
    path('webhook/', views.stripe_webhook),
    path('magportal/<slug:mag_name_Slug>/discountcode/', views.discountcode, name='discount'),
    path('codes/', views.view_codes, name='codes')
] 

