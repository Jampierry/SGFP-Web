from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Categoria, Conta, Receita, Despesa, Transferencia, Meta, Configuracao, CartaoCredito, Fatura
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, HTML
from crispy_bootstrap5.bootstrap5 import FloatingField

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Cadastrar', css_class='btn-primary'))
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6'),
                Column('password2', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
        )

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'tipo', 'cor', 'icone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-tag'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if self.user and nome:
            # Verifica se já existe uma categoria com o mesmo nome para este usuário
            existing = Categoria.objects.filter(usuario=self.user, nome__iexact=nome)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("Já existe uma categoria com este nome.")
        return nome

class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao', 'cor', 'icone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-wallet'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if self.user and nome:
            # Verifica se já existe uma conta com o mesmo nome para este usuário
            existing = Conta.objects.filter(usuario=self.user, nome__iexact=nome)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("Já existe uma conta com este nome.")
        return nome

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'data', 'categoria', 'conta', 'observacoes', 'recorrente', 'frequencia']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conta': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequencia': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            qs_categoria = Categoria.objects.filter(usuario=self.user, ativo=True, tipo__in=['receita', 'ambos'])
            qs_conta = Conta.objects.filter(usuario=self.user, ativo=True)
            if self.instance and self.instance.pk:
                # Verificar se a categoria existe antes de acessá-la
                try:
                    if hasattr(self.instance, 'categoria') and self.instance.categoria and self.instance.categoria not in qs_categoria:
                        qs_categoria = Categoria.objects.filter(pk=self.instance.categoria.pk) | qs_categoria
                except:
                    pass  # Se não conseguir acessar categoria, ignora
                try:
                    if hasattr(self.instance, 'conta') and self.instance.conta and self.instance.conta not in qs_conta:
                        qs_conta = Conta.objects.filter(pk=self.instance.conta.pk) | qs_conta
                except:
                    pass  # Se não conseguir acessar conta, ignora
            self.fields['categoria'].queryset = qs_categoria
            self.fields['conta'].queryset = qs_conta
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean(self):
        cleaned_data = super().clean()
        recorrente = cleaned_data.get('recorrente')
        frequencia = cleaned_data.get('frequencia')
        
        if recorrente and not frequencia:
            raise forms.ValidationError("Selecione uma frequência para receitas recorrentes.")
        
        return cleaned_data

class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['descricao', 'valor', 'data', 'categoria', 'conta', 'tipo_pagamento', 'cartao', 'parcelas', 'observacoes', 'recorrente', 'frequencia']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conta': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'cartao': forms.Select(attrs={'class': 'form-select'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequencia': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            qs_categoria = Categoria.objects.filter(usuario=self.user, ativo=True, tipo__in=['despesa', 'ambos'])
            qs_conta = Conta.objects.filter(usuario=self.user, ativo=True)
            qs_cartao = CartaoCredito.objects.filter(usuario=self.user, ativo=True)
            if self.instance and self.instance.pk:
                # Verificar se os objetos relacionados existem antes de acessá-los
                try:
                    if hasattr(self.instance, 'categoria') and self.instance.categoria and self.instance.categoria not in qs_categoria:
                        qs_categoria = Categoria.objects.filter(pk=self.instance.categoria.pk) | qs_categoria
                except:
                    pass
                try:
                    if hasattr(self.instance, 'conta') and self.instance.conta and self.instance.conta not in qs_conta:
                        qs_conta = Conta.objects.filter(pk=self.instance.conta.pk) | qs_conta
                except:
                    pass
                try:
                    if hasattr(self.instance, 'cartao') and self.instance.cartao and self.instance.cartao not in qs_cartao:
                        qs_cartao = CartaoCredito.objects.filter(pk=self.instance.cartao.pk) | qs_cartao
                except:
                    pass
            self.fields['categoria'].queryset = qs_categoria
            self.fields['conta'].queryset = qs_conta
            self.fields['cartao'].queryset = qs_cartao
        else:
            self.fields['cartao'].queryset = CartaoCredito.objects.none()
        self.fields['cartao'].required = False
        self.fields['parcelas'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean(self):
        cleaned_data = super().clean()
        recorrente = cleaned_data.get('recorrente')
        frequencia = cleaned_data.get('frequencia')
        tipo_pagamento = cleaned_data.get('tipo_pagamento')
        cartao = cleaned_data.get('cartao')
        parcelas = cleaned_data.get('parcelas')
        if recorrente and not frequencia:
            raise forms.ValidationError("Selecione uma frequência para despesas recorrentes.")
        if tipo_pagamento in ['cartao_credito_avista', 'cartao_credito_parcelado'] and not cartao:
            raise forms.ValidationError("Selecione o cartão de crédito utilizado.")
        if tipo_pagamento == 'cartao_credito_parcelado' and (not parcelas or parcelas < 2):
            raise forms.ValidationError("Informe o número de parcelas (mínimo 2) para despesas parceladas.")
        return cleaned_data

class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['descricao', 'valor', 'data', 'conta_origem', 'conta_destino', 'observacoes', 'taxa']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'conta_origem': forms.Select(attrs={'class': 'form-select'}),
            'conta_destino': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'taxa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['conta_origem'].queryset = Conta.objects.filter(usuario=self.user, ativo=True)
            self.fields['conta_destino'].queryset = Conta.objects.filter(usuario=self.user, ativo=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean(self):
        cleaned_data = super().clean()
        conta_origem = cleaned_data.get('conta_origem')
        conta_destino = cleaned_data.get('conta_destino')
        
        if conta_origem and conta_destino and conta_origem == conta_destino:
            raise forms.ValidationError("A conta de origem não pode ser a mesma da conta de destino.")
        
        return cleaned_data

class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = ['titulo', 'descricao', 'valor_meta', 'valor_atual', 'data_inicio', 'data_fim', 'tipo', 'categoria', 'conta']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_meta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'valor_atual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conta': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            qs_categoria = Categoria.objects.filter(usuario=self.user, ativo=True)
            qs_conta = Conta.objects.filter(usuario=self.user, ativo=True)
            if self.instance and self.instance.pk:
                # Verificar se os objetos relacionados existem antes de acessá-los
                try:
                    if hasattr(self.instance, 'categoria') and self.instance.categoria and self.instance.categoria not in qs_categoria:
                        qs_categoria = Categoria.objects.filter(pk=self.instance.categoria.pk) | qs_categoria
                except:
                    pass
                try:
                    if hasattr(self.instance, 'conta') and self.instance.conta and self.instance.conta not in qs_conta:
                        qs_conta = Conta.objects.filter(pk=self.instance.conta.pk) | qs_conta
                except:
                    pass
            self.fields['categoria'].queryset = qs_categoria
            self.fields['conta'].queryset = qs_conta
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        valor_meta = cleaned_data.get('valor_meta')
        valor_atual = cleaned_data.get('valor_atual')
        
        if data_inicio and data_fim and data_inicio >= data_fim:
            raise forms.ValidationError("A data de início deve ser anterior à data de fim.")
        
        if valor_meta and valor_atual and valor_atual > valor_meta:
            raise forms.ValidationError("O valor atual não pode ser maior que o valor da meta.")
        
        return cleaned_data

class ConfiguracaoForm(forms.ModelForm):
    MOEDA_CHOICES = [
        ('BRL', 'Real (BRL)'),
        ('USD', 'Dólar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('GBP', 'Libra (GBP)'),
    ]
    FORMATO_DATA_CHOICES = [
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
    ]
    TIPO_DASHBOARD_CHOICES = [
        ('moderno', 'Dashboard Moderno'),
        ('classico', 'Dashboard Clássico'),
    ]
    LAYOUT_CHOICES = [
        ('default', 'Padrão'),
        ('compact', 'Compacto'),
        ('wide', 'Amplo'),
        ('tall', 'Alto'),
    ]
    ESCALA_CHOICES = [
        (70, '70%'),
        (80, '80%'),
        (90, '90%'),
        (100, '100% (Padrão)'),
        (110, '110%'),
        (120, '120%'),
        (130, '130%'),
    ]
    
    moeda_padrao = forms.ChoiceField(choices=MOEDA_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    formato_data = forms.ChoiceField(choices=FORMATO_DATA_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    dashboard_tipo = forms.ChoiceField(
        choices=TIPO_DASHBOARD_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Dashboard'
    )
    dashboard_layout = forms.ChoiceField(
        choices=LAYOUT_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Layout do Dashboard'
    )
    dashboard_tema = forms.ChoiceField(
        choices=Configuracao._meta.get_field('dashboard_tema').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tema do Dashboard'
    )
    dashboard_refresh = forms.IntegerField(
        min_value=1,
        max_value=60,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Refresh Automático (minutos)',
        help_text='Intervalo de atualização automática do dashboard'
    )
    icones_coloridos = forms.BooleanField(
        required=False,
        label='Ícones Coloridos',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    escala_interface = forms.ChoiceField(
        choices=ESCALA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Escala da Interface (%)',
        initial=100
    )

    class Meta:
        model = Configuracao
        fields = [
            'moeda_padrao', 'formato_data', 'icones_coloridos', 'notificacoes_email', 'backup_automatico',
            'dashboard_tipo', 'dashboard_layout', 'dashboard_tema', 'dashboard_refresh',
            'dashboard_animations', 'dashboard_dragdrop', 'escala_interface'
        ]
        widgets = {
            'icones_coloridos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notificacoes_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_automatico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dashboard_animations': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dashboard_dragdrop': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar Configurações', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))

class FiltroRelatorioForm(forms.Form):
    PERIODO_CHOICES = [
        ('7d', 'Últimos 7 dias'),
        ('30d', 'Últimos 30 dias'),
        ('90d', 'Últimos 90 dias'),
        ('6m', 'Últimos 6 meses'),
        ('1y', 'Último ano'),
        ('custom', 'Período personalizado'),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='30d'
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas as categorias"
    )
    conta = forms.ModelChoiceField(
        queryset=Conta.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas as contas"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user, ativo=True)
            self.fields['conta'].queryset = Conta.objects.filter(usuario=user, ativo=True)

class ReceitaFiltroForm(forms.Form):
    data_inicial = forms.DateField(label='Data inicial', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    data_final = forms.DateField(label='Data final', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    categoria = forms.ModelChoiceField(label='Categoria', queryset=Categoria.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    conta = forms.ModelChoiceField(label='Conta', queryset=Conta.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    valor_min = forms.DecimalField(label='Valor mínimo', required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    valor_max = forms.DecimalField(label='Valor máximo', required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    recorrente = forms.NullBooleanField(label='Recorrente?', required=False, widget=forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Todos'), ('True', 'Sim'), ('False', 'Não')]))
    busca_texto = forms.CharField(label='Buscar descrição', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user, ativo=True, tipo__in=['receita', 'ambos'])
            self.fields['conta'].queryset = Conta.objects.filter(usuario=user, ativo=True)

class DespesaFiltroForm(forms.Form):
    data_inicial = forms.DateField(label='Data inicial', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    data_final = forms.DateField(label='Data final', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    categoria = forms.ModelChoiceField(label='Categoria', queryset=Categoria.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    conta = forms.ModelChoiceField(label='Conta', queryset=Conta.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    valor_min = forms.DecimalField(label='Valor mínimo', required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    valor_max = forms.DecimalField(label='Valor máximo', required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    recorrente = forms.NullBooleanField(label='Recorrente?', required=False, widget=forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Todos'), ('True', 'Sim'), ('False', 'Não')]))
    busca_texto = forms.CharField(label='Buscar descrição', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user, ativo=True, tipo__in=['despesa', 'ambos'])
            self.fields['conta'].queryset = Conta.objects.filter(usuario=user, ativo=True)

class CartaoCreditoForm(forms.ModelForm):
    class Meta:
        model = CartaoCredito
        fields = ['nome', 'numero', 'bandeira', 'titular', 'data_vencimento_fatura', 'data_fechamento_fatura', 'limite_total', 'conta_pagamento', 'chave_seguranca', 'observacoes', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nome do cartão'}),
            'numero': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'maxlength': '20', 'placeholder': 'Apenas os 4 últimos dígitos'}),
            'bandeira': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'titular': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nome do titular'}),
            'data_vencimento_fatura': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1, 'max': 31, 'placeholder': 'Dia do vencimento'}),
            'data_fechamento_fatura': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1, 'max': 31, 'placeholder': 'Dia do fechamento'}),
            'limite_total': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0.01', 'placeholder': 'Limite total'}),
            'conta_pagamento': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'chave_seguranca': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'maxlength': '10', 'placeholder': 'CVV'}),
            'observacoes': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Observações'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['conta_pagamento'].queryset = Conta.objects.filter(usuario=user, ativo=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()')) 

class FaturaForm(forms.ModelForm):
    class Meta:
        model = Fatura
        fields = ['cartao', 'valor', 'vencimento', 'paga', 'ajustada', 'data_pagamento']
        widgets = {
            'cartao': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'paga': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ajustada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            qs_cartao = CartaoCredito.objects.filter(usuario=user, ativo=True)
            if self.instance and self.instance.pk and self.instance.cartao and self.instance.cartao not in qs_cartao:
                qs_cartao = CartaoCredito.objects.filter(pk=self.instance.cartao.pk) | qs_cartao
            self.fields['cartao'].queryset = qs_cartao
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.add_input(Button('cancel', 'Cancelar', css_class='btn-secondary', onclick='history.back()'))
    def clean(self):
        cleaned_data = super().clean()
        cartao = cleaned_data.get('cartao')
        vencimento = cleaned_data.get('vencimento')
        if cartao and vencimento:
            qs = Fatura.objects.filter(cartao=cartao, vencimento=vencimento)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe uma fatura para este cartão com este vencimento.')
        return cleaned_data 