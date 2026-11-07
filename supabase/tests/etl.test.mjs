// Testa o ETL com um dump SINTÉTICO no formato do `manage.py dumpdata`.
import { PGlite } from '@electric-sql/pglite';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { gerarSql, conferirSaldos, uuidDe, lit } from '../etl/django_para_sql.mjs';

const migration = readFileSync(new URL('../migrations/0001_schema.sql', import.meta.url), 'utf8');
const UID = '00000000-0000-0000-0000-0000000000aa';
const stub = `
  create schema auth; create table auth.users (id uuid primary key);
  create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('app.uid', true), '')::uuid $$;
  create role authenticated nologin;`;

const T = '2025-01-01T10:00:00Z';
const base = { data_criacao: T, data_atualizacao: T, ativo: true, usuario: 1 };
const C1 = '11111111-1111-1111-1111-111111111111';
const C2 = '22222222-2222-2222-2222-222222222222';
const CAT = '33333333-3333-3333-3333-333333333333';
const CARTAO = '44444444-4444-4444-4444-444444444444';

const dump = [
  { model: 'auth.user', pk: 1, fields: { username: 'ana' } },
  { model: 'core.categoria', pk: CAT, fields: { ...base, nome: "Mercado d'Ana", descricao: '', tipo: 'ambos', cor: 'invalida', icone: 'fas fa-tag' } },
  { model: 'core.conta', pk: C1, fields: { ...base, nome: 'Corrente', tipo: 'corrente', saldo_inicial: '1000.00', saldo_atual: '845.00', descricao: '', cor: '#28a745', icone: 'x' } },
  { model: 'core.conta', pk: C2, fields: { ...base, nome: 'Poupança', tipo: 'poupanca', saldo_inicial: '0.00', saldo_atual: '100.00', descricao: '', cor: '#28a745', icone: 'x' } },
  { model: 'core.cartaocredito', pk: CARTAO, fields: { ...base, nome: 'Visa', numero: '4111 1111 1111 9999', bandeira: 'visa', titular: 'Ana', data_vencimento_fatura: 20, data_fechamento_fatura: 10, limite_total: '5000.00', conta_pagamento: C1, chave_seguranca: '123', observacoes: '' } },
  { model: 'core.fatura', pk: 7, fields: { cartao: CARTAO, valor: '0.00', vencimento: '2025-03-20', paga: false, ajustada: false, data_pagamento: null } },
  { model: 'core.receita', pk: 'aaaaaaaa-0000-0000-0000-000000000001', fields: { ...base, descricao: 'Salário', valor: '200.00', data: '2025-01-05', categoria: CAT, conta: C1, observacoes: '', recorrente: true, frequencia: 'mensal' } },
  { model: 'core.despesa', pk: 'bbbbbbbb-0000-0000-0000-000000000001', fields: { ...base, descricao: 'Luz', valor: '50.00', data: '2025-01-06', categoria: CAT, conta: C1, observacoes: '', recorrente: false, frequencia: '', tipo_pagamento: 'dinheiro', cartao: null, parcelas: null, fatura: null, parcela_atual: 1 } },
  { model: 'core.despesa', pk: 'bbbbbbbb-0000-0000-0000-000000000002', fields: { ...base, descricao: 'TV', valor: '5.00', data: '2025-03-05', categoria: CAT, conta: C1, observacoes: '', recorrente: false, frequencia: '', tipo_pagamento: 'cartao_credito_parcelado', cartao: CARTAO, parcelas: 3, fatura: 7, parcela_atual: 1 } },
  // Transferência com taxa (o Django ignorava a taxa no saldo).
  { model: 'core.transferencia', pk: 'cccccccc-0000-0000-0000-000000000001', fields: { ...base, descricao: 'Guardar', valor: '100.00', taxa: '2.00', data: '2025-01-07', conta_origem: C1, conta_destino: C2, observacoes: '' } },
  { model: 'core.meta', pk: 'dddddddd-0000-0000-0000-000000000001', fields: { ...base, titulo: 'Viagem', descricao: '', valor_meta: '1000.00', valor_atual: '100.00', data_inicio: '2025-01-01', data_fim: '2025-12-31', tipo: 'economia', categoria: null, conta: null } },
  { model: 'core.notificacao', pk: 1, fields: { usuario: 1, titulo: 'Oi', mensagem: 'msg', tipo: 'info', lida: false, data_criacao: T, data_leitura: null, link: '', icone: 'fas fa-bell' } },
  { model: 'core.configuracao', pk: 1, fields: { usuario: 1, dashboard_tipo: 'classico', dashboard_refresh: 10, escala_interface: 110, dashboard_tema: 'vanta-dark' } },
];

async function carregar() {
  const db = new PGlite();
  await db.exec(stub);
  await db.exec(migration);
  await db.exec(`insert into auth.users values ('${UID}')`);
  const { sql, avisos } = gerarSql(dump, { ana: UID });
  await db.exec(sql);
  return { db, sql, avisos };
}

test('carga roda sem erro e preserva contagens', async () => {
  const { db } = await carregar();
  const n = async (t) => (await db.query(`select count(*)::int n from ${t}`)).rows[0].n;
  assert.deepEqual([await n('categorias'), await n('contas'), await n('cartoes'), await n('faturas'), await n('receitas'), await n('despesas'), await n('transferencias'), await n('metas'), await n('notificacoes'), await n('configuracoes')],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 1]);
});

test('aspas, cor inválida, CVV descartado e últimos 4 dígitos', async () => {
  const { db, sql } = await carregar();
  assert.ok(!sql.includes('123\''), 'CVV não pode ir para o SQL');
  assert.ok(!sql.includes('4111'), 'número completo não pode ir para o SQL');
  assert.equal((await db.query('select nome, cor from categorias')).rows[0].nome, "Mercado d'Ana");
  assert.equal((await db.query('select cor from categorias')).rows[0].cor, '#007bff');
  assert.equal((await db.query('select ultimos4 from cartoes')).rows[0].ultimos4, '9999');
});

test('fatura recebe uuid determinístico e a despesa continua ligada', async () => {
  const { db } = await carregar();
  assert.equal(uuidDe('fatura:7'), uuidDe('fatura:7'));
  const r = (await db.query(`select d.fatura_id = f.id as ligada from despesas d join faturas f on f.id = d.fatura_id`)).rows;
  assert.equal(r.length, 1);
  assert.equal(r[0].ligada, true);
});

test('configuração do usuário substitui a padrão', async () => {
  const { db } = await carregar();
  const c = (await db.query('select dashboard_tipo, dashboard_refresh_min, escala_interface from configuracoes')).rows[0];
  assert.deepEqual(c, { dashboard_tipo: 'classico', dashboard_refresh_min: 10, escala_interface: 110 });
});

test('conferência de saldos: só a taxa explica a diferença', async () => {
  const { db } = await carregar();
  // O fixture traz saldo_atual=845 de propósito (defasado; o correto sem taxa seria 1045).
  const r = await conferirSaldos(db, dump);
  const corrente = r.find((x) => x.conta === 'Corrente');
  assert.equal(corrente.taxa, 2);
  assert.equal(corrente.novo, 1043); // 1000 + 200 - 50 - 5 - (100 + 2)
  assert.equal(corrente.diferenca_inesperada, 1043 - (845 - 2)); // 200: saldo antigo estava defasado
  const poupanca = r.find((x) => x.conta === 'Poupança');
  assert.equal(poupanca.diferenca_inesperada, 0);
});

test('avisa compra parcelada gravada com valor cheio', async () => {
  const { avisos } = await carregar();
  assert.equal(avisos.length, 1);
  assert.match(avisos[0], /TV/);
});

test('usuário sem mapeamento falha com mensagem clara', () => {
  assert.throws(() => gerarSql(dump, {}), /ana/);
});

test('lit escapa aspas', () => assert.equal(lit("d'a"), "'d''a'"));
