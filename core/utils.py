def preencher_campos_cartao(cartoes, fatura_id_selecionada=None):
    from datetime import date
    from calendar import monthrange
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    ultimo_dia_mes = monthrange(hoje.year, hoje.month)[1]
    fim_mes = hoje.replace(day=ultimo_dia_mes)
    for cartao in cartoes:
        if fatura_id_selecionada:
            fatura = cartao.faturas.filter(id=fatura_id_selecionada).first()
            cartao.fatura_valor = fatura.valor_calculado() if fatura else 0
        else:
            # Soma todas as faturas não pagas com vencimento até o fim do mês vigente
            faturas = cartao.faturas.filter(paga=False, vencimento__lte=fim_mes)
            cartao.fatura_valor = sum([f.valor_calculado() for f in faturas])
        cartao.limite_valor = cartao.limite_total
        cartao.utilizado_valor = cartao.limite_utilizado
        cartao.saldo_valor = cartao.limite_disponivel 