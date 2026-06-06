# Prism Chromatic Dispersion Simulator
[![Live Demo](https://img.shields.io/badge/Launch-Live_Simulation-FF4B4B?style=for-the-badge&logo=streamlit)](https://prism-chromatic-dispersion-jvvjk5vumsrnnxuwma9jaa.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)

## Motivation
This project was built as a foundational optics module for **The Kinetic Codex**. Standard optical simulations often default to a constant refractive index (e.g., $n=1.5$), which is sufficient for basic geometry but fails to capture the physical reality of polychromatic light. 

This engine implements empirical material data to model wavelength-dependent modal dispersion. It was designed to serve as a visual baseline for understanding pulse broadening and spectral resolution in advanced photonic technologies.

## The Physics Engine
The core backend (`physics_engine.py`) calculates the exact spatial separation of light across boundaries. 

Instead of Cauchy's equation (which loses accuracy in the infrared regime), the engine calculates the dispersion-mapped index for every simulated wavelength using the **Sellmeier Equation**:

$$n^2(\lambda) = 1 + \frac{B_1 \lambda^2}{\lambda^2 - C_1} + \frac{B_2 \lambda^2}{\lambda^2 - C_2} + \frac{B_3 \lambda^2}{\lambda^2 - C_3}$$

Where $\lambda$ is the target wavelength in micrometers, and $B_{1,2,3}$ / $C_{1,2,3}$ are the experimentally derived coefficients for materials like Fused Silica and N-BK7. The engine then processes the vectorized geometry using standard derivations of Snell's Law to track internal reflections and exit trajectories.

## Features & UI
* **Dynamic Material Profiles:** Select between standard optical glasses to see varying dispersion spreads.
* **Plotly Integration:** Hover over individual rays on the projection plot to extract precise internal angles and refractive indices.
* **Vectorized Processing:** Uses NumPy to compute trajectories for high-resolution spectrums simultaneously rather than relying on slow `for` loops.

## Local Setup
Ensure you have Python 3.9+ installed.

1. Clone the repo:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/kinetic-codex-optics.git](https://github.com/YOUR_USERNAME/kinetic-codex-optics.git)
