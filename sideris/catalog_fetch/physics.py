import math
from typing import Optional, Tuple

def calculate_absolute_magnitude_and_luminosity(mag_apparent: Optional[float], dist_ly: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculates the absolute magnitude and the luminosity relative to the Sun.
    """
    if mag_apparent is not None and dist_ly is not None and dist_ly > 0:
        dist_pc = dist_ly / 3.26156
        abs_mag = round(mag_apparent - 5 * (math.log10(dist_pc) - 1), 2)
        # Calculate luminosity compared to the Sun (absolute magnitude of 4.83)
        luminosity = round(10**(0.4 * (4.83 - abs_mag)), 2)
        return abs_mag, luminosity
    return None, None

def calculate_distance_ly(parallax_mas: float) -> Optional[float]:
    """
    Calculates the distance in light-years from the parallax in milliarcseconds.
    """
    if parallax_mas is not None and parallax_mas > 0:
        # 1 parsec = 1000 / parallax(mas). 1 parsec = 3.26156 light years.
        dist_ly = round((1000.0 / parallax_mas) * 3.26156, 2)
        return dist_ly
    return None
