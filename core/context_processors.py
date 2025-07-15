from core.models import Configuracao

def preferencias_usuario(request):
    if request.user.is_authenticated:
        configuracao, _ = Configuracao.objects.get_or_create(usuario=request.user)
        return {
            'icones_coloridos': configuracao.icones_coloridos,
            'tema_usuario': configuracao.dashboard_tema,
        }
    return {
        'icones_coloridos': False,
        'tema_usuario': 'corona-dark',
    } 