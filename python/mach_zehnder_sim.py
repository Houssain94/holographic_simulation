"""
Mach-Zehnder interferometer simulator
=====================================

Top-view layout (table plane x-z, vertical axis y out of the table):

                 M1 -------------> BS2 ---> I3 (near) ----> camera ----> I4 (far)
                 ^                  ^
        Arm A    |                  |   Arm B
                 |                  |
   laser ---->  BS1 -------------> M2

Model
-----
* Geometric ray tracing of the beam centre through the real 2-D layout
  (horizontal plane), with each element tilted by its own horizontal angle.
* Vertical direction handled with a linear (paraxial) model: every
  reflection adds 2*tau to the vertical beam angle, where tau is the
  element's vertical tilt. Transmission through a beamsplitter does not
  change direction (plate thickness / lateral shift ignored).
* Each arm is then represented at the camera plane as a Gaussian beam
  with its own centre, tilt, optical path length and wavefront curvature.
  The intensity is |E_A + E_B|^2.

All lengths in mm, angles in rad.  Run:  python mach_zehnder_sim.py
Requires: numpy, matplotlib
"""
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- parameters
LAMBDA = 632.8e-6          # He-Ne wavelength [mm]
K = 2 * np.pi / LAMBDA
W0 = 2.5                   # beam radius at the camera [mm] (1/e field), e.g. after a beam expander
ARM = 300.0                # side of the square interferometer [mm]
Z_I3 = 50.0                # near iris: distance after BS2 [mm]
Z_CAM = 300.0              # camera: distance after BS2 [mm]
Z_I4 = 1000.0              # far iris: distance after BS2 [mm]

# element centres and nominal orientation ("/" = 45 deg); normals point up-left
ELEMENTS = {
    "BS1": np.array([0.0, 0.0]),
    "M1":  np.array([0.0, ARM]),
    "M2":  np.array([ARM, 0.0]),
    "BS2": np.array([ARM, ARM]),
}
N0 = np.array([-1.0, 1.0]) / np.sqrt(2)   # nominal normal of every "/" element


def rot(v, a):
    c, s = np.cos(a), np.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def default_state():
    """All tilts in rad: h = horizontal (in table plane), v = vertical."""
    return {
        "input": {"dz": 0.0, "dy": 0.0, "ah": 0.0, "av": 0.0},   # input beam error
        "BS1": {"h": 0.0, "v": 0.0},
        "M1": {"h": 0.0, "v": 0.0},
        "M2": {"h": 0.0, "v": 0.0},
        "BS2": {"h": 0.0, "v": 0.0},
        "extra_path_B": 0.0,    # extra optical path in arm B (delay line / piezo) [mm]
        "R_in": np.inf,         # wavefront radius of the input beam at BS1 [mm] (inf = collimated)
    }


# ---------------------------------------------------------------- ray tracing
def _hit(p, d, name, st):
    """Intersect ray p + t d with the plane (line) of element `name`."""
    c = ELEMENTS[name]
    n = rot(N0, st[name]["h"])
    t = np.dot(c - p, n) / np.dot(d, n)
    return p + t * d, t, n


def trace(st, arm, z_after_bs2):
    """
    Trace the beam centre of arm 'A' or 'B' to a plane z_after_bs2 behind BS2.
    Returns dict with horizontal pos h, vertical pos y, angles (ah, av),
    and geometric path length L.
    """
    inp = st["input"]
    p = np.array([-200.0, inp["dz"]])
    d = rot(np.array([1.0, 0.0]), inp["ah"])
    y, av = inp["dy"], inp["av"]
    L = 0.0
    seq = [("BS1", "R"), ("M1", "R"), ("BS2", "T")] if arm == "A" else \
          [("BS1", "T"), ("M2", "R"), ("BS2", "R")]
    for name, action in seq:
        p, t, n = _hit(p, d, name, st)
        L += t
        y += av * t
        if action == "R":
            d = d - 2 * np.dot(d, n) * n
            av += 2 * st[name]["v"]
    # propagate to the observation plane x = ARM + z_after_bs2
    t = (ARM + z_after_bs2 - p[0]) / d[0]
    p = p + t * d
    L += t
    y += av * t
    # looking downstream (+x) with y up, +z is on the LEFT -> horizontal coordinate = -(z - ARM)
    h = -(p[1] - ARM)
    ah = -np.arctan2(d[1], d[0])
    return {"h": h, "y": y, "ah": ah, "av": av, "L": L}


# ---------------------------------------------------------------- interference
def field(beam, X, Y, R):
    dx, dy = X - beam["h"], Y - beam["y"]
    amp = np.exp(-(dx**2 + dy**2) / W0**2)
    phase = K * (beam["L"] + beam["ah"] * dx + beam["av"] * dy)
    if np.isfinite(R):
        phase = phase + K * (dx**2 + dy**2) / (2 * R)
    return amp * np.exp(1j * phase)


def camera_image(st, half=6.0, n=400, block=None):
    x = np.linspace(-half, half, n)
    X, Y = np.meshgrid(x, x[::-1])
    A = trace(st, "A", Z_CAM)
    B = trace(st, "B", Z_CAM)
    B = dict(B, L=B["L"] + st["extra_path_B"])
    RA = st["R_in"] + A["L"] if np.isfinite(st["R_in"]) else np.inf
    RB = st["R_in"] + B["L"] if np.isfinite(st["R_in"]) else np.inf
    E = 0
    if block != "A":
        E = E + field(A, X, Y, RA) / np.sqrt(2)
    if block != "B":
        E = E + field(B, X, Y, RB) / np.sqrt(2)
    return np.abs(E) ** 2, (A, B)


def iris_spots(st):
    return {name: (trace(st, "A", z), trace(st, "B", z)) for name, z in [("I3", Z_I3), ("I4", Z_I4)]}


# ---------------------------------------------------------------- demos
def demo_cases():
    cases = []
    s = default_state(); cases.append(("Perfectly aligned\n(one wide fringe)", s))
    s = default_state(); s["BS2"]["h"] = 0.25e-3; cases.append(("BS2 tilted 0.25 mrad\n(vertical fringes)", s))
    s = default_state(); s["M1"]["v"] = 0.25e-3; cases.append(("M1 tilted 0.25 mrad vertically\n(horizontal fringes)", s))
    s = default_state(); s["M2"]["h"] = 1.0e-3; s["BS2"]["h"] = 1.0e-3
    cases.append(("M2 and BS2 both tilted 1 mrad:\nbeams parallel but offset → wide\nfringe, reduced overlap", s))
    s = default_state(); s["R_in"] = 200.0; s["extra_path_B"] = 200.0
    cases.append(("Diverging input (R = 0.2 m) +\n200 mm path mismatch → rings", s))
    s = default_state(); s["extra_path_B"] = LAMBDA / 2
    cases.append(("Aligned, path shifted by λ/2\n(this port goes dark)", s))
    fig, axs = plt.subplots(2, 3, figsize=(12, 8.8))
    for ax, (title, st) in zip(axs.flat, cases):
        img, (A, B) = camera_image(st)
        ax.imshow(img, cmap="inferno", extent=[-6, 6, -6, 6], vmin=0, vmax=2)
        theta = np.hypot(A["ah"] - B["ah"], A["av"] - B["av"])
        sub = f"θ = {theta*1e3:.2f} mrad" + (f",  Λ = λ/θ = {LAMBDA/theta:.2f} mm" if theta > 1e-9 else "")
        ax.set_title(title + "\n" + sub, fontsize=9)
        ax.set_xlabel("x [mm]"); ax.set_ylabel("y [mm]")
    fig.suptitle("Mach–Zehnder: camera image for different misalignments (He–Ne, 632.8 nm)", fontsize=12)
    fig.tight_layout(h_pad=3.0)
    fig.savefig("mz_fringe_cases.png", dpi=150)
    return fig


def demo_alignment_procedure():
    """Reproduce the iris procedure numerically: start misaligned, then apply the rule
    'earlier element -> near iris, last element -> far iris' iteratively.

    Result worth noticing: Arm B converges fast because its last element (BS2) sits right
    next to I3, so tilting BS2 hardly disturbs the near spot. Arm A converges more slowly
    because M1 is ~350 mm before I3, so M1 and BS1 both move the I3 spot. In the lab this
    means Arm A needs more back-and-forth passes; putting I3 as close to BS2 as possible
    and I4 as far away as possible helps."""
    rng = np.random.default_rng(1)
    st = default_state()
    for e in ["BS1", "M1", "M2", "BS2"]:
        st[e]["h"] = rng.uniform(-1e-3, 1e-3)
        st[e]["v"] = rng.uniform(-1e-3, 1e-3)

    def centre(arm, near_el, far_el):
        # 1-D Newton-style correction using numerical derivatives (what your hand does on the knob)
        for key, coord in [("h", "h"), ("v", "y")]:
            for el, z in [(near_el, Z_I3), (far_el, Z_I4)]:
                f0 = trace(st, arm, z)[coord]
                st[el][key] += 1e-6
                f1 = trace(st, arm, z)[coord]
                st[el][key] -= 1e-6
                st[el][key] -= f0 / ((f1 - f0) / 1e-6)

    history = []
    for it in range(6):
        sp = iris_spots(st)
        history.append([np.hypot(sp[i][a]["h"], sp[i][a]["y"]) for i in ("I3", "I4") for a in (0, 1)])
        centre("A", "BS1", "M1")    # Arm A: BS1 -> I3, M1 -> I4
        centre("B", "M2", "BS2")    # Arm B: M2 -> I3, BS2 -> I4
    history = np.array(history)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    labels = ["Arm A on I3", "Arm B on I3", "Arm A on I4", "Arm B on I4"]
    for k in range(4):
        ax.semilogy(np.maximum(history[:, k], 1e-9), "o-", label=labels[k])
    ax.axhline(1.0, color="grey", ls="--", lw=1); ax.text(0.1, 1.15, "iris hole radius (1 mm)", fontsize=8, color="grey")
    ax.set_xlabel("iteration (one pass = both arms)"); ax.set_ylabel("spot distance from iris centre [mm]")
    ax.set_title("Iris procedure: spot error vs. number of passes"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig("mz_alignment_convergence.png", dpi=150)
    print("Alignment passes (distances in mm, columns: A@I3, B@I3, A@I4, B@I4):")
    for i, row in enumerate(history):
        print(f"  pass {i}: " + "  ".join(f"{v:9.2e}" for v in row))
    return fig


def demo_phase_scan():
    """Output power of both ports vs extra path in arm B: complementary cosine fringes."""
    st = default_state()
    dL = np.linspace(0, 3 * LAMBDA, 300)
    p1 = []
    for d in dL:
        st["extra_path_B"] = d
        img, _ = camera_image(st, n=60)
        p1.append(img.sum())
    p1 = np.array(p1) / max(p1)
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(dL * 1e6, p1, label="port 1 (camera)")
    ax.plot(dL * 1e6, 1 - p1, label="port 2 (other BS2 output)")
    ax.set_xlabel("extra path in arm B [nm]"); ax.set_ylabel("normalised power")
    ax.set_title("Moving one mirror by λ/2 changes the path by λ → one full fringe")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig("mz_phase_scan.png", dpi=150)
    return fig


def check_fringe_spacing():
    """Numerical check: measured fringe period equals λ/θ."""
    st = default_state(); st["BS2"]["h"] = 0.25e-3
    img, (A, B) = camera_image(st, half=6, n=2048)
    iA, _ = camera_image(st, half=6, n=2048, block="B")
    iB, _ = camera_image(st, half=6, n=2048, block="A")
    cross = img - iA - iB                      # interference term only (removes the Gaussian envelope)
    row = cross[cross.shape[0] // 2]
    x = np.linspace(-6, 6, 2048)
    npad = 32 * len(row)                       # zero-padding for fine frequency resolution
    spec = np.abs(np.fft.rfft(row, n=npad))
    freqs = np.fft.rfftfreq(npad, d=x[1] - x[0])
    f = freqs[np.argmax(spec[1:]) + 1]
    theta = abs(A["ah"] - B["ah"])
    print(f"beam angle θ = {theta*1e3:.3f} mrad  (expected 2 × 0.25 = 0.500 mrad)")
    print(f"fringe period: FFT = {1/f:.3f} mm,  λ/θ = {LAMBDA/theta:.3f} mm")


if __name__ == "__main__":
    check_fringe_spacing()
    demo_cases()
    demo_alignment_procedure()
    demo_phase_scan()
    print("Saved: mz_fringe_cases.png, mz_alignment_convergence.png, mz_phase_scan.png")
    plt.show()
