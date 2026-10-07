"""Figures for chapters 2-4 of the lens + pinhole theory document.
Every curve is computed from the same equations the document gives (and the simulator uses)."""
import numpy as np, matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy.special import j0, j1

for f in fm.findSystemFonts():
    if "texgyrepagella" in f.lower(): fm.fontManager.addfont(f)
mpl.rcParams.update({
    "font.family": "TeX Gyre Pagella", "mathtext.fontset": "custom",
    "mathtext.rm": "TeX Gyre Pagella", "mathtext.it": "TeX Gyre Pagella:italic", "mathtext.bf": "TeX Gyre Pagella:bold",
    "font.size": 11, "axes.titlesize": 11.5, "axes.labelsize": 11, "legend.fontsize": 9.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6,
    "axes.edgecolor": "#555", "xtick.color": "#333", "ytick.color": "#333", "savefig.bbox": "tight", "savefig.pad_inches": 0.03})
BLUE, GREEN, ORANGE, RED, GREY, PURPLE = "#1f5fa8", "#2e8b57", "#d9822b", "#c0392b", "#7f8c8d", "#7b4fa0"

lam, f, NAL, D0, d0, z1 = 0.532, 4000.0, 0.5, 2000.0, 1.0, 500.0     # µm
NAw0 = min(D0/2/f, NAL); w00 = lam/(np.pi*NAw0); zR0 = np.pi*w00**2/lam

# ---------------------------------------------------------------- Fig 2.2: spot size vs beam diameter
D = np.linspace(0.2, 6, 600)*1000
NAg = D/2/f
spot = np.where(NAg < NAL, 2*lam/(np.pi*NAg), 1.22*lam/NAL)
fig, ax = plt.subplots(figsize=(6.2, 3.3))
ax.axvspan(2*NAL*f/1000, 6, color=ORANGE, alpha=0.08)
ax.plot(D/1000, spot, color=BLUE, lw=2.2)
ax.plot(D[NAg < NAL]/1000, 2*lam/(np.pi*NAg[NAg < NAL]), color=BLUE, lw=0)
ax.axhline(1.22*lam/NAL, color=ORANGE, ls="--", lw=1.2)
ax.plot([D0/1000], [2*lam/(np.pi*NAw0)], "o", color=RED, ms=7, zorder=5)
ax.annotate(f"default: D = 2 mm\n$d_\\mathrm{{spot}}$ = {2*lam/(np.pi*NAw0):.2f} µm", (2, 2*lam/(np.pi*NAw0)), (2.45, 3.2),
            arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=10)
ax.text(2*NAL*f/1000+0.1, 4.4, "lens overfilled:\nspot fixed by the lens NA", color=ORANGE, fontsize=10, va="top")
ax.text(0.35, 4.6, "underfilled: wider beam\n= smaller spot", color=BLUE, fontsize=10, va="top")
ax.text(5.9, 1.22*lam/NAL+0.12, "Airy limit 1.22 λ / NA$_L$", color=ORANGE, fontsize=9.5, ha="right")
ax.set_xlim(0.2, 6); ax.set_ylim(0, 5)
ax.set_xlabel("laser beam diameter $D$  (mm)"); ax.set_ylabel("focal spot diameter  (µm)")
fig.savefig("fig_spot_vs_D.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Fig 2.3: Gaussian beam near the focus
dz = np.linspace(-14, 14, 801)
w = w00*np.sqrt(1+(dz/zR0)**2)
fig, ax = plt.subplots(figsize=(6.6, 3.4))
ax.fill_between(dz, -w, w, color=GREEN, alpha=0.18, lw=0)
ax.plot(dz, w, color=GREEN, lw=2); ax.plot(dz, -w, color=GREEN, lw=2)
for x0 in (-10, -6, -2.5, 0, 2.5, 6, 10):     # wavefronts: arcs with radius R(Δ)
    yy = np.linspace(-w00*np.sqrt(1+(x0/zR0)**2), w00*np.sqrt(1+(x0/zR0)**2), 50)
    if x0 == 0: xx = np.zeros_like(yy)
    else:
        R = x0*(1+(zR0/x0)**2); xx = x0 + yy**2/(2*R)*1.0
    ax.plot(xx, yy, color=GREEN, lw=0.8, alpha=0.7)
ax.axvspan(-zR0, zR0, color=BLUE, alpha=0.07)
ax.annotate("", (-zR0, -3.1), (zR0, -3.1), arrowprops=dict(arrowstyle="<->", color=BLUE))
ax.text(0, -3.55, f"$2z_R$ = {2*zR0:.1f} µm", color=BLUE, ha="center", fontsize=10)
ax.annotate("", (0, -w00), (0, w00), arrowprops=dict(arrowstyle="<->", color="k", lw=0.9))
ax.annotate(f"$2w_0$ = {2*w00:.2f} µm", (-0.1, 0.3), (-8.5, 1.6), fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.8))
# pinhole drawn at Δ = 0 and at Δ = +6 µm
for x0, col, lab in ((0, "#333", "pinhole in focus"), (6, RED, "pinhole 6 µm behind focus")):
    ax.plot([x0, x0], [d0/2, 3.4], color=col, lw=3.5, solid_capstyle="butt")
    ax.plot([x0, x0], [-3.0 if x0 else -2.6, -d0/2], color=col, lw=3.5, solid_capstyle="butt")
wd = w00*np.sqrt(1+(6/zR0)**2)
ax.text(6.4, 2.7, f"beam Ø here {2*wd:.1f} µm\n≫ pinhole 1 µm", color=RED, fontsize=10)
ax.set_xlabel("distance from the focus  Δ = s − f  (µm)"); ax.set_ylabel("radius  (µm)")
ax.set_ylim(-3.9, 3.6); ax.set_xlim(-14, 14)
ax.set_title("Focused beam (D = 2 mm, f = 4 mm, λ = 532 nm): waist, Rayleigh range, curved wavefronts", fontsize=10.5)
fig.savefig("fig_gauss_focus.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Fig 3.1: three regimes, beam profile vs pinhole
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6), sharey=True)
r = np.linspace(-3, 3, 1201)
I = np.exp(-2*r**2/w00**2)
for ax, d, name, col in zip(axs, (0.4, 1.0, 4.0), ("point source", "clipped beam", "focused spot"), (PURPLE, RED, GREEN)):
    inside = np.abs(r) <= d/2
    ax.fill_between(r, 0, I, where=inside, color=col, alpha=0.35, lw=0)
    ax.plot(r, I, color="#333", lw=1.4)
    for s_ in (-1, 1):
        ax.add_patch(plt.Rectangle((s_*d/2 if s_ > 0 else -3, 1.05), (3-d/2), 0.12, color="#555"))
    ax.axvline(-d/2, color="#555", lw=0.8, ls=":"); ax.axvline(d/2, color="#555", lw=0.8, ls=":")
    T = 1-np.exp(-2*(d/2)**2/w00**2)
    ax.set_title(f"{name}\nd = {d:g} µm, ratio = {d/(2*w00):.2f}", color=col, fontsize=10.5)
    ax.text(0, -0.24, f"passes {100*T:.0f} %", ha="center", fontsize=10, transform=ax.get_xaxis_transform() if False else ax.transData)
    ax.set_xlim(-3, 3); ax.set_ylim(-0.32, 1.25); ax.set_xlabel("x in pinhole plane (µm)", fontsize=9.5)
    ax.grid(False)
axs[0].set_ylabel("focus intensity")
fig.savefig("fig_regimes.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Fig 3.2: transmission vs pinhole diameter
dd = np.linspace(0.05, 5, 600)
fig, ax = plt.subplots(figsize=(6.2, 3.3))
for Dl, col in ((0, BLUE), (3, GREEN), (6, ORANGE)):
    wg = w00*np.sqrt(1+(Dl/zR0)**2)
    ax.plot(dd, 100*(1-np.exp(-2*(dd/2)**2/wg**2)), color=col, lw=2, label=f"Δ = {Dl} µm (beam Ø {2*wg:.1f} µm)")
ax.plot([1.0], [100*(1-np.exp(-2*0.25/w00**2))], "o", color=RED, ms=7, zorder=5)
ax.annotate("default 1 µm: 66 %", (1.0, 66), (1.35, 40), arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=10)
ax.plot([1.5*2*w00], [98.9], "s", color="k", ms=6, zorder=5)
ax.annotate("rule d ≈ 1.5 $d_\\mathrm{spot}$ = 2 µm: 99 %", (2.03, 98.9), (2.35, 80), arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.set_xlabel("pinhole diameter $d$  (µm)"); ax.set_ylabel("power through pinhole  (%)")
ax.set_ylim(0, 105); ax.set_xlim(0, 5); ax.legend(loc="lower right", frameon=False)
fig.savefig("fig_Tpin.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Fig 3.3: cone half-angle vs pinhole diameter
dd = np.linspace(0.45, 8, 700)
thA = np.degrees(np.arcsin(np.clip(1.22*lam/dd, 0, 1))); thB = np.degrees(np.arcsin(NAw0))
ratio = dd/(2*w00)
th = np.where(ratio < 0.5, thA, np.where(ratio > 2, thB, np.maximum(thA, thB)))
fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.axvspan(0.45, 0.5*2*w00, color=PURPLE, alpha=0.08); ax.axvspan(0.5*2*w00, 2*2*w00, color=RED, alpha=0.07); ax.axvspan(2*2*w00, 8, color=GREEN, alpha=0.07)
ax.plot(dd, thA, color=PURPLE, ls="--", lw=1.2, label="Airy: arcsin(1.22 λ/d)")
ax.axhline(thB, color=GREEN, ls="--", lw=1.2, label="focus: arcsin NA$_w$")
ax.plot(dd, th, color="k", lw=2.2, label="angle used by the simulator")
ax.plot([1], [np.degrees(np.arcsin(1.22*lam))], "o", color=RED, ms=7, zorder=5)
ax.text(1.12, 43, "default: 40.5°", color=RED, fontsize=10)
for x, t, c in ((0.48, "point\nsource", PURPLE), (1.6, "clipped", RED), (4.6, "focused spot", GREEN)):
    ax.text(x, 76, t, color=c, fontsize=10, va="top")
ax.set_xlim(0.45, 8); ax.set_ylim(0, 80)
ax.set_xlabel("pinhole diameter $d$  (µm)"); ax.set_ylabel("cone half-angle θ  (°)"); ax.legend(loc="center right", frameon=False)
fig.savefig("fig_cone.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Chapter 4: Hankel integral (Eq. hankel), Δ = 0
def A_of_rho(rho, d, wg=w00, z=z1, Rinv=0.0):
    a = min(d/2, 4*wg); n = 4000
    rr = (np.arange(n)+0.5)*a/n; dr = a/n
    g = np.exp(-rr**2/wg**2)*np.exp(1j*np.pi*rr**2/lam*(1/z+Rinv))*rr*dr
    return (j0(2*np.pi*np.outer(rho, rr)) @ g)
thdeg = np.linspace(0, 80, 1600); rho = np.sin(np.radians(thdeg))/lam
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.2))
for d, col, lab in ((0.4, PURPLE, "d = 0.4 µm (point source)"), (1.0, RED, "d = 1 µm (clipped, default)"), (4.0, GREEN, "d = 4 µm (focused spot)")):
    A = A_of_rho(rho, d); I = np.abs(A)**2; I /= I[0]
    axs[0].plot(thdeg, I, color=col, lw=2, label=lab); axs[1].semilogy(thdeg, I+1e-9, color=col, lw=1.6)
u = np.pi*1.0*np.sin(np.radians(thdeg))/lam; airy = (2*j1(u)/np.where(u == 0, 1, u))**2; airy[0] = 1
axs[1].semilogy(thdeg, airy+1e-9, color="k", ls=":", lw=1.2, label="pure Airy, d = 1 µm")
axs[1].semilogy(thdeg, np.exp(-2*(np.sin(np.radians(thdeg))/NAw0)**2)+1e-9, color=GREY, ls="--", lw=1.2, label="Gaussian cone of the focus")
axs[0].set_xlabel("angle from the axis θ (°)"); axs[0].set_ylabel("$|A|^2$ (normalised)"); axs[0].set_xlim(0, 80); axs[0].legend(frameon=False, fontsize=9)
axs[1].set_xlabel("angle from the axis θ (°)"); axs[1].set_ylim(1e-5, 1.5); axs[1].set_xlim(0, 80); axs[1].legend(frameon=False, fontsize=8.6, loc="lower left")
axs[0].set_title("linear scale"); axs[1].set_title("log scale: rings and tails")
fig.tight_layout(); fig.savefig("fig_hankel_profiles.pdf"); plt.close(fig)

# 2-D illumination on the sample plane (z1 = 0.5 mm), three pinholes
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.75))
X = np.linspace(-1100, 1100, 361); XX, YY = np.meshgrid(X, X); RS = np.hypot(XX, YY)
for ax, d, col, name in zip(axs, (0.4, 1.0, 4.0), (PURPLE, RED, GREEN), ("point source", "clipped (default)", "focused spot")):
    rs1 = np.linspace(0, RS.max(), 1500); A1 = A_of_rho(rs1/np.hypot(rs1, z1)/lam, d); I1 = np.abs(A1)**2; I1 /= I1.max()
    img = np.interp(RS, rs1, I1)
    ax.imshow(img**0.5, extent=[X[0]/1000, X[-1]/1000, X[0]/1000, X[-1]/1000], cmap="magma", origin="lower", vmin=0, vmax=1)
    ax.set_title(f"{name}, d = {d:g} µm", fontsize=10, color=col); ax.grid(False)
    ax.set_xlabel("x on sample (mm)", fontsize=9.5)
    half = 141/2/1000
    ax.add_patch(plt.Rectangle((-half, -half), 2*half, 2*half, fill=False, ec="cyan", lw=1.0))
axs[0].set_ylabel("y (mm)", fontsize=9.5)
axs[2].annotate("simulated field of view\n(141 µm)", (0.08, 0.08), (0.25, 0.75), color="cyan", fontsize=8.5, arrowprops=dict(arrowstyle="->", color="cyan"))
fig.tight_layout(); fig.savefig("fig_illum_2d.pdf"); plt.close(fig)

# Defocused pinhole: curvature term changes the pattern (d = 1 µm, Δ = 0, 3, 6 µm)
fig, ax = plt.subplots(figsize=(6.2, 3.1))
for Dl, col in ((0, RED), (3, ORANGE), (6, BLUE)):
    wg = w00*np.sqrt(1+(Dl/zR0)**2); Rinv = 0 if Dl == 0 else 1/(Dl*(1+(zR0/Dl)**2))
    # same laser power: scale the field by the beam amplitude at the pinhole (1/wg)
    A = A_of_rho(rho, 1.0, wg=wg, Rinv=Rinv)*(w00/wg); I = np.abs(A)**2
    if Dl == 0: I0 = I[0]
    T = 1-np.exp(-2*0.25/wg**2)
    ax.plot(thdeg, I/I0, color=col, lw=2, label=f"Δ = {Dl} µm: beam Ø {2*wg:.1f} µm, {100*T:.0f} % passes")
ax.set_xlabel("angle from the axis θ (°)"); ax.set_ylabel("$|A|^2$ (same laser power)")
ax.set_xlim(0, 80); ax.legend(frameon=False); ax.set_title("1 µm pinhole moved out of the focus: same cone shape, much less light", fontsize=10.5)
fig.savefig("fig_defocus.pdf"); plt.close(fig)
print("ok", w00, zR0)
