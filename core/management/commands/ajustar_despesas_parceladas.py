from django.core.management.base import BaseCommand
from core.models import Despesa, Fatura
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class Command(BaseCommand):
    help = 'Ajusta despesas parceladas antigas: divide valor, ajusta data e associa à fatura correta.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando ajuste de despesas parceladas antigas...'))
        count_ajustadas = 0
        # Busca despesas parceladas antigas (valor total igual em todas as parcelas)
        despesas = Despesa.objects.filter(
            tipo_pagamento='cartao_credito_parcelado',
            ativo=True
        ).order_by('cartao', 'descricao', 'data', 'parcelas', 'parcela_atual')
        agrupadas = {}
        for d in despesas:
            key = (d.cartao_id, d.descricao, d.data, d.parcelas)
            agrupadas.setdefault(key, []).append(d)
        for key, parcelas in agrupadas.items():
            if len(parcelas) < 2:
                continue  # Não é parcelado de verdade
            total = sum([p.valor for p in parcelas])
            n = len(parcelas)
            valor_parcela = (total / n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            resto = total - (valor_parcela * n)
            for i, p in enumerate(sorted(parcelas, key=lambda x: x.parcela_atual or 1)):
                # Calcula vencimento correto
                data_compra = p.data
                fechamento = p.cartao.data_fechamento_fatura
                vencimento = p.cartao.data_vencimento_fatura
                if data_compra.day <= fechamento:
                    mes_fatura = data_compra.month
                    ano_fatura = data_compra.year
                else:
                    if data_compra.month == 12:
                        mes_fatura = 1
                        ano_fatura = data_compra.year + 1
                    else:
                        mes_fatura = data_compra.month + 1
                        ano_fatura = data_compra.year
                mes = mes_fatura + i
                ano = ano_fatura
                while mes > 12:
                    mes -= 12
                    ano += 1
                try:
                    data_venc = date(ano, mes, vencimento)
                except Exception:
                    from calendar import monthrange
                    data_venc = date(ano, mes, monthrange(ano, mes)[1])
                fatura, _ = Fatura.objects.get_or_create(
                    cartao=p.cartao, vencimento=data_venc,
                    defaults={'valor': 0}
                )
                novo_valor = valor_parcela
                if i == n - 1:
                    novo_valor += resto
                mudou = False
                if p.valor != novo_valor:
                    p.valor = novo_valor
                    mudou = True
                if p.data != data_venc:
                    p.data = data_venc
                    mudou = True
                if p.fatura_id != fatura.id:
                    p.fatura = fatura
                    mudou = True
                if mudou:
                    p.save()
                    count_ajustadas += 1
        self.stdout.write(self.style.SUCCESS(f'Ajuste concluído. {count_ajustadas} despesas parceladas corrigidas.')) 