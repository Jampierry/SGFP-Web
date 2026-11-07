-- SGFP: esquema inicial (Postgres / Supabase). Fase 2 do plano de migração.
-- Regras de referência: docs/regras.md. Isolamento por usuário via RLS.
-- Dinheiro: numeric(14,2). Chaves: uuid. Nada de CVV nem número completo de cartão.

-- ===== Tabelas ================================================================
create table public.categorias (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  nome text not null check (length(nome) between 1 and 100),
  descricao text not null default '',
  tipo text not null default 'ambos' check (tipo in ('receita','despesa','ambos')),
  cor text not null default '#007bff' check (cor ~ '^#[0-9a-fA-F]{6}$'),
  icone text not null default 'fas fa-tag',
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, nome),
  unique (id, user_id)
);

create table public.contas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  nome text not null check (length(nome) between 1 and 100),
  tipo text not null default 'corrente'
    check (tipo in ('corrente','poupanca','investimento','cartao_credito','dinheiro','outros')),
  saldo_inicial numeric(14,2) not null default 0,
  descricao text not null default '',
  cor text not null default '#28a745' check (cor ~ '^#[0-9a-fA-F]{6}$'),
  icone text not null default 'fas fa-wallet',
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, nome),
  unique (id, user_id)
);

create table public.cartoes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  nome text not null check (length(nome) between 1 and 100),
  ultimos4 char(4) check (ultimos4 ~ '^[0-9]{4}$'),   -- só os 4 últimos dígitos
  bandeira text not null default 'visa'
    check (bandeira in ('visa','mastercard','elo','amex','hipercard','diners','outros')),
  titular text not null,
  dia_vencimento smallint not null check (dia_vencimento between 1 and 31),
  dia_fechamento smallint not null check (dia_fechamento between 1 and 31),
  limite_total numeric(14,2) not null check (limite_total >= 0),
  conta_pagamento_id uuid not null,
  observacoes text not null default '',
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id),
  foreign key (conta_pagamento_id, user_id) references public.contas (id, user_id) on delete restrict
);

create table public.faturas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  cartao_id uuid not null,
  vencimento date not null,
  valor_ajustado numeric(14,2),            -- preenchido = fatura "ajustada" manualmente
  paga boolean not null default false,
  data_pagamento date,
  unique (cartao_id, vencimento),
  unique (id, user_id),
  foreign key (cartao_id, user_id) references public.cartoes (id, user_id) on delete cascade
);

create table public.receitas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  descricao text not null check (length(descricao) between 1 and 200),
  valor numeric(14,2) not null check (valor >= 0.01),
  data date not null,
  categoria_id uuid not null,
  conta_id uuid not null,
  observacoes text not null default '',
  recorrente boolean not null default false,
  frequencia text check (frequencia in ('semanal','quinzenal','mensal','bimestral','trimestral','semestral','anual')),
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (categoria_id, user_id) references public.categorias (id, user_id) on delete restrict,
  foreign key (conta_id, user_id) references public.contas (id, user_id) on delete restrict
);

create table public.despesas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  descricao text not null check (length(descricao) between 1 and 200),
  valor numeric(14,2) not null check (valor >= 0.01),
  data date not null,
  categoria_id uuid not null,
  conta_id uuid not null,
  observacoes text not null default '',
  recorrente boolean not null default false,
  frequencia text check (frequencia in ('semanal','quinzenal','mensal','bimestral','trimestral','semestral','anual')),
  tipo_pagamento text not null default 'dinheiro'
    check (tipo_pagamento in ('dinheiro','cartao_credito_avista','cartao_credito_parcelado')),
  cartao_id uuid,
  fatura_id uuid,
  grupo_parcelas uuid,                      -- liga as parcelas de uma mesma compra
  parcelas smallint check (parcelas is null or parcelas between 1 and 120),
  parcela_atual smallint check (parcela_atual is null or parcela_atual >= 1),
  data_compra date,                         -- data real da compra (data = vencimento da parcela)
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (categoria_id, user_id) references public.categorias (id, user_id) on delete restrict,
  foreign key (conta_id, user_id) references public.contas (id, user_id) on delete restrict,
  foreign key (cartao_id, user_id) references public.cartoes (id, user_id) on delete set null (cartao_id),
  foreign key (fatura_id, user_id) references public.faturas (id, user_id) on delete set null (fatura_id)
);

create table public.transferencias (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  descricao text not null check (length(descricao) between 1 and 200),
  valor numeric(14,2) not null check (valor >= 0.01),
  taxa numeric(14,2) not null default 0 check (taxa >= 0),
  data date not null,
  conta_origem_id uuid not null,
  conta_destino_id uuid not null,
  observacoes text not null default '',
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (conta_origem_id <> conta_destino_id),
  foreign key (conta_origem_id, user_id) references public.contas (id, user_id) on delete restrict,
  foreign key (conta_destino_id, user_id) references public.contas (id, user_id) on delete restrict
);

create table public.metas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  titulo text not null check (length(titulo) between 1 and 200),
  descricao text not null default '',
  valor_meta numeric(14,2) not null check (valor_meta >= 0.01),
  valor_atual numeric(14,2) not null default 0,
  data_inicio date not null,
  data_fim date not null check (data_fim >= data_inicio),
  tipo text not null default 'economia'
    check (tipo in ('economia','investimento','pagamento','compra','outros')),
  categoria_id uuid,
  conta_id uuid,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (categoria_id, user_id) references public.categorias (id, user_id) on delete set null (categoria_id),
  foreign key (conta_id, user_id) references public.contas (id, user_id) on delete set null (conta_id)
);

create table public.notificacoes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  titulo text not null,
  mensagem text not null,
  tipo text not null default 'info' check (tipo in ('alerta','info','sucesso','aviso','erro')),
  lida boolean not null default false,
  link text,
  icone text not null default 'fas fa-bell',
  created_at timestamptz not null default now(),
  lida_em timestamptz
);

create table public.configuracoes (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  moeda_padrao char(3) not null default 'BRL',
  formato_data text not null default 'DD/MM/YYYY',
  icones_coloridos boolean not null default false,
  notificacoes_email boolean not null default true,
  dashboard_tipo text not null default 'moderno' check (dashboard_tipo in ('moderno','classico')),
  dashboard_layout text not null default 'default' check (dashboard_layout in ('default','compact','wide','tall')),
  dashboard_tema text not null default 'corona-dark',
  dashboard_refresh_min integer not null default 5 check (dashboard_refresh_min >= 0),
  dashboard_animations boolean not null default true,
  dashboard_dragdrop boolean not null default true,
  escala_interface integer not null default 100 check (escala_interface in (70,80,90,100,110,120,130)),
  updated_at timestamptz not null default now()
);

create index on public.receitas (user_id, data desc);
create index on public.despesas (user_id, data desc);
create index on public.despesas (conta_id);
create index on public.despesas (fatura_id);
create index on public.receitas (conta_id);
create index on public.transferencias (conta_origem_id);
create index on public.transferencias (conta_destino_id);
create index on public.notificacoes (user_id, lida, created_at desc);

-- ===== RLS: cada usuário só vê e altera o que é dele ==========================
do $$
declare t text;
begin
  foreach t in array array['categorias','contas','cartoes','faturas','receitas','despesas',
                           'transferencias','metas','notificacoes','configuracoes']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format($p$create policy "dono" on public.%I for all to authenticated
                      using (user_id = (select auth.uid()))
                      with check (user_id = (select auth.uid()))$p$, t);
  end loop;
end $$;

-- ===== Saldos e faturas (calculados, nunca gravados) ==========================
-- saldo = inicial + receitas - despesas + transferências recebidas - enviadas (só ativos).
-- Decisão: a taxa da transferência é debitada da conta de ORIGEM (o Django a ignorava).
create view public.contas_saldo with (security_invoker = true) as
select c.*,
  c.saldo_inicial
  + coalesce((select sum(valor) from public.receitas r where r.conta_id = c.id and r.ativo), 0)
  - coalesce((select sum(valor) from public.despesas d where d.conta_id = c.id and d.ativo), 0)
  + coalesce((select sum(valor) from public.transferencias t where t.conta_destino_id = c.id and t.ativo), 0)
  - coalesce((select sum(valor + taxa) from public.transferencias t where t.conta_origem_id = c.id and t.ativo), 0)
  as saldo_atual
from public.contas c;

create view public.faturas_valor with (security_invoker = true) as
select f.*,
  coalesce(f.valor_ajustado,
           (select sum(d.valor) from public.despesas d where d.fatura_id = f.id and d.ativo), 0) as valor,
  f.valor_ajustado is not null as ajustada,
  case when f.paga then 'Paga' when f.vencimento < current_date then 'Vencida' else 'Em aberto' end as status
from public.faturas f;

create view public.cartoes_limite with (security_invoker = true) as
select c.*,
  coalesce((select sum(d.valor) from public.despesas d where d.cartao_id = c.id and d.ativo), 0) as limite_utilizado,
  c.limite_total - coalesce((select sum(d.valor) from public.despesas d where d.cartao_id = c.id and d.ativo), 0) as limite_disponivel
from public.cartoes c;

-- ===== Regra única de fatura/parcelamento ====================================
-- Vencimento da fatura em que uma compra cai: compra até o dia do fechamento
-- (inclusive) vai para o mês; depois, para o mês seguinte. Dia inexistente
-- (ex.: 31 em fevereiro) vira o último dia do mês.
create function public.fatura_vencimento(p_dia_fechamento int, p_dia_vencimento int, p_data date, p_deslocamento int default 0)
returns date language sql immutable as $$
  with base as (
    select (date_trunc('month', p_data)
            + make_interval(months => (case when extract(day from p_data) <= p_dia_fechamento then 0 else 1 end) + p_deslocamento))::date as mes
  )
  select least(mes + (p_dia_vencimento - 1),
               ((mes + interval '1 month') - interval '1 day')::date)
  from base
$$;

-- Cria despesa no cartão (à vista ou parcelada) de forma atômica. Parcelas:
-- round(valor/n,2); o resto de centavos vai na última. Cada parcela cai na
-- fatura seguinte e tem data = vencimento da fatura (como o código original pretendia).
-- SECURITY INVOKER: respeita RLS do chamador.
create function public.criar_despesa_cartao(
  p_cartao_id uuid, p_conta_id uuid, p_categoria_id uuid, p_descricao text,
  p_valor numeric, p_data date, p_parcelas int default 1, p_observacoes text default ''
) returns setof public.despesas
language plpgsql security invoker set search_path = public as $$
declare
  v_cartao public.cartoes%rowtype;
  v_n int := greatest(coalesce(p_parcelas, 1), 1);
  v_parcela numeric(14,2);
  v_resto numeric(14,2);
  v_grupo uuid := gen_random_uuid();
  v_venc date;
  v_fatura uuid;
  v_valor numeric(14,2);
  i int;
begin
  select * into v_cartao from public.cartoes where id = p_cartao_id;
  if not found then raise exception 'cartão não encontrado'; end if;
  v_parcela := round(p_valor / v_n, 2);
  v_resto := round(p_valor - v_parcela * v_n, 2);
  for i in 0 .. v_n - 1 loop
    v_venc := public.fatura_vencimento(v_cartao.dia_fechamento, v_cartao.dia_vencimento, p_data, i);
    insert into public.faturas (cartao_id, vencimento) values (p_cartao_id, v_venc)
      on conflict (cartao_id, vencimento) do update set vencimento = excluded.vencimento
      returning id into v_fatura;
    v_valor := v_parcela + case when i = v_n - 1 then v_resto else 0 end;
    return query
      insert into public.despesas (descricao, valor, data, categoria_id, conta_id, observacoes,
         tipo_pagamento, cartao_id, fatura_id, grupo_parcelas, parcelas, parcela_atual, data_compra)
      values (p_descricao, v_valor, case when v_n > 1 then v_venc else p_data end, p_categoria_id, p_conta_id, p_observacoes,
         case when v_n > 1 then 'cartao_credito_parcelado' else 'cartao_credito_avista' end,
         p_cartao_id, v_fatura, case when v_n > 1 then v_grupo end, v_n, i + 1, p_data)
      returning *;
  end loop;
end $$;

-- ===== Novo usuário: cria a configuração ======================================
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.configuracoes (user_id) values (new.id) on conflict do nothing;
  return new;
end $$;

create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();
