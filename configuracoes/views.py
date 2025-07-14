from django.shortcuts import render, redirect
from core.models import Configuracao
from core.forms import ConfiguracaoForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    configuracao, _ = Configuracao.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, instance=configuracao)
        if form.is_valid():
            form.save()
            return redirect('configuracoes:home')
    else:
        form = ConfiguracaoForm(instance=configuracao)
    return render(request, 'configuracoes/configuracoes.html', {'form': form})
