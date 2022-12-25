#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import scipy.constants as constants
from scipy.integrate import solve_ivp
from pprint import pp


def generate_icosphere(radius: float = 1, scale_factor: int = 1):
    polar_divisions = 3 * scale_factor
    azimuth_divisions = 5 * scale_factor

    azimuth_angle = 2 * constants.pi / azimuth_divisions

    ps = np.linspace(0, constants.pi, polar_divisions + 1, endpoint=True)

    xs = np.array([])
    ys = np.array([])
    zs = np.array([])
    for pi, p in enumerate(ps):
        if 0 < p < constants.pi:
            # Limit azimuth divisions around the poles to maintain equilateral
            # triangles
            limited_azimuth_divisions = np.min(
                (5 * pi, azimuth_divisions, 5 * (polar_divisions - pi))
            )

            az = np.linspace(
                0, 2 * constants.pi, limited_azimuth_divisions + 1, endpoint=True
            )

            # Offset to create staggered triangle strips
            of = pi * (azimuth_angle / 2)

            xs = np.concatenate((radius * np.sin(p) * np.cos(az - of), xs))
            ys = np.concatenate((radius * np.sin(p) * np.sin(az - of), ys))
            zs = np.concatenate((radius * np.cos(p) * np.ones_like(az), zs))
        else:
            # Endpoints have only a singular point
            xs = np.concatenate(([0], xs))
            ys = np.concatenate(([0], ys))
            zs = np.concatenate(([radius * np.cos(p)], zs))

    return xs, ys, zs


xs, ys, zs = generate_icosphere(1, 3)

fig, axs = plt.subplots(1, 1, subplot_kw={"projection": "3d"}, squeeze=False)

axs[0][0].scatter(xs, ys, zs)
#axs[0][0].plot_trisurf(xs, ys, zs)

plt.show()

exit(0)


t_0 = 0  # seconds
t_f = 10  # seconds
t_points = np.linspace(t_0, t_f, 10)

fig, axs = plt.subplots(1, 1, subplot_kw={"projection": "3d"}, squeeze=False)

dynamicss = [
    {
        "satelite": ax.plot([], [], [], "bo", markersize=6, label="satelite")[0],
    }
    for ax in axs.flat
]
staticss = [
    {
        "planet": ax.plot_trisurf([0, 1, 0], [0, 0, 1], [0, 0, 0], label="planet"),
    }
    for ax in axs.flat
]

faces = generate_icosphere()
print(np.shape(faces))


def init():
    for ax, dynamics, statics in zip(axs.flat, dynamicss, staticss):

        planet_ln = statics["planet"]

        # r = 10
        # resolution = 20
        # azimuths = np.linspace(0, 2 * constants.pi, resolution + 1, endpoint=True)
        # polars = np.linspace(0, constants.pi, resolution + 1, endpoint=True)

        # xs = r * np.outer(np.sin(polars), np.cos(azimuths))
        # ys = r * np.outer(np.sin(polars), np.sin(azimuths))
        # zs = r * np.outer(np.cos(polars), np.ones_like(azimuths))

        planet_ln.set_verts(faces)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)
        # planet_ln.set_3d_properties(zs)

    return [dynamic for dynamics in dynamicss for dynamic in dynamics.values()]


def animate(i):
    for dynamics in dynamicss:
        pass
        # lns[2].set_data(barycenter_[:2])
        # lns[2].set_3d_properties(barycenter_[2])

    return [dynamic for dynamics in dynamicss for dynamic in dynamics.values()]


ani = FuncAnimation(
    fig,
    animate,
    init_func=init,
    frames=len(t_points),
    interval=100,
    # repeat=True,
    blit=True,
)

plt.show()
