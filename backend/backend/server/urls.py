from django.urls import path
from server import views


urlpatterns = [
    path('signin', views.login_student),
    path('signup', views.signup_student),
    path('signout', views.logout_student),
    path("profile/<str:roll>", views.fetch_profile),
    path("events", views.fetch_events),
    path('council', views.fetch_council),
    path("complains", views.fetch_complains),
    path("categories", views.fetch_categories),
    path('items/<str:category>', views.fetch_inventory),
    path('complaints/new', views.submit_complaint),
    path('complaints/delete', views.complaint_delete),
    path('issigned', views.user_check),
    path('mess/app', views.app_handler),
    path('user/update', views.save_profile),
    path('mess/status', views.get_mess_state),
    path('mess/history', views.mess_history),
    path('reg_machine', views.reg_machines),
    path('up', views.up),
    path('down', views.down),
]
