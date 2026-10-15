-- Codex-Design shared memory. Apply only to the owner-selected Supabase project.
-- Provision access_keys with SHA-256 hashes through an authorized admin surface;
-- never put raw tokens in this migration. Public RPCs require scoped tokens.
-- review_status is a human decision. This database cannot verify local evidence,
-- licenses, visual originality, or creative approval.
BEGIN;
CREATE SCHEMA IF NOT EXISTS codex_design_memory;

CREATE TABLE IF NOT EXISTS codex_design_memory.access_keys (
  namespace text NOT NULL CHECK (namespace ~ '^[a-z0-9][a-z0-9._:-]{0,127}$'),
  key_hash text NOT NULL CHECK (key_hash ~ '^[0-9a-f]{64}$'),
  permission text NOT NULL CHECK (permission IN ('read', 'write')),
  revoked boolean NOT NULL DEFAULT false,
  PRIMARY KEY (namespace, key_hash)
);
CREATE TABLE IF NOT EXISTS codex_design_memory.revisions (
  namespace text NOT NULL,
  id text NOT NULL,
  revision bigint NOT NULL CHECK (revision > 0),
  payload_text text NOT NULL,
  payload jsonb GENERATED ALWAYS AS (payload_text::jsonb) STORED,
  payload_sha256 text NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
  operation_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT pg_catalog.clock_timestamp(),
  PRIMARY KEY (namespace, id, revision)
);
CREATE TABLE IF NOT EXISTS codex_design_memory.heads (
  namespace text NOT NULL,
  id text NOT NULL,
  revision bigint NOT NULL,
  PRIMARY KEY (namespace, id),
  FOREIGN KEY (namespace, id, revision)
    REFERENCES codex_design_memory.revisions (namespace, id, revision)
);
CREATE TABLE IF NOT EXISTS codex_design_memory.operations (
  namespace text NOT NULL,
  operation_id uuid NOT NULL,
  expected_revision bigint NOT NULL,
  payload_sha256 text NOT NULL,
  receipt jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT pg_catalog.clock_timestamp(),
  PRIMARY KEY (namespace, operation_id)
);
ALTER TABLE codex_design_memory.access_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE codex_design_memory.revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE codex_design_memory.heads ENABLE ROW LEVEL SECURITY;
ALTER TABLE codex_design_memory.operations ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION codex_design_memory.assert_access(
  p_access_key text, p_namespace text, p_write boolean DEFAULT false
) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF p_namespace IS NULL OR p_namespace !~ '^[a-z0-9][a-z0-9._:-]{0,127}$'
     OR p_access_key IS NULL OR pg_catalog.length(p_access_key) NOT BETWEEN 32 AND 512 THEN
    RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'MEMORY_ACCESS_DENIED';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM codex_design_memory.access_keys k
    WHERE k.namespace = p_namespace AND NOT k.revoked
      AND k.key_hash = pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(p_access_key, 'UTF8')), 'hex')
      AND (NOT p_write OR k.permission = 'write')
  ) THEN
    RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'MEMORY_ACCESS_DENIED';
  END IF;
END;
$$;

CREATE OR REPLACE FUNCTION codex_design_memory.assert_payload(p_text text)
RETURNS jsonb LANGUAGE plpgsql SET search_path = '' AS $$
DECLARE
  v jsonb;
  item jsonb;
  field text;
BEGIN
  IF p_text IS NULL OR pg_catalog.octet_length(p_text) NOT BETWEEN 1 AND 64000 THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  BEGIN
    v := p_text::jsonb;
  EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END;
  IF pg_catalog.jsonb_typeof(v) IS DISTINCT FROM 'object' THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  IF NOT (v ?& ARRAY['id', 'kind', 'title', 'content', 'tags', 'review_status', 'evidence'])
     OR EXISTS (SELECT 1 FROM pg_catalog.jsonb_object_keys(v) k
                WHERE k NOT IN ('id', 'kind', 'title', 'content', 'tags', 'review_status', 'evidence', 'provenance')) THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  FOREACH field IN ARRAY ARRAY['id', 'kind'] LOOP
    IF pg_catalog.jsonb_typeof(v -> field) IS DISTINCT FROM 'string'
       OR (v ->> field) !~ '^[a-z0-9][a-z0-9._:-]{0,127}$' THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
  END LOOP;
  FOREACH field IN ARRAY ARRAY['title', 'content'] LOOP
    IF pg_catalog.jsonb_typeof(v -> field) IS DISTINCT FROM 'string'
       OR (v ->> field) !~ '[^[:space:]]'
       OR pg_catalog.length(v ->> field) > (CASE WHEN field = 'title' THEN 200 ELSE 12000 END) THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
  END LOOP;
  IF pg_catalog.jsonb_typeof(v -> 'review_status') IS DISTINCT FROM 'string'
     OR (v ->> 'review_status') NOT IN ('unverified', 'proposal', 'accepted', 'rejected', 'blocked') THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  IF pg_catalog.jsonb_typeof(v -> 'tags') IS DISTINCT FROM 'array'
     OR pg_catalog.jsonb_typeof(v -> 'evidence') IS DISTINCT FROM 'array' THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  IF pg_catalog.jsonb_array_length(v -> 'tags') > 32
     OR pg_catalog.jsonb_array_length(v -> 'evidence') > 32 THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  FOR item IN SELECT value FROM pg_catalog.jsonb_array_elements(v -> 'tags') LOOP
    IF pg_catalog.jsonb_typeof(item) IS DISTINCT FROM 'string'
       OR (item #>> '{}') !~ '[^[:space:]]'
       OR pg_catalog.length(item #>> '{}') > 64 THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
  END LOOP;
  IF (SELECT pg_catalog.count(DISTINCT value) FROM pg_catalog.jsonb_array_elements(v -> 'tags'))
     <> pg_catalog.jsonb_array_length(v -> 'tags') THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  FOR item IN SELECT value FROM pg_catalog.jsonb_array_elements(v -> 'evidence') LOOP
    IF pg_catalog.jsonb_typeof(item) IS DISTINCT FROM 'object' THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
    IF NOT (item ?& ARRAY['path', 'sha256'])
       OR EXISTS (SELECT 1 FROM pg_catalog.jsonb_object_keys(item) k WHERE k NOT IN ('path', 'sha256'))
       OR pg_catalog.jsonb_typeof(item -> 'path') IS DISTINCT FROM 'string'
       OR pg_catalog.length(pg_catalog.btrim(item ->> 'path')) NOT BETWEEN 1 AND 2048
       OR (item ->> 'path') !~ '[^[:space:]]'
       OR pg_catalog.strpos(item ->> 'path', '://') > 0
       OR pg_catalog.left(item ->> 'path', 2) IN ('//', pg_catalog.chr(92) || pg_catalog.chr(92))
       OR pg_catalog.jsonb_typeof(item -> 'sha256') IS DISTINCT FROM 'string'
       OR (item ->> 'sha256') !~ '^[0-9a-f]{64}$' THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
  END LOOP;
  IF (SELECT pg_catalog.count(DISTINCT value ->> 'path') FROM pg_catalog.jsonb_array_elements(v -> 'evidence'))
     <> pg_catalog.jsonb_array_length(v -> 'evidence') THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  IF v ->> 'review_status' = 'accepted' AND pg_catalog.jsonb_array_length(v -> 'evidence') = 0 THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  IF v ? 'provenance' THEN
    IF pg_catalog.jsonb_typeof(v -> 'provenance') IS DISTINCT FROM 'object'
       OR pg_catalog.length((v -> 'provenance')::text) > 8192 THEN
      RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
    END IF;
  END IF;
  RETURN v;
END;
$$;

CREATE OR REPLACE FUNCTION codex_design_memory.immutable_revision()
RETURNS trigger LANGUAGE plpgsql SET search_path = '' AS $$
BEGIN
  RAISE EXCEPTION USING ERRCODE = '55000', MESSAGE = 'MEMORY_HISTORY_IMMUTABLE';
END;
$$;
CREATE OR REPLACE TRIGGER revisions_immutable BEFORE UPDATE OR DELETE ON codex_design_memory.revisions
  FOR EACH ROW EXECUTE FUNCTION codex_design_memory.immutable_revision();
CREATE OR REPLACE TRIGGER operations_immutable BEFORE UPDATE OR DELETE ON codex_design_memory.operations
  FOR EACH ROW EXECUTE FUNCTION codex_design_memory.immutable_revision();

CREATE OR REPLACE FUNCTION public.codex_design_memory_get(
  p_access_key text, p_namespace text, p_id text, p_revision bigint DEFAULT NULL
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE
  row codex_design_memory.revisions%ROWTYPE;
BEGIN
  PERFORM codex_design_memory.assert_access(p_access_key, p_namespace);
  IF p_id IS NULL OR p_id !~ '^[a-z0-9][a-z0-9._:-]{0,127}$'
     OR (p_revision IS NOT NULL AND p_revision <= 0) THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  SELECT r.* INTO row FROM codex_design_memory.revisions r
  WHERE r.namespace = p_namespace AND r.id = p_id AND r.revision = COALESCE(p_revision,
    (SELECT h.revision FROM codex_design_memory.heads h WHERE h.namespace = p_namespace AND h.id = p_id));
  IF NOT FOUND THEN RETURN pg_catalog.jsonb_build_object('status', 'NOT_FOUND'); END IF;
  RETURN pg_catalog.jsonb_build_object('status', 'READ', 'record',
    pg_catalog.to_jsonb(row) - 'payload');
END;
$$;

CREATE OR REPLACE FUNCTION public.codex_design_memory_query(
  p_access_key text, p_namespace text, p_query text DEFAULT NULL, p_kind text DEFAULT NULL,
  p_limit integer DEFAULT 20, p_offset integer DEFAULT 0, p_history_id text DEFAULT NULL
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  PERFORM codex_design_memory.assert_access(p_access_key, p_namespace);
  IF p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 100 OR p_offset IS NULL OR p_offset < 0
     OR (p_query IS NOT NULL AND (pg_catalog.length(p_query) NOT BETWEEN 1 AND 256 OR p_query !~ '[^[:space:]]'))
     OR (p_kind IS NOT NULL AND p_kind !~ '^[a-z0-9][a-z0-9._:-]{0,127}$')
     OR (p_history_id IS NOT NULL AND p_history_id !~ '^[a-z0-9][a-z0-9._:-]{0,127}$') THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  RETURN (
    WITH source AS (
      SELECT r.* FROM codex_design_memory.revisions r
      WHERE r.namespace = p_namespace
        AND (p_history_id IS NOT NULL AND r.id = p_history_id OR p_history_id IS NULL AND EXISTS (
          SELECT 1 FROM codex_design_memory.heads h WHERE h.namespace = r.namespace AND h.id = r.id AND h.revision = r.revision))
        AND (p_kind IS NULL OR r.payload ->> 'kind' = p_kind)
    ), scored AS (
      SELECT s.*, CASE WHEN p_query IS NULL THEN 0 ELSE (
        SELECT COALESCE(pg_catalog.sum(
          (pg_catalog.strpos(pg_catalog.lower(s.payload ->> 'title'), token) > 0)::integer * 4
          + (pg_catalog.strpos(pg_catalog.lower((s.payload -> 'tags')::text), token) > 0)::integer * 3
          + (pg_catalog.strpos(pg_catalog.lower(s.payload ->> 'content'), token) > 0)::integer
        ), 0) FROM pg_catalog.unnest(pg_catalog.regexp_split_to_array(pg_catalog.lower(pg_catalog.btrim(p_query)), '\s+')) token
        WHERE token <> ''
      ) END score FROM source s
    ), matching AS MATERIALIZED (
      SELECT * FROM scored WHERE p_query IS NULL OR score > 0
    ), page AS (
      SELECT * FROM matching ORDER BY CASE WHEN p_history_id IS NOT NULL THEN revision END DESC,
        score DESC, id, revision DESC LIMIT p_limit OFFSET p_offset
    )
    SELECT pg_catalog.jsonb_build_object('status', 'FOUND',
      'records', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(page) - 'payload' - 'score'
        ORDER BY CASE WHEN p_history_id IS NOT NULL THEN revision END DESC, score DESC, id, revision DESC) FROM page), '[]'::jsonb),
      'total', (SELECT pg_catalog.count(*) FROM matching), 'offset', p_offset, 'limit', p_limit,
      'next_offset', CASE WHEN p_offset::bigint + p_limit < (SELECT pg_catalog.count(*) FROM matching)
                          THEN p_offset::bigint + p_limit ELSE NULL END)
  );
END;
$$;

CREATE OR REPLACE FUNCTION public.codex_design_memory_put(
  p_access_key text, p_namespace text, p_payload_text text, p_expected_revision bigint, p_operation_id uuid
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' SET lock_timeout = '5s' AS $$
DECLARE
  value jsonb;
  record_id text;
  payload_hash text;
  current_revision bigint;
  current_row codex_design_memory.revisions%ROWTYPE;
  prior codex_design_memory.operations%ROWTYPE;
  receipt jsonb;
  result_status text;
BEGIN
  PERFORM codex_design_memory.assert_access(p_access_key, p_namespace, true);
  IF p_expected_revision IS NULL OR p_expected_revision < 0 OR p_operation_id IS NULL THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  value := codex_design_memory.assert_payload(p_payload_text);
  record_id := value ->> 'id';
  payload_hash := pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(p_payload_text, 'UTF8')), 'hex');
  -- An operation can be retried for another ID: serialize that identity first.
  PERFORM pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended('codex-design-operation:' || p_namespace || ':' || p_operation_id::text, 0));
  SELECT * INTO prior FROM codex_design_memory.operations o WHERE o.namespace = p_namespace AND o.operation_id = p_operation_id;
  IF FOUND THEN
    IF prior.expected_revision <> p_expected_revision OR prior.payload_sha256 <> payload_hash
       OR prior.receipt -> 'record' ->> 'payload_text' <> p_payload_text THEN
      RAISE EXCEPTION USING ERRCODE = 'P0001', MESSAGE = 'MEMORY_OPERATION_CONFLICT';
    END IF;
    RETURN prior.receipt;
  END IF;
  PERFORM pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended('codex-design-record:' || p_namespace || ':' || record_id, 0));
  SELECT h.revision INTO current_revision FROM codex_design_memory.heads h
    WHERE h.namespace = p_namespace AND h.id = record_id;
  current_revision := COALESCE(current_revision, 0);
  IF current_revision <> p_expected_revision THEN
    RAISE EXCEPTION USING ERRCODE = 'P0001', MESSAGE = 'MEMORY_REVISION_CONFLICT';
  END IF;
  SELECT * INTO current_row FROM codex_design_memory.revisions r
    WHERE r.namespace = p_namespace AND r.id = record_id AND r.revision = current_revision;
  IF FOUND AND current_row.payload_text = p_payload_text THEN
    result_status := 'UNCHANGED';
  ELSE
    current_revision := current_revision + 1;
    INSERT INTO codex_design_memory.revisions(namespace, id, revision, payload_text, payload_sha256, operation_id)
      VALUES (p_namespace, record_id, current_revision, p_payload_text, payload_hash, p_operation_id) RETURNING * INTO current_row;
    INSERT INTO codex_design_memory.heads(namespace, id, revision) VALUES (p_namespace, record_id, current_revision)
      ON CONFLICT (namespace, id) DO UPDATE SET revision = EXCLUDED.revision;
    result_status := 'STORED';
  END IF;
  receipt := pg_catalog.jsonb_build_object('status', result_status, 'namespace', p_namespace,
    'operation_id', p_operation_id, 'expected_revision', p_expected_revision, 'payload_sha256', payload_hash,
    'record', pg_catalog.to_jsonb(current_row) - 'payload');
  INSERT INTO codex_design_memory.operations(namespace, operation_id, expected_revision, payload_sha256, receipt)
    VALUES (p_namespace, p_operation_id, p_expected_revision, payload_hash, receipt);
  RETURN receipt;
END;
$$;

CREATE OR REPLACE FUNCTION public.codex_design_memory_operation(
  p_access_key text, p_namespace text, p_operation_id uuid
) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE receipt jsonb;
BEGIN
  PERFORM codex_design_memory.assert_access(p_access_key, p_namespace);
  IF p_operation_id IS NULL THEN
    RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'MEMORY_INPUT_INVALID';
  END IF;
  SELECT o.receipt INTO receipt FROM codex_design_memory.operations o
    WHERE o.namespace = p_namespace AND o.operation_id = p_operation_id;
  RETURN COALESCE(receipt, pg_catalog.jsonb_build_object('status', 'NOT_FOUND'));
END;
$$;

REVOKE ALL ON SCHEMA codex_design_memory FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL ON ALL TABLES IN SCHEMA codex_design_memory FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA codex_design_memory FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL ON FUNCTION public.codex_design_memory_get(text,text,text,bigint) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.codex_design_memory_query(text,text,text,text,integer,integer,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.codex_design_memory_put(text,text,text,bigint,uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.codex_design_memory_operation(text,text,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.codex_design_memory_get(text,text,text,bigint) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.codex_design_memory_query(text,text,text,text,integer,integer,text) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.codex_design_memory_put(text,text,text,bigint,uuid) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.codex_design_memory_operation(text,text,uuid) TO anon, authenticated, service_role;
COMMIT;
