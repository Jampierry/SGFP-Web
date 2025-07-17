from core.models import Configuracao

def preferencias_usuario(request):
    if request.user.is_authenticated:
        configuracao, _ = Configuracao.objects.get_or_create(usuario=request.user)
        escala_interface = configuracao.escala_interface
        fator_escala = round(escala_interface * 0.007, 3)  # 100% = 0.7 real
        font_size_percent = str(round(escala_interface * 0.7, 1)).replace(',', '.')  # Corrige separador decimal
        return {
            'icones_coloridos': configuracao.icones_coloridos,
            'tema_usuario': configuracao.dashboard_tema,
            'escala_interface': escala_interface,
            'fator_escala': fator_escala,
            'font_size_percent': font_size_percent,
        }
    return {
        'icones_coloridos': False,
        'tema_usuario': 'corona-dark',
        'escala_interface': 100,
        'fator_escala': 0.7,
        'font_size_percent': '70',
    } 