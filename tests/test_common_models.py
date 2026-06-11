from services.common.models import AOI, Artifact, Citation, DateRange


def test_aoi_bbox():
    aoi = AOI(name="sample", bbox=(-122.5, 37.7, -122.3, 37.9))
    assert len(aoi.bbox) == 4


def test_artifact_defaults_to_no_citations():
    art = Artifact(kind="geojson", uri="data/out/detections.geojson")
    assert art.citations == []


def test_daterange_and_citation():
    dr = DateRange(start="2023-06-01", end="2023-06-30")
    cite = Citation(source="kb:sentinel-2", detail="10 day revisit")
    assert dr.start < dr.end
    assert cite.source.startswith("kb:")
