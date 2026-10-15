// Disposable PostgreSQL regression fixture; never connects to Supabase.
// Install PGlite outside the repo and set PGLITE_MODULE to its dist/index.js,
// or use an already installed @electric-sql/pglite. No runtime dependency.
import assert from 'node:assert/strict';
import { createHash, randomUUID } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { after, before, test } from 'node:test';

const { PGlite } = await import(process.env.PGLITE_MODULE
  ? pathToFileURL(process.env.PGLITE_MODULE).href : '@electric-sql/pglite');
const db = new PGlite();
const migration = await readFile(new URL('./design_brain_memory_supabase.sql', import.meta.url), 'utf8');
const namespace = 'codex-design';
// These disposable fixture tokens have no relationship to deployed credentials.
const writer = 'fixture-write-'.repeat(5);
const reader = 'fixture-read-'.repeat(5);
const revoked = 'fixture-revoked-'.repeat(5);
const other = 'fixture-other-'.repeat(5);
const hash = text => createHash('sha256').update(text, 'utf8').digest('hex');
const payload = (id, changes = {}) => ({
  id, kind: 'layout_case', title: 'PPTX layout evidence',
  content: 'Measured geometry only; MAIN must review originality.',
  tags: ['pptx'], review_status: 'unverified', evidence: [], ...changes,
});
// Parameter values are bound, never interpolated as SQL.
const sql = {
  get: 'SELECT public.codex_design_memory_get($1,$2,$3,$4) AS result',
  query: 'SELECT public.codex_design_memory_query($1,$2,$3,$4,$5,$6,$7) AS result',
  put: 'SELECT public.codex_design_memory_put($1,$2,$3,$4,$5) AS result',
  operation: 'SELECT public.codex_design_memory_operation($1,$2,$3) AS result',
};
const safeError = failure => Object.assign(new Error(failure.message), { code: failure.code });
const rpc = async (method, args, connection = db) => {
  try { return (await connection.query(sql[method], args)).rows[0].result; }
  catch (failure) { throw safeError(failure); } // Never print bound tokens on test failures.
};
const put = (value, expected = 0, operation = randomUUID(), token = writer, connection = db) =>
  rpc('put', [token, namespace, JSON.stringify(value), expected, operation], connection);
const get = (id, revision = null, token = reader, connection = db) =>
  rpc('get', [token, namespace, id, revision], connection);
const query = (overrides = {}, connection = db) => {
  const options = { token: reader, scope: namespace, search: null, kind: null,
    limit: 20, offset: 0, history: null, ...overrides };
  return rpc('query', [options.token, options.scope, options.search, options.kind,
    options.limit, options.offset, options.history], connection);
};
const error = (promise, code, message) => assert.rejects(promise, failure => {
  assert.equal(failure.code, code);
  if (message) assert.equal(failure.message, message);
  return true;
});
const asRole = (role, callback) => db.transaction(async tx => {
  assert.ok(['anon', 'authenticated', 'service_role'].includes(role));
  await tx.exec(`SET LOCAL ROLE ${role}`);
  return callback(tx);
});

before(async () => {
  try {
  await db.exec('CREATE ROLE anon; CREATE ROLE authenticated; CREATE ROLE service_role;');
  await db.exec(migration);
  for (const [scope, token, permission, isRevoked] of [
    [namespace, writer, 'write', false], [namespace, reader, 'read', false],
    [namespace, revoked, 'write', true], ['other-scope', other, 'write', false],
  ]) {
    await db.query('INSERT INTO codex_design_memory.access_keys VALUES ($1,$2,$3,$4)',
      [scope, hash(token), permission, isRevoked]);
  }
  } catch (failure) { throw safeError(failure); }
});
after(async () => { await db.close(); });

test('RPC authorization is namespace scoped; read token cannot write', async () => {
  for (const role of ['anon', 'authenticated', 'service_role']) {
    assert.equal((await asRole(role, tx => get('absent', null, reader, tx))).status, 'NOT_FOUND');
    await error(asRole(role, tx => put(payload('reader-denied'), 0, randomUUID(), reader, tx)),
      '42501', 'MEMORY_ACCESS_DENIED');
  }
  for (const token of [null, 'short', revoked, other, 'not-provisioned-'.repeat(5)]) {
    await error(get('absent', null, token), '42501', 'MEMORY_ACCESS_DENIED');
  }
  await error(query({ scope: 'other-scope' }), '42501', 'MEMORY_ACCESS_DENIED');
  assert.equal((await query({ token: other, scope: 'other-scope' })).total, 0);
  const stored = await asRole('anon', tx => put(payload('anon-scoped-write'), 0, randomUUID(), writer, tx));
  assert.equal(stored.status, 'STORED');
});

test('private tables/schema/helpers deny all API roles; RLS and empty search_path remain', async () => {
  for (const role of ['anon', 'authenticated', 'service_role']) {
    for (const statement of [
      'SELECT * FROM codex_design_memory.access_keys',
      'SELECT * FROM codex_design_memory.revisions',
      'SELECT * FROM codex_design_memory.heads',
      'SELECT * FROM codex_design_memory.operations',
      "SELECT codex_design_memory.assert_payload('{}')",
    ]) await error(asRole(role, tx => tx.query(statement)), '42501');
  }
  const tables = await db.query("SELECT relrowsecurity FROM pg_catalog.pg_class WHERE relnamespace = 'codex_design_memory'::regnamespace AND relkind = 'r'");
  assert.equal(tables.rows.length, 4);
  assert.ok(tables.rows.every(row => row.relrowsecurity));
  const functions = await db.query("SELECT prosecdef, proconfig, proacl FROM pg_catalog.pg_proc WHERE pronamespace='public'::regnamespace AND proname LIKE 'codex_design_memory_%'");
  assert.equal(functions.rows.length, 4);
  for (const row of functions.rows) {
    assert.equal(row.prosecdef, true);
    assert.ok(row.proconfig.includes('search_path=""'));
    assert.ok(!row.proacl.some(acl => acl.startsWith('=')), 'PUBLIC must not inherit execute');
  }
});

test('stored UTF8 payload, immutable versions and negative decisions round trip', async () => {
  const original = payload('history-case', { title: 'Foto répété — 測定', review_status: 'rejected' });
  const first = await put(original);
  assert.equal(first.status, 'STORED');
  assert.equal(first.expected_revision, 0);
  assert.equal(first.payload_sha256, hash(JSON.stringify(original)));
  assert.equal(first.record.namespace, namespace);
  assert.equal(first.record.revision, 1);
  const second = await put({ ...original, review_status: 'blocked' }, 1);
  assert.equal(second.record.revision, 2);
  assert.equal(JSON.parse((await get(original.id, 1)).record.payload_text).review_status, 'rejected');
  assert.equal(JSON.parse((await get(original.id)).record.payload_text).review_status, 'blocked');
  const history = await query({ history: original.id, limit: 1 });
  assert.equal(history.total, 2);
  assert.equal(history.records[0].revision, 2);
  assert.equal(history.next_offset, 1);
  assert.equal((await query({ history: original.id, offset: 1 })).records[0].revision, 1);
});

test('CAS rejects stale writes before same-payload idempotency; valid unchanged makes only receipt', async () => {
  const value = payload('cas-case');
  await put(value);
  await error(put(value, 0), 'P0001', 'MEMORY_REVISION_CONFLICT');
  const operation = randomUUID();
  const unchanged = await put(value, 1, operation);
  assert.equal(unchanged.status, 'UNCHANGED');
  assert.equal(unchanged.record.revision, 1);
  assert.equal(unchanged.operation_id, operation);
  assert.equal((await query({ history: value.id })).total, 1);
});

test('operation retry returns original receipt after newer revision; entire request conflicts', async () => {
  const value = payload('operation-case');
  const operation = randomUUID();
  const first = await put(value, 0, operation);
  await put({ ...value, content: 'A later recorded decision.' }, 1);
  assert.deepEqual(await put(value, 0, operation), first);
  assert.deepEqual(await rpc('operation', [reader, namespace, operation]), first);
  assert.equal(first.expected_revision, 0);
  assert.equal(first.payload_sha256, hash(JSON.stringify(value)));
  await error(put(value, 1, operation), 'P0001', 'MEMORY_OPERATION_CONFLICT');
  await error(put({ ...value, id: 'another-operation-target' }, 0, operation), 'P0001', 'MEMORY_OPERATION_CONFLICT');
  await error(put({ ...value, content: 'Conflicting bytes.' }, 0, operation), 'P0001', 'MEMORY_OPERATION_CONFLICT');
  assert.equal((await rpc('operation', [reader, namespace, randomUUID()])).status, 'NOT_FOUND');
});

test('malformed payloads reject without head or operation receipt', async () => {
  const base = payload('malformed-case');
  const malformed = [null, [], {}, { ...base, secret: 'unknown field' },
    { ...base, id: '' }, { ...base, kind: true }, { ...base, title: '\t\n' },
    { ...base, content: 'x'.repeat(12001) }, { ...base, review_status: 'PASS' },
    { ...base, tags: ['x', 'x'] }, { ...base, tags: [null] }, { ...base, evidence: {} },
    { ...base, evidence: [{ path: '', sha256: 'a'.repeat(64) }] },
    { ...base, evidence: [{ path: 'proof.png', sha256: 'INVALID' }] },
    { ...base, evidence: [{ path: 'https://example.invalid/proof', sha256: 'a'.repeat(64) }] },
    { ...base, evidence: [{ path: '\\\\server\\proof', sha256: 'a'.repeat(64) }] },
    { ...base, evidence: [{ path: 'proof', sha256: 'a'.repeat(64), extra: 1 }] },
    { ...base, evidence: Array(2).fill({ path: 'proof', sha256: 'a'.repeat(64) }) },
    { ...base, review_status: 'accepted' }, { ...base, provenance: [] }];
  for (const value of malformed) {
    const operation = randomUUID();
    await error(put(value, 0, operation), '22023', 'MEMORY_INPUT_INVALID');
    assert.equal((await rpc('operation', [reader, namespace, operation])).status, 'NOT_FOUND');
  }
  await error(rpc('put', [writer, namespace, '{', 0, randomUUID()]), '22023', 'MEMORY_INPUT_INVALID');
  assert.equal((await get(base.id)).status, 'NOT_FOUND');
});

test('accepted payload requires structured evidence; no file/creative verification is inferred', async () => {
  const value = payload('accepted-case', { review_status: 'accepted',
    evidence: [{ path: 'reports/decision.json', sha256: 'a'.repeat(64) }],
    provenance: { reviewer: 'main', scope: 'fixture only' } });
  const result = await put(value);
  assert.equal(JSON.parse(result.record.payload_text).review_status, 'accepted');
  assert.ok(!('evidence_status' in result));
  assert.ok(!('creative_approval' in result));
});

test('list/search kind filter and stable pagination retain rejected/proposal records', async () => {
  for (const [id, title, status] of [['listing-a', 'Layout orbit', 'rejected'], ['listing-b', 'Other', 'proposal'], ['listing-c', 'Orbit measure', 'unverified']]) {
    await put(payload(id, { kind: 'listing_fixture', title, content: 'Orbit shared clue', review_status: status }));
  }
  const first = await query({ kind: 'listing_fixture', limit: 2 });
  assert.equal(first.total, 3);
  assert.equal(first.next_offset, 2);
  assert.deepEqual(first.records.map(row => row.id), ['listing-a', 'listing-b']);
  const last = await query({ kind: 'listing_fixture', limit: 2, offset: 2 });
  assert.equal(last.next_offset, null);
  assert.deepEqual(last.records.map(row => row.id), ['listing-c']);
  const found = await query({ kind: 'listing_fixture', search: 'ORBIT', limit: 1 });
  assert.equal(found.total, 3);
  assert.equal(found.records[0].id, 'listing-a');
  assert.equal((await query({ search: '\tdefinitelymissing\n' })).total, 0);
});

test('bound search input cannot execute SQL; invalid bounds/IDs fail cleanly', async () => {
  const injection = "'; DROP SCHEMA codex_design_memory CASCADE; --";
  await query({ search: injection });
  assert.equal((await get('history-case')).status, 'READ');
  for (const options of [{ limit: 0 }, { limit: 101 }, { offset: -1 }, { search: '\n\t' },
    { kind: injection }, { history: injection }]) {
    await error(query(options), '22023', 'MEMORY_INPUT_INVALID');
  }
  await error(get('bad id'), '22023', 'MEMORY_INPUT_INVALID');
  await error(get('history-case', 0), '22023', 'MEMORY_INPUT_INVALID');
  await error(put(payload('bad-expected'), -1), '22023', 'MEMORY_INPUT_INVALID');
});

test('two queued writers with same expected revision produce one winner and one CAS conflict', async () => {
  // PGlite serializes queries in one backend. This exercises CAS outcomes,
  // not independent PostgreSQL sessions or live advisory-lock contention.
  const results = await Promise.allSettled([
    put(payload('competing-case', { content: 'first writer' })),
    put(payload('competing-case', { content: 'second writer' })),
  ]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
  const loser = results.find(result => result.status === 'rejected');
  assert.equal(loser.reason.code, 'P0001');
  assert.equal(loser.reason.message, 'MEMORY_REVISION_CONFLICT');
  assert.equal((await query({ history: 'competing-case' })).total, 1);
});

test('transaction failure rolls back head, revision and operation together', async () => {
  const operation = randomUUID();
  await error(db.transaction(async tx => {
    await put(payload('rolled-back'), 0, operation, writer, tx);
    await tx.query('SELECT 1 / 0');
  }), '22012');
  assert.equal((await get('rolled-back')).status, 'NOT_FOUND');
  assert.equal((await rpc('operation', [reader, namespace, operation])).status, 'NOT_FOUND');
});

test('revision and operation UPDATE/DELETE are immutable even through migration owner role', async () => {
  for (const statement of [
    "UPDATE codex_design_memory.revisions SET payload_text = '{}' WHERE id='history-case'",
    "DELETE FROM codex_design_memory.revisions WHERE id='history-case'",
    "UPDATE codex_design_memory.operations SET expected_revision = 999",
    'DELETE FROM codex_design_memory.operations',
  ]) await error(db.query(statement), '55000', 'MEMORY_HISTORY_IMMUTABLE');
  assert.equal((await query({ history: 'history-case' })).total, 2);
});

test('migration is repeatable and preserves records, receipts and token restrictions', async () => {
  const before = await get('history-case');
  await db.exec(migration);
  assert.deepEqual(await get('history-case'), before);
  await error(put(payload('still-reader-denied'), 0, randomUUID(), reader), '42501', 'MEMORY_ACCESS_DENIED');
});
