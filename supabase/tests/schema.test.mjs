// Testa a migration 0001 num Postgres real em WASM (PGlite). Rodar: npm test (nesta pasta).
import { PGlite } from '@electric-sql/pglite';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';

const migration = readFileSync(new URL('../migrations/0001_schema.sql', import.meta.url), 'utf8');
const A = '00000000-0000-0000-0000-00000000000a';
const B = '00000000-0000-0000-0000-00000000000b';

// Simula o que o Supabase fornece: schema auth, auth.uid() e o papel "authenticated".
const stub = `
  create schema auth;
  create table auth.users (id uuid primary key);
  create function auth.uid() returns uuid language sql stable as
    $$ select nullif(current_setting('app.uid', true), '')::uuid $$;
  create role authenticated nologin;
  grant usage on schema auth to authenticated;
  grant execute on function auth.uid() to authenticated;
`;
const grants = `
  grant usage on schema public to authenticated;
  grant all on all tables in schema public to authenticated;
  grant execute on all functions in schema public to authenticated;
`;

async function novoBanco() {
  const db = new PGlite();
  await db.exec(stub);
  await db.exec(migration);
  await db.exec(grants);
  await db.exec(`insert into auth.users values ('${A}'), ('${B}')`); // dispara handle_new_user
  return db;
}
// Executa como usuário autenticado (RLS ativa).
async function como(db, uid, fn) {
  await db.exec(`set role authenticated; select set_config('app.uid','${uid}',false)`);
  try { return await fn(); } finally { await db.exec('reset role'); }
}
const q = (db, sql, p) => db.query(sql, p).then(r => r.rows);

async function base(db, uid) {
  return como(db, uid, async () => {
    const [cat] = await q(db, `insert into categorias(nome) values ('Geral') returning id`);
    const [c1] = await q(db, `insert into contas(nome, saldo_inicial) values ('Corrente', 1000) returning id`);
    const [c2] = await q(db, `insert into contas(nome) values ('Poupança') returning id`);
    return { cat: cat.id, c1: c1.id, c2: c2.id };
  });
}

test('novo usuário ganha configuração', async () => {
  const db = await novoBanco();
  const n = await como(db, A, () => q(db, 'select count(*)::int n from configuracoes'));
  assert.equal(n[0].n, 1);
});

test('RLS: usuário B não vê nem altera dados do A', async () => {
  const db = await novoBanco();
  await base(db, A);
  await como(db, B, async () => {
    assert.equal((await q(db, 'select count(*)::int n from contas'))[0].n, 0);
    assert.equal((await q(db, `update contas set nome = 'x' returning id`)).length, 0);
    assert.equal((await q(db, 'delete from contas returning id')).length, 0);
  });
});

test('RLS: B não consegue inserir em nome de A', async () => {
  const db = await novoBanco();
  await como(db, B, async () => {
    await assert.rejects(() => db.query(`insert into contas(user_id, nome) values ('${A}', 'invasora')`));
  });
});

test('integridade: B não consegue apontar para conta/categoria do A', async () => {
  const db = await novoBanco();
  const a = await base(db, A);
  await como(db, B, async () => {
    await assert.rejects(() => db.query(
      `insert into despesas(descricao, valor, data, categoria_id, conta_id)
       values ('x', 10, '2025-01-01', $1, $2)`, [a.cat, a.c1]));
  });
});

test('saldo: receitas, despesas e transferências (taxa debitada da origem)', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  await como(db, A, async () => {
    await db.query(`insert into receitas(descricao,valor,data,categoria_id,conta_id) values ('r',200,'2025-01-10',$1,$2)`, [x.cat, x.c1]);
    await db.query(`insert into despesas(descricao,valor,data,categoria_id,conta_id) values ('d',50.50,'2025-01-10',$1,$2)`, [x.cat, x.c1]);
    await db.query(`insert into despesas(descricao,valor,data,categoria_id,conta_id,ativo) values ('d',999,'2025-01-10',$1,$2,false)`, [x.cat, x.c1]);
    await db.query(`insert into transferencias(descricao,valor,taxa,data,conta_origem_id,conta_destino_id) values ('t',100,5,'2025-01-11',$1,$2)`, [x.c1, x.c2]);
    const s = await q(db, 'select nome, saldo_atual::text from contas_saldo order by nome');
    assert.deepEqual(s, [
      { nome: 'Corrente', saldo_atual: '1044.50' },
      { nome: 'Poupança', saldo_atual: '100.00' },
    ]);
  });
});

test('saldo: excluir despesa atualiza o saldo (corrige quirk do Django)', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  await como(db, A, async () => {
    const [d] = await q(db, `insert into despesas(descricao,valor,data,categoria_id,conta_id) values ('d',100,'2025-01-10',$1,$2) returning id`, [x.cat, x.c1]);
    await db.query('delete from despesas where id = $1', [d.id]);
    const [s] = await q(db, `select saldo_atual::text from contas_saldo where nome='Corrente'`);
    assert.equal(s.saldo_atual, '1000.00');
  });
});

test('fatura_vencimento: fechamento, virada de ano e dia 31', async () => {
  const db = await novoBanco();
  const v = async (fech, venc, data, off = 0) =>
    (await q(db, `select fatura_vencimento($1,$2,$3::date,$4)::text d`, [fech, venc, data, off]))[0].d;
  assert.equal(await v(10, 20, '2025-03-10'), '2025-03-20'); // no dia do fechamento: mês corrente
  assert.equal(await v(10, 20, '2025-03-11'), '2025-04-20'); // após: mês seguinte
  assert.equal(await v(10, 20, '2025-12-15'), '2026-01-20'); // virada de ano
  assert.equal(await v(10, 31, '2025-02-05'), '2025-02-28'); // dia inexistente
  assert.equal(await v(10, 31, '2024-02-05'), '2024-02-29'); // bissexto
  assert.equal(await v(10, 20, '2025-11-20', 2), '2026-02-20'); // após fechamento (dez) + 2 parcelas
});

async function cartaoDe(db, x) {
  return (await q(db, `insert into cartoes(nome,titular,dia_vencimento,dia_fechamento,limite_total,conta_pagamento_id)
     values ('Visa','T',20,10,5000,$1) returning id`, [x.c1]))[0].id;
}

test('à vista: uma despesa, uma fatura, reaproveitada', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  await como(db, A, async () => {
    const cartao = await cartaoDe(db, x);
    for (const dia of ['2025-03-01', '2025-03-05', '2025-03-10'])
      await q(db, `select * from criar_despesa_cartao($1,$2,$3,'c',10,$4::date)`, [cartao, x.c1, x.cat, dia]);
    await q(db, `select * from criar_despesa_cartao($1,$2,$3,'outro ciclo',999,'2025-03-11'::date)`, [cartao, x.c1, x.cat]);
    const f = await q(db, `select vencimento::text v, valor::text from faturas_valor order by vencimento`);
    assert.deepEqual(f, [{ v: '2025-03-20', valor: '30.00' }, { v: '2025-04-20', valor: '999.00' }]);
  });
});

test('parcelado: divide em n, resto na última, uma fatura por mês, atômico', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  await como(db, A, async () => {
    const cartao = await cartaoDe(db, x);
    const p = await q(db, `select valor::text, data::text, parcela_atual, parcelas, data_compra::text dc, fatura_id
        from criar_despesa_cartao($1,$2,$3,'tv',100,'2025-11-05'::date,3) order by parcela_atual`, [cartao, x.c1, x.cat]);
    assert.deepEqual(p.map(r => r.valor), ['33.33', '33.33', '33.34']);
    assert.deepEqual(p.map(r => r.data), ['2025-11-20', '2025-12-20', '2026-01-20']);
    assert.ok(p.every(r => r.parcelas === 3 && r.dc === '2025-11-05'));
    assert.equal(new Set(p.map(r => r.fatura_id)).size, 3);
    const [t] = await q(db, `select sum(valor)::text s from despesas`);
    assert.equal(t.s, '100.00');
    const [lim] = await q(db, `select limite_disponivel::text l from cartoes_limite`);
    assert.equal(lim.l, '4900.00');
  });
});

test('fatura ajustada usa o valor manual', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  await como(db, A, async () => {
    const cartao = await cartaoDe(db, x);
    await db.query(`insert into faturas(cartao_id, vencimento, valor_ajustado) values ($1,'2025-03-20',77)`, [cartao]);
    const [f] = await q(db, `select valor::text v, ajustada from faturas_valor`);
    assert.deepEqual(f, { v: '77.00', ajustada: true });
  });
});

test('RLS: B não executa criar_despesa_cartao no cartão do A', async () => {
  const db = await novoBanco();
  const x = await base(db, A);
  const cartao = await como(db, A, () => cartaoDe(db, x));
  await como(db, B, async () => {
    await assert.rejects(() => db.query(`select * from criar_despesa_cartao($1,$2,$3,'x',10,'2025-03-01'::date)`, [cartao, x.c1, x.cat]));
  });
});
