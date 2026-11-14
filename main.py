"""OrbitWatch API: deployable starting point for survey-candidate ranking."""
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="OrbitWatch API", version="0.2.0")

class Evidence(BaseModel):
    motion: float = Field(ge=0, le=100)
    signal: float = Field(ge=0, le=100)
    cross_match: float = Field(ge=0, le=100)
    artifact_risk: float = Field(ge=0, le=100)

class Weights(BaseModel):
    motion: float = Field(default=35, ge=0)
    signal: float = Field(default=30, ge=0)
    cross_match: float = Field(default=20, ge=0)
    artifact_risk: float = Field(default=15, ge=0)

class ScoreRequest(BaseModel):
    evidence: Evidence
    weights: Weights = Weights()

class ReviewRequest(BaseModel):
    candidate_id: str = Field(min_length=3, max_length=80)
    label: str = Field(pattern="^(likely_real_motion|likely_artifact|needs_follow_up)$")
    note: str = Field(default="", max_length=500)

reviews: list[ReviewRequest] = []

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/v1/score')
def score(request: ScoreRequest):
    evidence, weights = request.evidence, request.weights
    denominator = weights.motion + weights.signal + weights.cross_match + weights.artifact_risk
    value = (evidence.motion * weights.motion + evidence.signal * weights.signal + evidence.cross_match * weights.cross_match - evidence.artifact_risk * weights.artifact_risk) / max(denominator, 1)
    return {'score': round(max(value, 0), 2), 'components': evidence.model_dump(), 'weights': weights.model_dump()}

@app.get('/v1/spherex/explorer')
def spherex_explorer(
    ra: float = Query(ge=0, lt=360),
    dec: float = Query(ge=-90, le=90),
    radius_arcsec: float = Query(default=60, gt=0, le=3600),
):
    """Return a provenance-preserving IRSA Data Explorer link for a sky coordinate."""
    return {
        'source': 'NASA/IRSA SPHEREx Data Explorer',
        'url': f'https://irsa.ipac.caltech.edu/applications/spherex/?api=spectral-images&ra={ra}&dec={dec}&sr={radius_arcsec}s',
        'query': {'ra_deg': ra, 'dec_deg': dec, 'radius_arcsec': radius_arcsec},
        'next_step': 'Download calibrated cutouts and retain observation/product identifiers with every candidate.',
    }

@app.get('/v1/known-objects/{designation}')
def known_object(designation: str):
    """Check a user-supplied designation against JPL SBDB; never labels an object as new."""
    if not designation.strip() or len(designation) > 100:
        raise HTTPException(status_code=400, detail='Provide a short asteroid or comet designation.')
    endpoint = f'https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={quote(designation.strip())}'
    try:
        with urlopen(endpoint, timeout=8) as response:
            return {'source': 'NASA JPL Small-Body Database', 'result': response.read().decode('utf-8')}
    except URLError as error:
        raise HTTPException(status_code=503, detail=f'JPL lookup is temporarily unavailable: {error.reason}') from error

@app.post('/v1/reviews', status_code=201)
def create_review(review: ReviewRequest):
    """Prototype audit endpoint. Replace this in-memory list with Postgres in production."""
    reviews.append(review)
    return {'stored': True, 'review_count': len(reviews), 'record': review}
