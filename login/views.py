from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect

class SGFPPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Redireciona diretamente para a tela de redefinição de senha
            return redirect(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
        except User.DoesNotExist:
            messages.success(self.request, 'Se o e-mail informado estiver cadastrado, você receberá instruções para redefinir sua senha.')
            return super().form_valid(form) 