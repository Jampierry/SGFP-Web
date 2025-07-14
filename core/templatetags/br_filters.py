from django import template
from decimal import Decimal, InvalidOperation
from django.utils.safestring import mark_safe

register = template.Library()

ICONE_CORES = {
    'edit': 'text-primary',
    'delete': 'text-danger',
    'receita': 'text-success',
    'despesa': 'text-danger',
    'transferencia': 'text-info',
    'categoria': 'text-warning',
    'conta': 'text-purple',
    'cartao': 'text-info',
    'meta': 'text-pink',
    'relatorio': 'text-info',
    'configuracao': 'text-warning',
    'padrao': 'text-success',
}

@register.simple_tag(takes_context=True)
def icone_colorido(context, icone_class, contexto='padrao', extra_classes=''):
    user = context.get('user')
    cor = ICONE_CORES.get(contexto, ICONE_CORES['padrao'])
    colorido = False
    if hasattr(user, 'configuracoes') and getattr(user.configuracoes, 'icones_coloridos', False):
        colorido = True
    classes = f"{icone_class} {extra_classes}"
    if colorido:
        classes += f" {cor}"
    return mark_safe(f'<i class="{classes}"></i>')

@register.filter
def br_currency(value):
    """Formata valor monetário no padrão brasileiro: R$ 1.234,56"""
    try:
        if value is None or value == '' or value == 'None':
            return 'R$ 0,00'
        if isinstance(value, str):
            value = value.strip().replace('R$', '').replace(' ', '').replace('$', '')
            if not value or value.lower() == 'none':
                return 'R$ 0,00'
            value = value.replace(',', '.')
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            return 'R$ 0,00'
        # Formatação manual para padrão brasileiro
        inteiro, decimal = f"{value:.2f}".split('.')
        inteiro = inteiro[::-1]
        partes = [inteiro[i:i+3] for i in range(0, len(inteiro), 3)]
        inteiro_formatado = '.'.join(partes)[::-1]
        return f"R$ {inteiro_formatado},{decimal}"
    except Exception:
        return 'R$ 0,00'

@register.filter
def br_date(value):
    """Formata data no padrão brasileiro"""
    try:
        if value:
            return value.strftime('%d/%m/%Y')
        return ''
    except:
        return str(value) if value else ''

@register.filter
def br_datetime(value):
    """Formata data e hora no padrão brasileiro"""
    try:
        if value:
            return value.strftime('%d/%m/%Y %H:%M')
        return ''
    except:
        return str(value) if value else ''

@register.filter
def percentage(value, total=100):
    """Calcula e formata percentual"""
    try:
        if total and float(total) > 0:
            percent = (float(value) / float(total)) * 100
            return f'{percent:.1f}%'
        return '0%'
    except:
        return '0%'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def banco_cor(nome_banco):
    """Retorna a cor oficial do banco pelo nome (hex)."""
    if not nome_banco:
        return '#232526'
    nome = nome_banco.strip().lower()
    cores = {
        'nubank': '#8A05BE',
        'neon': '#00E1FF',
        'inter': '#FF6600',
        'next': '#00C86F',
        'pan': '#1A1A1A',
        'banco pan': '#1A1A1A',
        'original': '#00B488',
        'banco original': '#00B488',
        'banco do brasil': '#FFCC29',
        'banco brasil': '#FFCC29',
        'caixa economica': '#005ca9',
        'caixa': '#005ca9',
        'santander': '#ed0033',
        'bradesco': '#a51c48',
        'itau': '#ff7300',
        'banco safra': '#2d2a6e',
        'banco mercantil': '#f58220',
        'bancoob': '#00995d',
        'banco intermedium': '#ff6600',
        'bmg': '#ff6600',
        'c6 bank': '#222',
        'c6': '#222',
        'c6bank': '#222',
        'pagbank': '#00bfae',
        'will bank': '#ffe600',
        'willbank': '#ffe600',
        'banrisul': '#009ddc',
        'banco do nordeste': '#a51c48',
        'banco da amazonia': '#009739',
        'banco do estado do pará': '#009739',
        'banco do estado de sergipe': '#f58220',
        'banco do estado de goias': '#009739',
        'banco do estado de minas gerais': '#009739',
        'banco do estado do rio grande do sul': '#009ddc',
        'banco do estado de santa catarina': '#009739',
        'banco do estado do espirito santo': '#009739',
        'banco do estado do mato grosso': '#009739',
        'banco do estado do mato grosso do sul': '#009739',
        'banco do estado do maranhão': '#009739',
        'banco do estado do piauí': '#009739',
        'banco do estado do acre': '#009739',
        'banco do estado do amapá': '#009739',
        'banco do estado de rondônia': '#009739',
        'banco do estado de roraima': '#009739',
        'banco do estado do tocantins': '#009739',
    }
    return cores.get(nome, '#232526') 