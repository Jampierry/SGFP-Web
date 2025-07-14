from django.urls import path
from .views import SGFPPasswordResetView
from core.views import LoginViewCustom
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', LoginViewCustom.as_view(), name='login'),
    path('recuperar-senha/', SGFPPasswordResetView.as_view(), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
] 