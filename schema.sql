CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE candidates (
  id UUID PRIMARY KEY,
  healpix BIGINT NOT NULL,
  ra_deg DOUBLE PRECISION NOT NULL,
  dec_deg DOUBLE PRECISION NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  product_id TEXT NOT NULL,
  product_url TEXT NOT NULL,
  score NUMERIC(5,2),
  evidence JSONB NOT NULL,
  geom GEOGRAPHY(POINT, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(ra_deg, dec_deg), 4326)::geography) STORED
);
CREATE INDEX candidates_healpix_idx ON candidates (healpix, observed_at);
CREATE INDEX candidates_geom_idx ON candidates USING GIST (geom);

CREATE TABLE reviews (
  id UUID PRIMARY KEY,
  candidate_id UUID REFERENCES candidates(id),
  reviewer_id TEXT NOT NULL,
  label TEXT NOT NULL CHECK (label IN ('likely_real_motion', 'likely_artifact', 'needs_follow_up')),
  note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
