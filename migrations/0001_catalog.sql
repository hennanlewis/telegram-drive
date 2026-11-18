-- Catálogo: árvore virtual, arquivos, referências, legendas, favoritos,
-- auditoria e estado da varredura.
-- A migration 0000 já criou users/settings e a fundação.

CREATE TABLE folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES folders (id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    name_key TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    CHECK (length(trim(name)) > 0),
    CHECK (parent_id IS NULL OR parent_id <> id)
);

-- Unicidade por pasta, sem diferenciar maiúsculas/minúsculas.
CREATE UNIQUE INDEX ux_folders_parent_name ON folders (COALESCE(parent_id, 0), name_key);
CREATE UNIQUE INDEX ux_folders_single_root ON folders ((1)) WHERE parent_id IS NULL;
CREATE INDEX idx_folders_parent ON folders (parent_id);

CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id INTEGER NOT NULL REFERENCES folders (id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    name_key TEXT NOT NULL,
    mime TEXT NOT NULL DEFAULT 'application/octet-stream',
    size_bytes INTEGER NOT NULL DEFAULT 0 CHECK (size_bytes >= 0),
    sha256 TEXT CHECK (
        sha256 IS NULL
        OR (length(sha256) = 64 AND sha256 NOT GLOB '*[^0-9a-f]*')
    ),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'trashed', 'missing')),
    trashed_from_folder_id INTEGER REFERENCES folders (id) ON DELETE RESTRICT,
    trashed_at TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1)),
    manifest_synced_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    CHECK (length(trim(name)) > 0),
    CHECK (status <> 'trashed' OR trashed_from_folder_id IS NOT NULL),
    CHECK (status <> 'trashed' OR trashed_at IS NOT NULL)
);

-- A lixeira libera o nome para um substituto ativo.
CREATE UNIQUE INDEX ux_files_folder_name_version
    ON files (folder_id, name_key, version)
    WHERE status <> 'trashed';
CREATE INDEX idx_files_folder ON files (folder_id, status);
CREATE INDEX idx_files_sha256 ON files (sha256) WHERE sha256 IS NOT NULL;
CREATE INDEX idx_files_status ON files (status);

CREATE TABLE telegram_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL REFERENCES files (id) ON DELETE CASCADE,
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    access_hash INTEGER NOT NULL,
    size_bytes INTEGER CHECK (size_bytes IS NULL OR size_bytes >= 0),
    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    width INTEGER,
    height INTEGER,
    mime TEXT,
    part_index INTEGER NOT NULL DEFAULT 1 CHECK (part_index >= 1),
    part_count INTEGER NOT NULL DEFAULT 1 CHECK (part_count >= 1 AND part_index <= part_count),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (chat_id, message_id)
);

CREATE INDEX idx_telegram_refs_file ON telegram_refs (file_id);
CREATE INDEX idx_telegram_refs_message ON telegram_refs (chat_id, message_id);

CREATE TABLE subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL REFERENCES files (id) ON DELETE CASCADE,
    source TEXT NOT NULL CHECK (source IN ('embedded', 'sidecar')),
    language TEXT,
    format TEXT NOT NULL CHECK (format IN ('srt', 'ass', 'vtt')),
    label TEXT,
    telegram_message_id INTEGER,
    cache_path TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE UNIQUE INDEX ux_subtitles_identity
    ON subtitles (file_id, source, COALESCE(language, ''), COALESCE(label, ''));

CREATE INDEX idx_subtitles_file ON subtitles (file_id);

CREATE TABLE favorites (
    file_id INTEGER PRIMARY KEY REFERENCES files (id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL CHECK (
        action IN (
            'ingest', 'move', 'rename', 'trash', 'restore', 'delete',
            'manifest', 'duplicate'
        )
    ),
    file_id INTEGER REFERENCES files (id) ON DELETE SET NULL,
    folder_id INTEGER REFERENCES folders (id) ON DELETE SET NULL,
    detail TEXT,
    result TEXT NOT NULL DEFAULT 'ok' CHECK (result IN ('ok', 'error')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX idx_activity_created_at ON activity (created_at);
CREATE INDEX idx_activity_file ON activity (file_id);

CREATE TABLE scan_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    last_message_id INTEGER,
    last_scan_at TEXT,
    last_error TEXT,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

INSERT INTO scan_state (id) VALUES (1);

-- Raiz e Inbox reservados. Os IDs ficam em settings para consulta estável.
INSERT INTO folders (parent_id, name, name_key) VALUES (NULL, 'Raiz', 'raiz');

INSERT INTO folders (parent_id, name, name_key)
SELECT id, 'Para organizar', 'para organizar'
FROM folders
WHERE parent_id IS NULL;

INSERT INTO settings (key, value)
VALUES ('root_folder_id', (SELECT CAST(id AS TEXT) FROM folders WHERE parent_id IS NULL));

INSERT INTO settings (key, value)
VALUES (
    'inbox_folder_id',
    (SELECT CAST(id AS TEXT) FROM folders WHERE name_key = 'para organizar' AND parent_id IS NOT NULL)
);
