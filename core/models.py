from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from django.utils import timezone
from datetime import date
import calendar
from datetime import timedelta

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
        ('ambos', 'Ambos'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='ambos')
    cor = models.CharField(max_length=7, default='#007bff')  # Cor em hexadecimal
    icone = models.CharField(max_length=50, default='fas fa-tag')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categorias')
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']
        unique_together = ['nome', 'usuario']

    def __str__(self):
        return self.nome

class Conta(models.Model):
    TIPO_CHOICES = [
        ('corrente', 'Conta Corrente'),
        ('poupanca', 'Conta Poupança'),
        ('investimento', 'Conta Investimento'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('dinheiro', 'Dinheiro'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='corrente')
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default='#28a745')
    icone = models.CharField(max_length=50, default='fas fa-wallet')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contas')
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['nome']
        unique_together = ['nome', 'usuario']

    def __str__(self):
        return f"{self.nome} - R$ {self.saldo_atual}"

    def atualizar_saldo(self):
        """Atualiza o saldo da conta baseado nas transações"""
        # Receitas da conta
        receitas = self.receitas.filter(ativo=True).aggregate(
            total=models.Sum('valor'))['total'] or 0
        
        # Despesas da conta
        despesas = self.despesas.filter(ativo=True).aggregate(
            total=models.Sum('valor'))['total'] or 0
        
        # Transferências onde esta conta é destino (entrada)
        transferencias_entrada = self.transferencias_destino.filter(ativo=True).aggregate(
            total=models.Sum('valor'))['total'] or 0
        
        # Transferências onde esta conta é origem (saída)
        transferencias_saida = self.transferencias_origem.filter(ativo=True).aggregate(
            total=models.Sum('valor'))['total'] or 0
        
        # Cálculo do saldo: saldo_inicial + receitas - despesas + transferências_entrada - transferências_saida
        self.saldo_atual = self.saldo_inicial + receitas - despesas + transferencias_entrada - transferencias_saida
        self.save(update_fields=['saldo_atual'])

class Receita(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='receitas')
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='receitas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receitas')
    observacoes = models.TextField(blank=True)
    recorrente = models.BooleanField(default=False)
    frequencia = models.CharField(max_length=20, blank=True, choices=[
        ('semanal', 'Semanal'),
        ('quinzenal', 'Quinzenal'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ])
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        ordering = ['-data', '-data_criacao']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza o saldo da conta
        self.conta.atualizar_saldo()

class Despesa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='despesas')
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='despesas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='despesas')
    observacoes = models.TextField(blank=True)
    recorrente = models.BooleanField(default=False)
    frequencia = models.CharField(max_length=20, blank=True, choices=[
        ('semanal', 'Semanal'),
        ('quinzenal', 'Quinzenal'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ])
    # Novos campos para cartão de crédito
    TIPO_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro/Conta'),
        ('cartao_credito_avista', 'Cartão de Crédito (à vista)'),
        ('cartao_credito_parcelado', 'Cartão de Crédito (parcelado)'),
    ]
    tipo_pagamento = models.CharField(max_length=30, choices=TIPO_PAGAMENTO_CHOICES, default='dinheiro')
    cartao = models.ForeignKey('CartaoCredito', null=True, blank=True, on_delete=models.SET_NULL, related_name='despesas_cartao')
    parcelas = models.PositiveIntegerField(null=True, blank=True)
    fatura = models.ForeignKey('Fatura', null=True, blank=True, on_delete=models.SET_NULL, related_name='despesas_fatura')
    parcela_atual = models.PositiveIntegerField(null=True, blank=True, default=1)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data', '-data_criacao']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

    def save(self, *args, **kwargs):
        # Se for uma despesa parcelada e ainda não foi criada (não tem id)
        if self.cartao and self.tipo_pagamento == 'cartao_credito_parcelado' and not self.id:
            from core.models import Fatura
            from datetime import date
            fechamento = self.cartao.data_fechamento_fatura
            vencimento = self.cartao.data_vencimento_fatura
            data_compra = self.data
            parcelas = self.parcelas or 1
            valor_parcela = round(self.valor / parcelas, 2)
            resto = round(self.valor - (valor_parcela * parcelas), 2)
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
            for i in range(parcelas):
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
                    cartao=self.cartao, vencimento=data_venc,
                    defaults={'valor': 0}
                )
                # Corrige o valor da última parcela para somar exatamente o valor total
                valor_atual = valor_parcela
                if i == parcelas - 1:
                    valor_atual += resto
                # Ajusta a data da despesa para o mês de vencimento da fatura
                data_parcela = data_venc
                despesa_parcela = Despesa(
                    descricao=self.descricao,
                    valor=valor_atual,
                    data=data_parcela,
                    categoria=self.categoria,
                    conta=self.conta,
                    usuario=self.usuario,
                    observacoes=self.observacoes,
                    recorrente=self.recorrente,
                    frequencia=self.frequencia,
                    tipo_pagamento=self.tipo_pagamento,
                    cartao=self.cartao,
                    parcelas=parcelas,
                    fatura=fatura,
                    parcela_atual=i+1,
                    ativo=self.ativo
                )
                super(Despesa, despesa_parcela).save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            self.conta.atualizar_saldo()
            # Para despesas à vista ou não parceladas, associar à fatura correta
            if self.cartao and self.tipo_pagamento.startswith('cartao_credito'):
                from core.models import Fatura
                from datetime import date
                fechamento = self.cartao.data_fechamento_fatura
                vencimento = self.cartao.data_vencimento_fatura
                data_compra = self.data
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
                fatura, _ = Fatura.objects.get_or_create(
                    cartao=self.cartao, vencimento=data_venc,
                    defaults={'valor': 0}
                )
                self.fatura = fatura
                super().save(update_fields=['fatura'])

class Transferencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    data = models.DateField()
    conta_origem = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='transferencias_origem')
    conta_destino = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='transferencias_destino')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferencias')
    observacoes = models.TextField(blank=True)
    taxa = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transferência'
        verbose_name_plural = 'Transferências'
        ordering = ['-data', '-data_criacao']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza os saldos das contas
        self.conta_origem.atualizar_saldo()
        self.conta_destino.atualizar_saldo()

class Meta(models.Model):
    TIPO_CHOICES = [
        ('economia', 'Economia'),
        ('investimento', 'Investimento'),
        ('pagamento', 'Pagamento de Dívida'),
        ('compra', 'Compra'),
        ('outros', 'Outros'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    valor_meta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='economia')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='metas')
    conta = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True, blank=True, related_name='metas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metas')
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['data_fim', 'titulo']

    def __str__(self):
        return self.titulo

    @property
    def percentual_concluido(self):
        """Retorna o percentual de conclusão da meta"""
        if self.valor_meta > 0:
            return min((self.valor_atual / self.valor_meta) * 100, 100)
        return 0

    @property
    def valor_restante(self):
        """Retorna o valor restante para atingir a meta"""
        return max(self.valor_meta - self.valor_atual, 0)

class Configuracao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='configuracao')
    moeda_padrao = models.CharField(max_length=3, default='BRL')
    formato_data = models.CharField(max_length=20, default='DD/MM/YYYY')
    icones_coloridos = models.BooleanField(default=False, verbose_name='Ícones Coloridos')
    notificacoes_email = models.BooleanField(default=True)
    backup_automatico = models.BooleanField(default=True)
    # Novos campos para dashboard
    dashboard_tipo = models.CharField(max_length=20, default='moderno', choices=[('moderno', 'Moderno'), ('classico', 'Clássico')])
    dashboard_layout = models.CharField(max_length=20, default='default', choices=[('default', 'Padrão'), ('compact', 'Compacto'), ('wide', 'Amplo'), ('tall', 'Alto')])
    dashboard_tema = models.CharField(
        max_length=30,
        default='corona-dark',
        choices=[
            ('corona-dark', 'Corona Dark'),
            ('vanta-dark', 'Vanta Dark'),
            ('futureui-color', 'Future UI Colorido'),
            ('material-light', 'Material Light'),
            ('sgfp-light-sidebar', 'SGFP Light Sidebar'),
        ]
    )
    dashboard_refresh = models.PositiveIntegerField(default=5, help_text='Intervalo de atualização automática (minutos)')
    dashboard_animations = models.BooleanField(default=True)
    dashboard_dragdrop = models.BooleanField(default=True)
    escala_interface = models.PositiveIntegerField(
        default=100,
        choices=[
            (70, '70%'),
            (80, '80%'),
            (90, '90%'),
            (100, '100% (Padrão)'),
            (110, '110%'),
            (120, '120%'),
            (130, '130%'),
        ],
        verbose_name='Escala da Interface (%)'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return f"Configuração de {self.usuario.username}"

class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('alerta', 'Alerta'),
        ('info', 'Informação'),
        ('sucesso', 'Sucesso'),
        ('aviso', 'Aviso'),
        ('erro', 'Erro'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='info')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_leitura = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    icone = models.CharField(max_length=50, default='fas fa-bell')
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def marcar_como_lida(self):
        self.lida = True
        self.data_leitura = timezone.now()
        self.save()
    
    @classmethod
    def criar_alerta_saldo_negativo(cls, usuario, saldo):
        return cls.objects.create(
            usuario=usuario,
            titulo='Saldo Negativo',
            mensagem=f'Seu saldo está negativo em R$ {abs(saldo):.2f}. Revise suas despesas.',
            tipo='erro',
            icone='fas fa-exclamation-triangle'
        )
    
    @classmethod
    def criar_alerta_meta_vencendo(cls, usuario, meta):
        dias_restantes = (meta.data_fim - timezone.now().date()).days
        percentual = (meta.valor_atual / meta.valor_meta * 100) if meta.valor_meta > 0 else 0
        
        return cls.objects.create(
            usuario=usuario,
            titulo=f'Meta: {meta.titulo}',
            mensagem=f'Meta vence em {dias_restantes} dias. Progresso: {percentual:.1f}%',
            tipo='aviso',
            link=f'/metas/{meta.id}/',
            icone='fas fa-bullseye'
        )
    
    @classmethod
    def criar_alerta_despesas_elevadas(cls, usuario, percentual):
        return cls.objects.create(
            usuario=usuario,
            titulo='Despesas Elevadas',
            mensagem=f'Suas despesas estão consumindo {percentual:.1f}% das suas receitas.',
            tipo='aviso',
            link='/dashboard/',
            icone='fas fa-chart-line'
        )

class CartaoCredito(models.Model):
    BANDEIRA_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('elo', 'Elo'),
        ('amex', 'American Express'),
        ('hipercard', 'Hipercard'),
        ('diners', 'Diners Club'),
        ('outros', 'Outros'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    numero = models.CharField(max_length=20, blank=True, help_text='Apenas os 4 últimos dígitos')
    bandeira = models.CharField(max_length=20, choices=BANDEIRA_CHOICES, default='visa')
    titular = models.CharField(max_length=100)
    data_vencimento_fatura = models.PositiveSmallIntegerField(help_text='Dia do vencimento da fatura')
    data_fechamento_fatura = models.PositiveSmallIntegerField(help_text='Dia do fechamento da fatura')
    limite_total = models.DecimalField(max_digits=12, decimal_places=2)
    conta_pagamento = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='cartoes_pagamento')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cartoes_credito')
    chave_seguranca = models.CharField(max_length=10, blank=True, help_text='CVV, não exibir em tela')
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cartão de Crédito'
        verbose_name_plural = 'Cartões de Crédito'
        ordering = ['nome']
        unique_together = ['nome', 'usuario', 'numero']

    def __str__(self):
        return f"{self.nome} ({self.get_bandeira_display()})"

    @property
    def limite_utilizado(self):
        # Soma das despesas em aberto vinculadas a este cartão
        total = Despesa.objects.filter(cartao=self, ativo=True).aggregate(models.Sum('valor'))['valor__sum'] or 0
        return total

    @property
    def limite_disponivel(self):
        return self.limite_total - self.limite_utilizado

    @property
    def data_vencimento(self):
        """Retorna a próxima data de vencimento da fatura"""
        hoje = date.today()
        # Calcula o próximo vencimento
        if hoje.day > self.data_vencimento_fatura:
            # Se já passou do dia de vencimento, vai para o próximo mês
            if hoje.month == 12:
                return date(hoje.year + 1, 1, self.data_vencimento_fatura)
            else:
                return date(hoje.year, hoje.month + 1, self.data_vencimento_fatura)
        else:
            # Se ainda não chegou o dia de vencimento, usa o mês atual
            return date(hoje.year, hoje.month, self.data_vencimento_fatura)

    @property
    def data_fechamento(self):
        """Retorna a próxima data de fechamento da fatura"""
        hoje = date.today()
        # Calcula o próximo fechamento
        if hoje.day > self.data_fechamento_fatura:
            # Se já passou do dia de fechamento, vai para o próximo mês
            if hoje.month == 12:
                return date(hoje.year + 1, 1, self.data_fechamento_fatura)
            else:
                return date(hoje.year, hoje.month + 1, self.data_fechamento_fatura)
        else:
            # Se ainda não chegou o dia de fechamento, usa o mês atual
            return date(hoje.year, hoje.month, self.data_fechamento_fatura)

class Fatura(models.Model):
    cartao = models.ForeignKey('CartaoCredito', on_delete=models.CASCADE, related_name='faturas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField()
    paga = models.BooleanField(default=False)
    ajustada = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('cartao', 'vencimento')
        ordering = ['-vencimento']

    def __str__(self):
        return f'Fatura {self.vencimento.strftime("%m/%Y")} - {self.cartao.nome}'

    def get_mes_display(self):
        return self.vencimento.strftime('%b').capitalize()

    @property
    def status(self):
        if self.paga:
            return 'Paga'
        elif self.vencimento < timezone.now().date():
            return 'Vencida'
        else:
            return 'Em aberto'

    def despesas_do_ciclo(self):
        fechamento_atual = self.cartao.data_fechamento_fatura
        from datetime import date
        data_fechamento_anterior = self.vencimento.replace(day=fechamento_atual) - timedelta(days=30)
        data_fechamento_atual = self.vencimento.replace(day=fechamento_atual)
        return self.cartao.despesas_cartao.filter(
            data__gt=data_fechamento_anterior,
            data__lte=data_fechamento_atual,
            ativo=True
        )

    def valor_calculado(self):
        """Soma das despesas do ciclo, se não ajustada manualmente."""
        if self.ajustada:
            return self.valor
        return self.despesas_do_ciclo().aggregate(models.Sum('valor'))['valor__sum'] or 0
