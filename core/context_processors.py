from core.models import Configuracao

def tema_config(request):
    """Context processor para disponibilizar configurações do tema em todas as páginas"""
    if request.user.is_authenticated:
        try:
            configuracao = request.user.configuracao
        except Configuracao.DoesNotExist:
            configuracao = Configuracao.objects.create(usuario=request.user)
            return {
            'configuracao': configuracao,
            'icones_coloridos': configuracao.icones_coloridos
            }
    return {
        'configuracao': None,
        'icones_coloridos': False
    }

def tema_usuario(request):
    if request.user.is_authenticated:
        try:
            return {'tema_usuario': request.user.configuracao.dashboard_tema}
        except Exception:
            return {'tema_usuario': 'corona-dark'}
    return {'tema_usuario': None} 