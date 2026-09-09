from backend.app.analytics import haversine_m, traffic_density


def test_haversine_zero_distance():
    assert haversine_m(17.385044, 78.486671, 17.385044, 78.486671) == 0


def test_traffic_density_levels():
    low = traffic_density(1, 1_000_000, 40)
    high = traffic_density(40, 1_000_000, 5)
    assert low["score"] < high["score"]
    assert high["level"] in {"high", "critical"}
