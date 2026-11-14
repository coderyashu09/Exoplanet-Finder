"""Kepler-90 Star System Explorer router."""
from fastapi import APIRouter
from backend.schemas import Kepler90SystemResponse, Kepler90Planet

router = APIRouter(prefix="/api/kepler90", tags=["Kepler-90"])


@router.get("", response_model=Kepler90SystemResponse)
def get_kepler90_system() -> Kepler90SystemResponse:
    planets = [
        Kepler90Planet(
            name="Kepler-90b",
            letter="b",
            period_days=7.008,
            semi_major_axis_au=0.074,
            radius_earth=1.31,
            temp_kelvin=1056,
            transit_depth_ppm=340.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.00,
            color="#FF6B6B",
        ),
        Kepler90Planet(
            name="Kepler-90c",
            letter="c",
            period_days=8.719,
            semi_major_axis_au=0.089,
            radius_earth=1.18,
            temp_kelvin=981,
            transit_depth_ppm=280.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.00,
            color="#FFA94D",
        ),
        Kepler90Planet(
            name="Kepler-90i",
            letter="i",
            period_days=14.449,
            semi_major_axis_au=0.123,
            radius_earth=1.32,
            temp_kelvin=709,
            transit_depth_ppm=160.0,
            discovery_year=2017,
            discovered_by_ai=True,
            eccentricity=0.01,
            color="#69DB7C",  # Highlighted AI planet!
        ),
        Kepler90Planet(
            name="Kepler-90d",
            letter="d",
            period_days=59.736,
            semi_major_axis_au=0.320,
            radius_earth=2.88,
            temp_kelvin=518,
            transit_depth_ppm=940.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.00,
            color="#4DABF7",
        ),
        Kepler90Planet(
            name="Kepler-90e",
            letter="e",
            period_days=91.939,
            semi_major_axis_au=0.420,
            radius_earth=2.67,
            temp_kelvin=448,
            transit_depth_ppm=890.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.00,
            color="#38D9A9",
        ),
        Kepler90Planet(
            name="Kepler-90f",
            letter="f",
            period_days=124.914,
            semi_major_axis_au=0.480,
            radius_earth=2.89,
            temp_kelvin=409,
            transit_depth_ppm=980.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.01,
            color="#74C0FC",
        ),
        Kepler90Planet(
            name="Kepler-90g",
            letter="g",
            period_days=210.607,
            semi_major_axis_au=0.710,
            radius_earth=8.13,
            temp_kelvin=340,
            transit_depth_ppm=6200.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.01,
            color="#B197FC",
        ),
        Kepler90Planet(
            name="Kepler-90h",
            letter="h",
            period_days=331.601,
            semi_major_axis_au=1.010,
            radius_earth=11.32,
            temp_kelvin=292,
            transit_depth_ppm=9800.0,
            discovery_year=2013,
            discovered_by_ai=False,
            eccentricity=0.01,
            color="#DA77F2",
        ),
    ]

    solar_system_comparison = {
        "earth_orbit_au": 1.00,
        "kepler90h_orbit_au": 1.01,
        "mercury_orbit_au": 0.387,
        "all_fit_within_earth_orbit": True,
        "rocky_planets": ["b", "c", "i"],
        "sub_neptunes": ["d", "e", "f"],
        "gas_giants": ["g", "h"],
        "star_vs_sun": {
            "mass_ratio": 1.20,
            "radius_ratio": 1.20,
            "temperature_delta_k": 302,  # 6080K vs 5778K
        }
    }

    return Kepler90SystemResponse(
        star_name="Kepler-90 (KOI-351)",
        kepid=11442793,
        spectral_type="G0V Main Sequence",
        mass_solar=1.20,
        radius_solar=1.20,
        temperature_kelvin=6080,
        distance_ly=2840,
        constellation="Draco",
        total_confirmed_planets=8,
        ai_discovery_summary=(
            "In December 2017, researchers Christopher Shallue (Google AI) and Andrew Vanderburg (NASA / UT Austin) "
            "trained a deep convolutional neural network on 15,000 Kepler signals. The AI detected Kepler-90i, "
            "a small rocky planet with a 14.4-day orbit, making Kepler-90 the first known 8-planet star system beyond our own."
        ),
        planets=planets,
        solar_system_comparison=solar_system_comparison,
    )

