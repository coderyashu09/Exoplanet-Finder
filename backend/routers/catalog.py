"""Curated astronomical catalog objects router with authentic NASA parameters and scientific categorization."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


class CatalogPlanet(BaseModel):
    name: str
    letter: str
    period_days: float
    radius_earth: float
    semi_major_axis_au: Optional[float] = None
    equilibrium_temp_k: Optional[int] = None
    discovery_year: int
    discovery_method: str
    is_habitable_zone: bool
    discovered_by_ai: bool
    color: str
    description: str


class CatalogObject(BaseModel):
    id: str
    name: str
    kepid: int
    coordinates_3d: Dict[str, float]  # x, y, z for Three.js placement
    spectral_type: str
    distance_ly: int
    constellation: str
    mass_solar: float
    radius_solar: float
    temperature_k: int
    confirmed_planets_count: int
    planets: List[CatalogPlanet]
    visualization_category: str  # "Observationally supported object" | "Catalog-parameter-based visualization" | "Illustrative educational object"
    scientific_summary: str
    provenance_reference: str


CATALOG_OBJECTS: List[CatalogObject] = [
    CatalogObject(
        id="kepler-90",
        name="Kepler-90 (KOI-351)",
        kepid=11442793,
        coordinates_3d={"x": 0.0, "y": 0.0, "z": 0.0},
        spectral_type="G0V Main Sequence",
        distance_ly=2840,
        constellation="Draco",
        mass_solar=1.20,
        radius_solar=1.20,
        temperature_k=6080,
        confirmed_planets_count=8,
        visualization_category="Catalog-parameter-based visualization",
        scientific_summary="The first extrasolar system discovered with 8 confirmed planets. Kepler-90i was discovered by a 1D CNN trained on Kepler data (Shallue & Vanderburg 2017).",
        provenance_reference="NASA Exoplanet Archive / Shallue & Vanderburg (2018) AJ 155 94",
        planets=[
            CatalogPlanet(
                name="Kepler-90b",
                letter="b",
                period_days=7.008,
                radius_earth=1.31,
                semi_major_axis_au=0.074,
                equilibrium_temp_k=1056,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#FF6B6B",
                description="Hot rocky planet in a rapid 7-day orbit.",
            ),
            CatalogPlanet(
                name="Kepler-90c",
                letter="c",
                period_days=8.719,
                radius_earth=1.18,
                semi_major_axis_au=0.089,
                equilibrium_temp_k=981,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#FFA94D",
                description="Small rocky inner world orbiting close to the host star.",
            ),
            CatalogPlanet(
                name="Kepler-90i",
                letter="i",
                period_days=14.449,
                radius_earth=1.32,
                semi_major_axis_au=0.123,
                equilibrium_temp_k=709,
                discovery_year=2017,
                discovery_method="Transit / Deep Learning CNN",
                is_habitable_zone=False,
                discovered_by_ai=True,
                color="#35D49A",
                description="Historic exoplanet discovered using a 1D Convolutional Neural Network.",
            ),
            CatalogPlanet(
                name="Kepler-90d",
                letter="d",
                period_days=59.736,
                radius_earth=2.88,
                semi_major_axis_au=0.320,
                equilibrium_temp_k=518,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#4DABF7",
                description="Sub-Neptune world with volatile envelope.",
            ),
            CatalogPlanet(
                name="Kepler-90e",
                letter="e",
                period_days=91.939,
                radius_earth=2.67,
                semi_major_axis_au=0.420,
                equilibrium_temp_k=448,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#38D9A9",
                description="Warm sub-Neptune orbiting inside Mercury's relative distance.",
            ),
            CatalogPlanet(
                name="Kepler-90f",
                letter="f",
                period_days=124.914,
                radius_earth=2.89,
                semi_major_axis_au=0.480,
                equilibrium_temp_k=409,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#74C0FC",
                description="Intermediate gas-rich planet.",
            ),
            CatalogPlanet(
                name="Kepler-90g",
                letter="g",
                period_days=210.607,
                radius_earth=8.13,
                semi_major_axis_au=0.710,
                equilibrium_temp_k=340,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#B197FC",
                description="Gas giant similar in size to Saturn.",
            ),
            CatalogPlanet(
                name="Kepler-90h",
                letter="h",
                period_days=331.601,
                radius_earth=11.32,
                semi_major_axis_au=1.010,
                equilibrium_temp_k=292,
                discovery_year=2013,
                discovery_method="Transit",
                is_habitable_zone=True,
                discovered_by_ai=False,
                color="#DA77F2",
                description="Jupiter-sized gas giant orbiting at the outer edge (1.01 AU) of the system.",
            ),
        ],
    ),
    CatalogObject(
        id="kepler-186",
        name="Kepler-186",
        kepid=8120608,
        coordinates_3d={"x": 42.0, "y": 14.0, "z": -30.0},
        spectral_type="M1V Red Dwarf",
        distance_ly=582,
        constellation="Cygnus",
        mass_solar=0.54,
        radius_solar=0.52,
        temperature_k=3755,
        confirmed_planets_count=5,
        visualization_category="Observationally supported object",
        scientific_summary="Hosts Kepler-186f, the first validated Earth-sized planet orbiting in the circumstellar habitable zone of another star.",
        provenance_reference="NASA Exoplanet Archive / Quintana et al. (2014) Science 344 6181",
        planets=[
            CatalogPlanet(
                name="Kepler-186f",
                letter="f",
                period_days=129.944,
                radius_earth=1.17,
                semi_major_axis_au=0.432,
                equilibrium_temp_k=188,
                discovery_year=2014,
                discovery_method="Transit",
                is_habitable_zone=True,
                discovered_by_ai=False,
                color="#35D49A",
                description="First validated Earth-sized planet found in the habitable zone of a star outside our Solar System.",
            ),
        ],
    ),
    CatalogObject(
        id="kepler-452",
        name="Kepler-452",
        kepid=8311864,
        coordinates_3d={"x": -48.0, "y": -18.0, "z": 36.0},
        spectral_type="G2V Solar Twin",
        distance_ly=1402,
        constellation="Cygnus",
        mass_solar=1.04,
        radius_solar=1.11,
        temperature_k=5757,
        confirmed_planets_count=1,
        visualization_category="Observationally supported object",
        scientific_summary="Hosts Kepler-452b, often called Earth's older, larger cousin, orbiting a G2V star nearly identical to our Sun.",
        provenance_reference="NASA Exoplanet Archive / Jenkins et al. (2015) AJ 150 56",
        planets=[
            CatalogPlanet(
                name="Kepler-452b",
                letter="b",
                period_days=384.843,
                radius_earth=1.63,
                semi_major_axis_au=1.046,
                equilibrium_temp_k=265,
                discovery_year=2015,
                discovery_method="Transit",
                is_habitable_zone=True,
                discovered_by_ai=False,
                color="#49E4E8",
                description="Super-Earth planet receiving approximately 1.1x the solar energy Earth receives from the Sun.",
            ),
        ],
    ),
    CatalogObject(
        id="kepler-22",
        name="Kepler-22",
        kepid=10666592,
        coordinates_3d={"x": 58.0, "y": -22.0, "z": 18.0},
        spectral_type="G5V Sun-like",
        distance_ly=635,
        constellation="Cygnus",
        mass_solar=0.97,
        radius_solar=0.98,
        temperature_k=5518,
        confirmed_planets_count=1,
        visualization_category="Observationally supported object",
        scientific_summary="The first star system where Kepler confirmed a transiting exoplanet within the habitable zone of a Sun-like star.",
        provenance_reference="NASA Exoplanet Archive / Borucki et al. (2012) ApJ 745 120",
        planets=[
            CatalogPlanet(
                name="Kepler-22b",
                letter="b",
                period_days=289.862,
                radius_earth=2.38,
                semi_major_axis_au=0.849,
                equilibrium_temp_k=262,
                discovery_year=2011,
                discovery_method="Transit",
                is_habitable_zone=True,
                discovered_by_ai=False,
                color="#63B3FF",
                description="The first planet confirmed by NASA Kepler to orbit comfortably inside its star's habitable zone.",
            ),
        ],
    ),
    CatalogObject(
        id="kepler-10",
        name="Kepler-10",
        kepid=11904151,
        coordinates_3d={"x": -36.0, "y": 32.0, "z": -48.0},
        spectral_type="G4V Star",
        distance_ly=608,
        constellation="Draco",
        mass_solar=0.91,
        radius_solar=1.06,
        temperature_k=5708,
        confirmed_planets_count=2,
        visualization_category="Observationally supported object",
        scientific_summary="Historic system featuring Kepler-10b, the first confirmed rocky exoplanet discovered by the Kepler Space Telescope.",
        provenance_reference="NASA Exoplanet Archive / Batalha et al. (2011) ApJ 729 27",
        planets=[
            CatalogPlanet(
                name="Kepler-10b",
                letter="b",
                period_days=0.837,
                radius_earth=1.47,
                semi_major_axis_au=0.017,
                equilibrium_temp_k=2169,
                discovery_year=2011,
                discovery_method="Transit",
                is_habitable_zone=False,
                discovered_by_ai=False,
                color="#FF657A",
                description="Tidally locked rocky world covered in molten lava oceans, orbiting in under 20 hours.",
            ),
        ],
    ),
    CatalogObject(
        id="kepler-16",
        name="Kepler-16",
        kepid=12644769,
        coordinates_3d={"x": 25.0, "y": -36.0, "z": -40.0},
        spectral_type="Circumbinary Binary (K+M)",
        distance_ly=245,
        constellation="Cygnus",
        mass_solar=0.69,
        radius_solar=0.65,
        temperature_k=4450,
        confirmed_planets_count=1,
        visualization_category="Observationally supported object",
        scientific_summary="The first confirmed circumbinary planet—orbiting around two stars rather than one, like the fictional Tatooine.",
        provenance_reference="NASA Exoplanet Archive / Doyle et al. (2011) Science 333 1602",
        planets=[
            CatalogPlanet(
                name="Kepler-16b",
                letter="b",
                period_days=228.776,
                radius_earth=8.45,
                semi_major_axis_au=0.705,
                equilibrium_temp_k=180,
                discovery_year=2011,
                discovery_method="Transit",
                is_habitable_zone=True,
                discovered_by_ai=False,
                color="#FFBE55",
                description="Cold Saturn-mass gas giant orbiting around two mutually orbiting stars.",
            ),
        ],
    ),
]


@router.get("/objects", response_model=List[CatalogObject])
def list_catalog_objects() -> List[CatalogObject]:
    """Returns verified astronomical objects with 3D spatial coordinates and observational parameters."""
    return CATALOG_OBJECTS


@router.get("/objects/{object_id}", response_model=CatalogObject)
def get_catalog_object(object_id: str) -> CatalogObject:
    for obj in CATALOG_OBJECTS:
        if obj.id == object_id or str(obj.kepid) == object_id:
            return obj
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Astronomical object '{object_id}' not found in verified catalog.")

