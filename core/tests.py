"""Testes de caracterização (Fase 1 do plano de migração).

Registram o comportamento ATUAL do Django, inclusive quirks, para servir de
referência (golden) na reimplementação em TypeScript/Postgres. Dados sintéticos.
Quirks marcados com "QUIRK" não são necessariamente desejáveis.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import (
    CartaoCredito, Categoria, Conta, Despesa, Fatura, Meta, Receita,
    Transferencia,
)

D = Decimal


class BaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u1', password='x')
        self.cat = Categoria.objects.create(nome='Geral', usuario=self.user)
        self.conta = Conta.objects.create(
            nome='Corrente', usuario=self.user, saldo_inicial=D('1000.00'),
            saldo_atual=D('1000.00'))
        self.conta2 = Conta.objects.create(
            nome='Poupança', usuario=self.user, saldo_inicial=D('0'))

    def saldo(self, conta=None):
        c = conta or self.conta
        c.refresh_from_db()
        return c.saldo_atual

    def receita(self, valor, **kw):
        return Receita.objects.create(
            descricao='r', valor=D(valor), data=kw.pop('data', date(2025, 1, 10)),
            categoria=self.cat, conta=kw.pop('conta', self.conta),
            usuario=self.user, **kw)

    def despesa(self, valor, **kw):
        return Despesa.objects.create(
            descricao='d', valor=D(valor), data=kw.pop('data', date(2025, 1, 10)),
            categoria=self.cat, conta=kw.pop('conta', self.conta),
            usuario=self.user, **kw)

    def cartao(self, fechamento=10, vencimento=20):
        return CartaoCredito.objects.create(
            nome='Visa', titular='T', usuario=self.user,
            data_fechamento_fatura=fechamento, data_vencimento_fatura=vencimento,
            limite_total=D('5000'), conta_pagamento=self.conta)


class SaldoTests(BaseTest):
    def test_saldo_receita_e_despesa(self):
        self.receita('200.00')
        self.despesa('50.50')
        self.assertEqual(self.saldo(), D('1149.50'))

    def test_transferencia_move_valor_entre_contas(self):
        Transferencia.objects.create(
            descricao='t', valor=D('300.00'), data=date(2025, 1, 5),
            conta_origem=self.conta, conta_destino=self.conta2, usuario=self.user)
        self.assertEqual(self.saldo(self.conta), D('700.00'))
        self.assertEqual(self.saldo(self.conta2), D('300.00'))

    def test_taxa_da_transferencia_e_ignorada_no_saldo(self):
        # QUIRK: o campo `taxa` não entra em atualizar_saldo().
        Transferencia.objects.create(
            descricao='t', valor=D('100.00'), taxa=D('5.00'), data=date(2025, 1, 5),
            conta_origem=self.conta, conta_destino=self.conta2, usuario=self.user)
        self.assertEqual(self.saldo(self.conta), D('900.00'))
        self.assertEqual(self.saldo(self.conta2), D('100.00'))

    def test_registro_inativo_nao_conta(self):
        self.despesa('100.00', ativo=False)
        self.assertEqual(self.saldo(), D('1000.00'))

    def test_delete_nao_recalcula_saldo(self):
        # QUIRK: delete() não chama atualizar_saldo(); saldo fica defasado.
        d = self.despesa('100.00')
        self.assertEqual(self.saldo(), D('900.00'))
        d.delete()
        self.assertEqual(self.saldo(), D('900.00'))
        self.conta.refresh_from_db()
        self.conta.atualizar_saldo()
        self.assertEqual(self.conta.saldo_atual, D('1000.00'))

    def test_saldo_inicial_alterado_so_vale_no_proximo_recalculo(self):
        self.conta.saldo_inicial = D('500.00')
        self.conta.save()
        self.assertEqual(self.saldo(), D('1000.00'))
        self.conta.atualizar_saldo()
        self.assertEqual(self.saldo(), D('500.00'))


class FaturaAvistaTests(BaseTest):
    """Despesa no cartão à vista: escolhe a fatura pelo dia do fechamento."""

    def fatura_de(self, data, **cartao_kw):
        cartao = self.cartao(**cartao_kw)
        d = self.despesa('100.00', data=data, cartao=cartao,
                         tipo_pagamento='cartao_credito_avista')
        d.refresh_from_db()
        return d.fatura

    def test_compra_ate_o_fechamento_vai_para_fatura_do_mes(self):
        f = self.fatura_de(date(2025, 3, 10))  # fechamento 10 (inclusive)
        self.assertEqual(f.vencimento, date(2025, 3, 20))

    def test_compra_apos_o_fechamento_vai_para_o_mes_seguinte(self):
        f = self.fatura_de(date(2025, 3, 11))
        self.assertEqual(f.vencimento, date(2025, 4, 20))

    def test_virada_de_ano(self):
        f = self.fatura_de(date(2025, 12, 15))
        self.assertEqual(f.vencimento, date(2026, 1, 20))

    def test_vencimento_31_cai_no_ultimo_dia_do_mes(self):
        f = self.fatura_de(date(2025, 2, 5), vencimento=31)
        self.assertEqual(f.vencimento, date(2025, 2, 28))

    def test_mesma_fatura_e_reutilizada(self):
        cartao = self.cartao()
        for dia in (1, 5, 10):
            self.despesa('10.00', data=date(2025, 3, dia), cartao=cartao,
                         tipo_pagamento='cartao_credito_avista')
        self.assertEqual(Fatura.objects.filter(cartao=cartao).count(), 1)

    def test_valor_calculado_soma_o_ciclo(self):
        cartao = self.cartao()
        self.despesa('100.00', data=date(2025, 3, 5), cartao=cartao,
                     tipo_pagamento='cartao_credito_avista')
        self.despesa('50.00', data=date(2025, 3, 10), cartao=cartao,
                     tipo_pagamento='cartao_credito_avista')
        self.despesa('999.00', data=date(2025, 3, 11), cartao=cartao,
                     tipo_pagamento='cartao_credito_avista')  # outro ciclo
        f = Fatura.objects.get(cartao=cartao, vencimento=date(2025, 3, 20))
        self.assertEqual(f.valor_calculado(), D('150.00'))

    def test_fatura_ajustada_usa_valor_manual(self):
        cartao = self.cartao()
        f = Fatura.objects.create(cartao=cartao, valor=D('77.00'),
                                  vencimento=date(2025, 3, 20), ajustada=True)
        self.assertEqual(f.valor_calculado(), D('77.00'))

    def test_despesa_no_cartao_reduz_saldo_da_conta(self):
        # QUIRK: compra no cartão já debita a conta (não espera pagar a fatura).
        self.fatura_de(date(2025, 3, 5))
        self.assertEqual(self.saldo(), D('900.00'))

    def test_limite_disponivel(self):
        cartao = self.cartao()
        self.despesa('100.00', cartao=cartao, tipo_pagamento='cartao_credito_avista')
        self.assertEqual(cartao.limite_disponivel, D('4900.00'))


class ParceladoTests(BaseTest):
    def test_parcelado_novo(self):
        """Documenta o que acontece HOJE ao criar uma despesa parcelada.

        QUIRK: `not self.id` é sempre falso (id tem default=uuid4), então o
        ramo que divide em parcelas nunca roda: grava UMA despesa com o valor
        cheio, associada à fatura da 1ª data (como à vista).
        """
        cartao = self.cartao()
        self.despesa('100.00', cartao=cartao, parcelas=3,
                     tipo_pagamento='cartao_credito_parcelado',
                     data=date(2025, 3, 5))
        self.assertEqual(Despesa.objects.count(), 1)
        d = Despesa.objects.get()
        self.assertEqual(d.valor, D('100.00'))
        self.assertEqual(d.fatura.vencimento, date(2025, 3, 20))
        self.assertEqual(Fatura.objects.count(), 1)

    def test_regra_pretendida_de_divisao_de_parcelas(self):
        """Regra pretendida (código do ramo morto) para a reimplementação:
        parcela = round(valor/n, 2); resto vai na última parcela."""
        valor, n = D('100.00'), 3
        parcela = round(valor / n, 2)
        resto = round(valor - parcela * n, 2)
        self.assertEqual(parcela, D('33.33'))
        self.assertEqual(resto, D('0.01'))
        self.assertEqual(parcela * (n - 1) + parcela + resto, valor)


class MetaTests(BaseTest):
    def meta(self, alvo, atual):
        return Meta(titulo='m', valor_meta=D(alvo), valor_atual=D(atual),
                    data_inicio=date(2025, 1, 1), data_fim=date(2025, 12, 31),
                    usuario=self.user)

    def test_percentual_limitado_a_100(self):
        self.assertEqual(self.meta('100', '250').percentual_concluido, 100)

    def test_percentual_normal(self):
        self.assertEqual(self.meta('200', '50').percentual_concluido, D('25'))

    def test_valor_restante_nunca_negativo(self):
        self.assertEqual(self.meta('100', '250').valor_restante, 0)
        self.assertEqual(self.meta('100', '40').valor_restante, D('60'))
