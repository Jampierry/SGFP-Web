// ETL Django -> Postgres (Fase 3).
//
// Uso:
//   python manage.py dumpdata auth.user core configuracoes --indent 1 > dump.json
//   node django_para_sql.mjs dump.json usuarios.json carga.sql
// usuarios.json: { "<username do Django>": "<uuid do usuário no Supabase Auth>" }
// Rode carga.sql no SQL Editor do Supabase (papel postgres ignora RLS). NUNCA commite dump/carga.
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const FREQ = new Set(['semanal', 'quinzenal', 'mensal', 'bimestral', 'trimestral', 'semestral', 'anual']);

export const lit = (v) => {
  if (v === null || v === undefined || v === '') return 'null';
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  if (typeof v === 'number') return String(v);
  return `'${String(v).replace(/'/g, "''")}'`;
};
// Texto obrigatório: '' é valor válido (não vira null).
const txt = (v) => (v === null || v === undefined ? "''" : `'${String(v).replace(/'/g, "''")}'`);

// uuid determinístico (Fatura tem pk inteira no Django).
export const uuidDe = (chave) => {
  const h = createHash('sha1').update(chave).digest('hex');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-5${h.slice(13, 16)}-a${h.slice(17, 20)}-${h.slice(20, 32)}`;
};

const ins = (tabela, cols, vals) => `insert into public.${tabela} (${cols.join(', ')}) values (${vals.join(', ')});`;
const cor = (c, padrao) => (/^#[0-9a-fA-F]{6}$/.test(c || '') ? c : padrao);

export function gerarSql(dump, mapaUsuarios) {
  const porModelo = {};
  for (const o of dump) (porModelo[o.model] ||= []).push(o);
  const L = (m) => porModelo[m] || [];

  const usuarios = {};
  const faltando = [];
  for (const u of L('auth.user')) {
    const uuid = mapaUsuarios[u.fields.username];
    if (uuid) usuarios[u.pk] = uuid; else faltando.push(u.fields.username);
  }
  if (faltando.length) throw new Error(`Usuários sem mapeamento no usuarios.json: ${faltando.join(', ')}`);
  const uid = (f) => {
    const v = usuarios[f.usuario];
    if (!v) throw new Error(`usuario ${f.usuario} não encontrado`);
    return lit(v);
  };
  const avisos = [];
  const out = ['begin;'];

  for (const { pk, fields: f } of L('core.categoria'))
    out.push(ins('categorias',
      ['id', 'user_id', 'nome', 'descricao', 'tipo', 'cor', 'icone', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.nome), txt(f.descricao), lit(f.tipo), lit(cor(f.cor, '#007bff')), lit(f.icone), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));

  for (const { pk, fields: f } of L('core.conta'))
    out.push(ins('contas',
      ['id', 'user_id', 'nome', 'tipo', 'saldo_inicial', 'descricao', 'cor', 'icone', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.nome), lit(f.tipo), lit(Number(f.saldo_inicial)), txt(f.descricao), lit(cor(f.cor, '#28a745')), lit(f.icone), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));

  for (const { pk, fields: f } of L('core.cartaocredito')) {
    const digitos = String(f.numero || '').replace(/\D/g, '');
    out.push(ins('cartoes',
      ['id', 'user_id', 'nome', 'ultimos4', 'bandeira', 'titular', 'dia_vencimento', 'dia_fechamento', 'limite_total', 'conta_pagamento_id', 'observacoes', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.nome), digitos.length >= 4 ? lit(digitos.slice(-4)) : 'null', lit(f.bandeira), lit(f.titular),
        lit(f.data_vencimento_fatura), lit(f.data_fechamento_fatura), lit(Number(f.limite_total)), lit(f.conta_pagamento), txt(f.observacoes), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));
  } // chave_seguranca (CVV) é descartada de propósito.

  const cartaoDono = Object.fromEntries(L('core.cartaocredito').map((c) => [c.pk, c.fields.usuario]));
  for (const { pk, fields: f } of L('core.fatura'))
    out.push(ins('faturas',
      ['id', 'user_id', 'cartao_id', 'vencimento', 'valor_ajustado', 'paga', 'data_pagamento'],
      [lit(uuidDe(`fatura:${pk}`)), lit(usuarios[cartaoDono[f.cartao]]), lit(f.cartao), lit(f.vencimento),
        f.ajustada ? lit(Number(f.valor)) : 'null', lit(f.paga), lit(f.data_pagamento)]));

  const freq = (f) => (FREQ.has(f.frequencia) ? lit(f.frequencia) : 'null');
  for (const { pk, fields: f } of L('core.receita'))
    out.push(ins('receitas',
      ['id', 'user_id', 'descricao', 'valor', 'data', 'categoria_id', 'conta_id', 'observacoes', 'recorrente', 'frequencia', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.descricao), lit(Number(f.valor)), lit(f.data), lit(f.categoria), lit(f.conta), txt(f.observacoes), lit(f.recorrente), freq(f), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));

  for (const { pk, fields: f } of L('core.despesa')) {
    if (f.tipo_pagamento === 'cartao_credito_parcelado' && (f.parcelas || 1) > 1 && (f.parcela_atual || 1) === 1 &&
      !L('core.despesa').some((o) => o.pk !== pk && o.fields.descricao === f.descricao && o.fields.parcela_atual > 1))
      avisos.push(`Despesa ${pk} ("${f.descricao}"): parcelada em ${f.parcelas}x mas gravada com o valor cheio (bug antigo); mantida como está.`);
    out.push(ins('despesas',
      ['id', 'user_id', 'descricao', 'valor', 'data', 'categoria_id', 'conta_id', 'observacoes', 'recorrente', 'frequencia', 'tipo_pagamento', 'cartao_id', 'fatura_id', 'parcelas', 'parcela_atual', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.descricao), lit(Number(f.valor)), lit(f.data), lit(f.categoria), lit(f.conta), txt(f.observacoes), lit(f.recorrente), freq(f), lit(f.tipo_pagamento || 'dinheiro'),
        lit(f.cartao), f.fatura ? lit(uuidDe(`fatura:${f.fatura}`)) : 'null', lit(f.parcelas), lit(f.parcela_atual), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));
  }

  for (const { pk, fields: f } of L('core.transferencia'))
    out.push(ins('transferencias',
      ['id', 'user_id', 'descricao', 'valor', 'taxa', 'data', 'conta_origem_id', 'conta_destino_id', 'observacoes', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.descricao), lit(Number(f.valor)), lit(Number(f.taxa || 0)), lit(f.data), lit(f.conta_origem), lit(f.conta_destino), txt(f.observacoes), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));

  for (const { pk, fields: f } of L('core.meta'))
    out.push(ins('metas',
      ['id', 'user_id', 'titulo', 'descricao', 'valor_meta', 'valor_atual', 'data_inicio', 'data_fim', 'tipo', 'categoria_id', 'conta_id', 'ativo', 'created_at', 'updated_at'],
      [lit(pk), uid(f), lit(f.titulo), txt(f.descricao), lit(Number(f.valor_meta)), lit(Number(f.valor_atual || 0)), lit(f.data_inicio), lit(f.data_fim), lit(f.tipo), lit(f.categoria), lit(f.conta), lit(f.ativo), lit(f.data_criacao), lit(f.data_atualizacao)]));

  for (const { fields: f } of L('core.notificacao'))
    out.push(ins('notificacoes',
      ['user_id', 'titulo', 'mensagem', 'tipo', 'lida', 'link', 'icone', 'created_at', 'lida_em'],
      [uid(f), lit(f.titulo), txt(f.mensagem), lit(f.tipo), lit(f.lida), lit(f.link), lit(f.icone), lit(f.data_criacao), lit(f.data_leitura)]));

  for (const { fields: f } of [...L('core.configuracao'), ...L('configuracoes.configuracao')])
    out.push(`insert into public.configuracoes (user_id, moeda_padrao, formato_data, icones_coloridos, notificacoes_email, dashboard_tipo, dashboard_layout, dashboard_tema, dashboard_refresh_min, dashboard_animations, dashboard_dragdrop, escala_interface)
values (${uid(f)}, ${lit(f.moeda_padrao || 'BRL')}, ${lit(f.formato_data || 'DD/MM/YYYY')}, ${lit(!!f.icones_coloridos)}, ${lit(f.notificacoes_email ?? true)}, ${lit(f.dashboard_tipo || 'moderno')}, ${lit(f.dashboard_layout || 'default')}, ${lit(f.dashboard_tema || 'corona-dark')}, ${lit(f.dashboard_refresh ?? 5)}, ${lit(f.dashboard_animations ?? true)}, ${lit(f.dashboard_dragdrop ?? true)}, ${lit(f.escala_interface || 100)})
on conflict (user_id) do update set moeda_padrao = excluded.moeda_padrao, formato_data = excluded.formato_data, icones_coloridos = excluded.icones_coloridos,
  notificacoes_email = excluded.notificacoes_email, dashboard_tipo = excluded.dashboard_tipo, dashboard_layout = excluded.dashboard_layout, dashboard_tema = excluded.dashboard_tema,
  dashboard_refresh_min = excluded.dashboard_refresh_min, dashboard_animations = excluded.dashboard_animations, dashboard_dragdrop = excluded.dashboard_dragdrop, escala_interface = excluded.escala_interface;`);

  out.push('commit;');
  return { sql: out.join('\n') + '\n', avisos };
}

// Compara o saldo gravado no Django (saldo_atual) com a view contas_saldo.
// Diferença esperada = taxas de transferência (agora debitadas) e saldos defasados do Django.
export async function conferirSaldos(db, dump) {
  const taxas = {};
  for (const t of dump.filter((o) => o.model === 'core.transferencia' && o.fields.ativo))
    taxas[t.fields.conta_origem] = (taxas[t.fields.conta_origem] || 0) + Number(t.fields.taxa || 0);
  const { rows } = await db.query('select id, nome, saldo_atual::float8 as novo from contas_saldo');
  const novo = Object.fromEntries(rows.map((r) => [r.id, r]));
  const r2 = (n) => Math.round(n * 100) / 100;
  return dump.filter((o) => o.model === 'core.conta').map(({ pk, fields: f }) => {
    const antigo = Number(f.saldo_atual);
    const taxa = taxas[pk] || 0;
    const dif = r2(novo[pk].novo - (antigo - taxa));
    return { conta: f.nome, antigo, taxa, novo: novo[pk].novo, diferenca_inesperada: dif };
  });
}

if (process.argv[1] && process.argv[1].endsWith('django_para_sql.mjs')) {
  const [, , dumpPath, mapaPath, saida] = process.argv;
  if (!dumpPath || !mapaPath || !saida) {
    console.error('Uso: node django_para_sql.mjs dump.json usuarios.json carga.sql');
    process.exit(1);
  }
  const { sql, avisos } = gerarSql(JSON.parse(readFileSync(dumpPath, 'utf8')), JSON.parse(readFileSync(mapaPath, 'utf8')));
  writeFileSync(saida, sql);
  avisos.forEach((a) => console.warn('AVISO:', a));
  console.log(`OK: ${saida} (${sql.split('\n').length} linhas)`);
}
