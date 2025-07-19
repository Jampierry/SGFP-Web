def preencher_campos_cartao(cartoes, fatura_id_selecionada=None, data_base=None):
    from datetime import date
    from calendar import monthrange
    if data_base is None:
        data_base = date.today()
    mes_atual = data_base.month
    ano_atual = data_base.year
    for cartao in cartoes:
        if fatura_id_selecionada:
            fatura = cartao.faturas.filter(id=fatura_id_selecionada).first()
            cartao.fatura_valor = fatura.valor_calculado() if fatura else 0
        else:
            # Exibe o valor da(s) fatura(s) do mês vigente (em aberto e não paga)
            faturas_mes = cartao.faturas.filter(paga=False, vencimento__month=mes_atual, vencimento__year=ano_atual)
            cartao.fatura_valor = sum([f.valor_calculado() for f in faturas_mes]) if faturas_mes else 0
        # Badge de fatura vencida
        cartao.tem_fatura_vencida = cartao.faturas.filter(paga=False, vencimento__lt=data_base).exists()
        cartao.limite_valor = cartao.limite_total
        cartao.utilizado_valor = cartao.limite_utilizado
        cartao.saldo_valor = cartao.limite_disponivel
        cartao.data_fechamento_fatura = cartao.data_fechamento_fatura 