# Holography Bench

Interactive simulators for **digital holographic microscopy (DHM)** that run entirely in the browser:

| | **In-line DHM** (lensless, Gabor) | **Off-axis DHM** (Mach–Zehnder) |
|---|---|---|
| Source | laser + focusing lens + pinhole, or single-mode fibre | He–Ne 632.8 nm |
| Optics | none between sample and camera; magnification M = L / z₁ | microscope objective + tube lens in the object arm, tilted reference |
| Reconstruction | back-propagation, illumination division, iterative twin-image removal | Fourier filtering of the +1 order, blank division |
| Extras | photon budget and noise, dust and spatial filtering, pixel super-resolution, grids up to 2128 px, WebGPU engine with start-up check | carrier and bandwidth check, red blood cells and phase targets, alignment of every mount |


use this link to use the simulation https://houssain94.github.io/holographic_simulation/
