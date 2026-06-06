"""Chromatic Dispersion Prism Simulator - Interactive Web Interface

Core module for wavelength-dependent modal dispersion via the Sellmeier equation.
Provides foundational modeling for pulse broadening and spectral decomposition 
in dispersive media. Interactive visualization framework for understanding prism-based
spectrometers and chromatic aberration in optical systems.

Physics foundation:
- Snell's Law for refraction at glass/air boundaries
- Sellmeier equation for wavelength-dependent refractive index
- Geometric ray tracing through prism

Note: Assumes isotropic media and neglects Fresnel losses (see Limitations)
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from physics_engine import prism_deviation

# Configure Streamlit page for optimal display
st.set_page_config(
    page_title="Chromatic Dispersion Prism Simulator",
    layout="wide",
)

# Custom branded header
st.markdown(
    "<div style='text-align: center; margin-bottom: 1em;'>"
    "<h1 style='color: #1f77b4; letter-spacing: 0.15em;'>The Kinetic Codex</h1>"
    "<h3 style='color: #555; font-weight: 300;'>Core Optics Module: Chromatic Dispersion Simulator</h3>"
    "</div>",
    unsafe_allow_html=True
)

# Technical abstract - researcher tone
st.markdown(
    "**Module Overview:** This simulator models wavelength-dependent dispersion through prism-based "
    "optical systems using geometric ray tracing and the Sellmeier equation. Suitable for investigating "
    "spectral decomposition, chromatic aberration effects, and total internal reflection phenomena in "
    "dispersive media. Intended as pedagogical tool for understanding fundamental photonics principles."
)

# Sidebar control panel
with st.sidebar:
    st.header("Prism Simulation Parameters")
    
    # Material selection
    material = st.selectbox(
        "Prism Material",
        ["BK7", "Fused Silica"],
        help="BK7: standard crown glass with higher dispersion | Fused Silica: lower dispersion, precision optics"
    )
    
    # Light incident angle
    incident_angle = st.slider(
        "Incident Angle (Degrees)",
        0.0, 80.0, 45.0, step=1.0,
        help="Angle between incoming light and surface normal"
    )
    
    # Prism apex angle - critical parameter
    apex_angle = st.slider(
        "Prism Apex Angle (Degrees)",
        10.0, 80.0, 60.0, step=1.0,
        help="Angle between two refracting surfaces. Standard equilateral = 60°"
    )
    
    # Spectral range
    wavelength_min, wavelength_max = st.slider(
        "Spectrum Range (nm)",
        380, 780, (420, 680), step=10,
        help="Visible spectrum: 380nm (violet) to 780nm (red)"
    )
    
    # Ray resolution
    ray_count = st.slider(
        "Spectrum Resolution",
        15, 80, 40, step=5,
        help="Number of rays computed. Higher = smoother but slower"
    )

# Display active configuration
st.markdown(
    "### Active Prism Configuration\n"
    f"- **Material:** {material}  |  "
    f"**Apex angle:** {apex_angle:.1f}°  |  "
    f"**Incident angle:** {incident_angle:.1f}°  |  "
    f"**Wavelength range:** {wavelength_min}–{wavelength_max} nm"
)

# Calculate ray deviations
wavelengths = np.linspace(wavelength_min, wavelength_max, ray_count)
results = [prism_deviation(wl, material, incident_angle, apex_angle) for wl in wavelengths]
valid = [entry for entry in results if entry is not None]
invalid = len(results) - len(valid)

if len(valid) == 0:
    st.error(
        "❌ **No rays transmitted!** All wavelengths experienced total internal reflection. "
        "Try lowering the incident angle or reducing the apex angle."
    )
else:
    # Extract data for visualization
    deviations = np.array([entry["deviation"] for entry in valid])
    wavelengths_valid = np.array([entry["wavelength"] for entry in valid])
    
    # Map wavelengths to colors
    colors = cm.get_cmap("plasma")(
        (wavelengths_valid - wavelength_min) / max(wavelength_max - wavelength_min, 1)
    )

    # Create spectrum fan visualization
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Dispersed Spectrum Fan (Ray Tracing)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Distance from prism exit face (arbitrary units)")
    ax.set_ylabel("Vertical displacement (arbitrary units)")

    # Draw rays
    x_line = np.linspace(0, 1.2, 10)
    for entry, color in zip(valid, colors):
        ray_slope = np.tan(np.radians(entry["deviation"]))
        y_line = ray_slope * x_line
        ax.plot(x_line, y_line, color=color, linewidth=1.8, alpha=0.9)

    # Virtual screen reference
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(1.02, 0.0, "Screen", va="center", fontsize=10, fontweight='bold')

    # Axis limits
    ax.set_xlim(0, 1.25)
    y_min = min(np.min(np.tan(np.radians(deviations))) * 1.1, -0.1)
    y_max = max(np.max(np.tan(np.radians(deviations))) * 1.1, 0.1)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    # Detailed data table
    with st.expander("📊 View Detailed Dispersion Data"):
        st.write("### Wavelength-by-Wavelength Breakdown")
        display_data = [
            {
                "Wavelength (nm)": f"{entry['wavelength']:.0f}",
                "Refractive Index (n)": f"{entry['n']:.6f}",
                "Exit Angle (°)": f"{entry['deviation']:.3f}",
                "Inside Angle (°)": f"{entry['theta_inside']:.2f}",
            }
            for entry in valid
        ]
        st.table(display_data)

    # Dispersion metrics
    st.markdown("### 📈 Dispersion Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Angular Dispersion",
            f"{deviations.max() - deviations.min():.2f}°",
            help="Total spread between least and most deviated rays"
        )
    
    with col2:
        st.metric(
            "Min / Max Deviation",
            f"{deviations.min():.2f}° / {deviations.max():.2f}°",
            help="Deviation range across spectrum"
        )
    
    with col3:
        transmission_rate = (len(valid) / len(results)) * 100
        st.metric(
            "Ray Transmission",
            f"{len(valid)} / {len(results)}",
            f"{transmission_rate:.0f}% transmitted"
        )

    # TIR warning
    if invalid > 0:
        st.warning(
            f"⚠️ **Total Internal Reflection:** {invalid} wavelength(s) did not transmit. "
            f"These rays reflected back into the prism, typically at shorter wavelengths "
            f"where refractive index is higher and critical angle is lower."
        )
    
    # Assumptions and limitations
    with st.expander("⚠️ Assumptions & Limitations"):
        st.markdown(
            """**Model Assumptions:**

- **Isotropic media:** Assumes uniform refractive index independent of polarization. No birefringence modeled.
- **Geometric optics:** Assumes ray wavelengths >> crystal lattice spacing. Diffraction effects neglected.
- **Lossless interfaces:** Assumes 100% transmission (no Fresnel losses at air-glass boundaries). Real systems lose ~4% per interface due to reflection.
- **Single ray path:** Models deterministic ray tracing. Multiple scattering and internal reflections ignored.

**Known Limitations:**

- Temperature-dependent refractive index shifts not modeled (dn/dT effects).
- Non-linear optical effects (Kerr effect, Raman scattering) absent.
- Surface roughness and scatter losses ignored.
- Prism assumed perfect geometry (manufacturing aberrations not included).
- Anisotropic materials (e.g., calcite) not supported.

**Future Enhancements:**

- Fresnel reflection modeling for realistic interface losses
- Temperature-dependent coefficient updates
- Support for anisotropic (birefringent) materials
- Polarization-dependent effects
- Multi-bounce ray tracing for internal reflections
"""
        )

# Footer with attribution
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.85em; color: #999;'>"
    "The Kinetic Codex | Core Optics Module<br>"
    "Educational photonics simulation framework | 2026"
    "</div>",
    unsafe_allow_html=True
)
