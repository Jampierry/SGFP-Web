from django.core.management.base import BaseCommand
from core.models import Despesa, Fatura
from datetime import date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Associa despesas de cartão de crédito às faturas corretas baseado na data de vencimento.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando associação de despesas às faturas...'))
        
        # Buscar despesas de cartão de crédito sem fatura associada
        despesas_sem_fatura = Despesa.objects.filter(
            cartao__isnull=False,
            fatura__isnull=True,
            ativo=True
        )
        
        count_associadas = 0
        
        for despesa in despesas_sem_fatura:
            cartao = despesa.cartao
            fechamento = cartao.data_fechamento_fatura
            vencimento = cartao.data_vencimento_fatura
            data_compra = despesa.data
            
            # Determinar a qual fatura esta despesa pertence
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
            
            try:
                data_venc = date(ano_fatura, mes_fatura, vencimento)
            except Exception:
                from calendar import monthrange
                data_venc = date(ano_fatura, mes_fatura, monthrange(ano_fatura, mes_fatura)[1])
            
            # Criar ou buscar a fatura correspondente
            fatura, created = Fatura.objects.get_or_create(
                cartao=cartao,
                vencimento=data_venc,
                defaults={'valor': 0}
            )
            
            # Associar a despesa à fatura
            despesa.fatura = fatura
            despesa.save(update_fields=['fatura'])
            count_associadas += 1
            
            if created:
                self.stdout.write(f'  Criada fatura para {cartao.nome} - {data_venc.strftime("%m/%Y")}')
            else:
                self.stdout.write(f'  Associada despesa "{despesa.descricao}" à fatura {data_venc.strftime("%m/%Y")}')
        
        self.stdout.write(self.style.SUCCESS(f'Associação concluída. {count_associadas} despesas associadas às faturas.'))
        
        # Verificar se ainda há despesas sem fatura
        despesas_restantes = Despesa.objects.filter(
            cartao__isnull=False,
            fatura__isnull=True,
            ativo=True
        ).count()
        
        if despesas_restantes > 0:
            self.stdout.write(self.style.WARNING(f'Ainda existem {despesas_restantes} despesas sem fatura associada.'))
        else:
            self.stdout.write(self.style.SUCCESS('Todas as despesas de cartão de crédito estão associadas às faturas!')) 