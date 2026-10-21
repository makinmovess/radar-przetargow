CREATE TABLE IF NOT EXISTS przetargi (
    object_id        TEXT PRIMARY KEY,
    bzp_number       TEXT NOT NULL,
    przedmiot        TEXT NOT NULL,
    rodzaj           TEXT,
    kody_cpv         TEXT[],
    zamawiajacy      TEXT,
    miasto           TEXT,
    wojewodztwo      TEXT,
    termin_ofert     TIMESTAMPTZ,
    data_publikacji  TIMESTAMPTZ NOT NULL,
    tresc_html       TEXT,
    pobrano          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_przetargi_publikacja ON przetargi (data_publikacji);
CREATE INDEX IF NOT EXISTS idx_przetargi_wojewodztwo ON przetargi (wojewodztwo);
