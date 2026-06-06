"""Physics engine for chromatic dispersion calculations.

Core module for wavelength-dependent modal dispersion via the Sellmeier equation.
Provides foundational modeling for pulse broadening and spectral decomposition 
in dispersive media. Serves as pedagogical framework for understanding prism-based
spectrometers and chromatic aberration in optical systems.

Note: This module assumes isotropic, homogeneous media. Fresnel reflection losses
at interfaces are not modeled (TODO: implement Fresnel coefficients for air-glass
boundaries in future iterations).
"""

import numpy as np


def sellmeier_index(wavelength_nm, material='BK7'):
    """Calculate refractive index using the Sellmeier equation.
    
    The Sellmeier equation accurately models how glass refractive index
    varies with wavelength across the visible and near-UV/IR spectrum.
    
    Args:
        wavelength_nm: wavelength in nanometers
        material: 'BK7' (borosilicate crown glass) or 'Fused Silica'
        
    Returns:
        Refractive index n at the given wavelength
    """
    # Convert wavelength from nm to micrometers for the Sellmeier formula
    wave_um = wavelength_nm / 1000.0 

    # Load material-specific Sellmeier coefficients
    # BK7: common optical glass used in most lens/prism systems
    # Fused Silica: lower dispersion, used in high-precision applications
    if material == 'BK7':
        B1, B2, B3 = 1.03961212, 0.231792344, 1.01046945
        C1, C2, C3 = 0.00600069867, 0.0200179144, 103.560653
    elif material == 'Fused Silica':
        B1, B2, B3 = 0.6961663, 0.4079426, 0.8974794
        C1, C2, C3 = 0.004679148, 0.013512063, 97.9340025
    else:
        raise ValueError(f"Unknown material: {material}")

    # Apply the Sellmeier equation: n² - 1 = Σ(Bᵢλ² / (λ² - Cᵢ))
    # Choice: Sellmeier over Cauchy's approximation because Sellmeier maintains accuracy
    # across visible and near-IR range. Cauchy breaks down λ < 350nm and λ > 2000nm.
    # Coefficients sourced from Schott Glass technical documentation
    n_squared = 1 + (B1 * wave_um**2) / (wave_um**2 - C1) + (B2 * wave_um**2) / (wave_um**2 - C2) + (B3 * wave_um**2) / (wave_um**2 - C3)
    return np.sqrt(n_squared)

def snells_law(n1, n2, theta_inc_deg):
    """Apply Snell's Law to calculate refraction angle at a boundary.
    
    This is the fundamental law of refraction: n₁ sin(θ₁) = n₂ sin(θ₂)
    It also detects total internal reflection (TIR) conditions.
    
    Args:
        n1: refractive index of incident medium
        n2: refractive index of transmission medium
        theta_inc_deg: incident angle in degrees (from normal)
        
    Returns:
        Refraction angle in degrees, or None if total internal reflection occurs
    """
    # Convert to radians for numpy trigonometric functions
    theta_inc_rad = np.radians(theta_inc_deg)

    # Apply Snell's Law: n₁·sin(θ₁) = n₂·sin(θ₂) → solve for sin(θ₂)
    sin_theta2 = (n1/n2) * np.sin(theta_inc_rad)

    # Check for total internal reflection (TIR)
    # If |sin(θ)| > 1, we've exceeded the critical angle θc = arcsin(n₂/n₁)
    # Beyond this angle, light reflects internally instead of refracting.
    # Limitation: This code treats it as binary (reflect/transmit). In practice,
    # partial reflection (Fresnel losses) occurs at all incident angles.
    if abs(sin_theta2) > 1.0:
        return None  # TIR detected; this wavelength is lost
    
    # Calculate refracted angle and convert back to degrees
    theta_trans_rad = np.arcsin(sin_theta2)
    return np.degrees(theta_trans_rad)

def prism_deviation(wavelength_nm, material='BK7', incident_angle_deg=45.0, apex_angle_deg=60.0):
    """Compute chromatic dispersion through a prism.
    
    Traces a light ray through a prism, calculating both refraction events
    (entry and exit) and accounting for wavelength-dependent dispersion.
    Different wavelengths experience different deviations - the foundation
    of spectral decomposition.
    
    Args:
        wavelength_nm: wavelength in nanometers (380-780 nm visible range)
        material: prism material ('BK7' or 'Fused Silica')
        incident_angle_deg: incoming ray angle relative to surface normal
        apex_angle_deg: angle between the two prism surfaces
        
    Returns:
        Dict with wavelength, refractive index, ray angles, and final deviation
        or None if total internal reflection blocks the ray
    """
    # Get refractive index for this specific wavelength
    n_prism = sellmeier_index(wavelength_nm, material)

    # STEP 1: Ray enters the prism (air → glass)
    # Apply Snell's law at the entry surface
    theta_inside = snells_law(1.0, n_prism, incident_angle_deg)
    if theta_inside is None:
        return None  # TIR at entry - shouldn't happen for normal incidence, but check anyway

    # STEP 2: Ray travels through prism interior
    # Calculate the incident angle at the exit surface using prism geometry
    theta_interior_to_exit = apex_angle_deg - theta_inside

    # STEP 3: Ray exits the prism (glass → air)
    # Apply Snell's law at the exit surface
    theta_outside = snells_law(n_prism, 1.0, theta_interior_to_exit)
    if theta_outside is None:
        return None  # TIR at exit - ray reflects back into prism and is lost

    # STEP 4: Calculate total deviation
    # This is the angle between the original ray and the final ray (D = θᵢₙ + θₑₓᵢₜ - A)
    # Shorter wavelengths deviate more (normal dispersion for λ > 200nm in glass).
    # Note: Anomalous dispersion (dn/dλ > 0) exists near absorption bands—not modeled here.
    deviation = incident_angle_deg + theta_outside - apex_angle_deg
    
    return {
        'wavelength': wavelength_nm,
        'n': n_prism,
        'theta_inside': theta_inside,
        'theta_interior_to_exit': theta_interior_to_exit,
        'theta_outside': theta_outside,
        'deviation': deviation,
    }






