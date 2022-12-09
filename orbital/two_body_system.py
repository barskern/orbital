#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp

G = 6.67430e-20  # km**3/(kg * s**2)
m_1 = 1.0e26  # kg
m_2 = 1.0e26  # kg

R_1_0 = np.array([0, 0, 0])
R_2_0 = np.array([3000, 0, 0])
dotR_1_0 = np.array([10, 20, 30])
dotR_2_0 = np.array([0, 40, 0])


def plot_state(ax, Y, arrow_scale=5):
    R_1, R_2, dotR_1, dotR_2 = Y[:3], Y[3:6], Y[6:9], Y[9:12]
    r = R_2 - R_1

    ax.plot(*R_1[1:], "bo", label="m_1")
    # ax.annotate("1", R_1[1:], textcoords='offset pixels', xytext=(10, 10))
    ax.plot(*R_2[1:], "ro", label="m_2")
    # ax.annotate("2", R_2[1:], textcoords='offset pixels', xytext=(10, 10))

    if np.linalg.norm(dotR_1) > 0:
        ax.arrow(*R_1[1:], *dotR_1[1:] * arrow_scale, width=20)

    if np.linalg.norm(dotR_2_0) > 0:
        ax.arrow(*R_2[1:], *dotR_2[1:] * arrow_scale, width=20)

    bounding_box = np.array([-4000, 4000])
    xlim = bounding_box + (r[1] / 2)
    ylim = bounding_box + (r[2] / 2)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


Y_0 = np.hstack([R_1_0, R_2_0, dotR_1_0, dotR_2_0])


def two_body_kepler(t, Y):
    R_1, R_2 = Y[:3], Y[3:6]

    Yn = np.zeros_like(Y)

    # Change in positions is equal to velocity
    Yn[:6] = Y[6:]

    # Change in velocity is equal to acceleration
    r = R_2 - R_1

    gp = r * G / np.linalg.norm(r) ** 3
    a_1 = m_2 * gp
    a_2 = -m_1 * gp

    Yn[6:9] = a_1
    Yn[9:12] = a_2

    return Yn


t_0 = 0  # seconds
t_f = 480  # seconds
t_points = np.linspace(t_0, t_f, 1000)

sol = solve_ivp(two_body_kepler, [t_0, t_f], Y_0, t_eval=t_points)

y = sol.y.T
R_1 = y[:, :3]  # km
R_2 = y[:, 3:6]  # km
V_1 = y[:, 6:9]  # km/s
V_2 = y[:, 9:]  # km/s
barycenter = (m_1 * R_1 + m_2 * R_2) / (m_1 + m_2)  # km

fig, axs = plt.subplots(2, 2, subplot_kw={"projection": "3d"})

lnss = [
    (
        ax.plot([], [], [], "bo", markersize=6, label="m_1")[0],
        ax.plot([], [], [], "ro", markersize=6, label="m_2")[0],
        ax.plot([], [], [], "ko", markersize=3, label="COG")[0],
    )
    for ax in axs.flat
]
trailss = [
    (
        ax.plot([], [], [], "b", label="m_1")[0],
        ax.plot([], [], [], "r", label="m_2")[0],
        ax.plot([], [], [], "k", label="COG")[0],
    )
    for ax in axs.flat
]

refs = [("none", np.zeros_like(R_1)), ("COG", barycenter), ("R1", R_1), ("R2", R_2)]


def init():
    for (ref_name, reference), ax, lns, trails in zip(refs, axs.flat, lnss, trailss):
        R_1_ = R_1 - reference
        R_2_ = R_2 - reference
        barycenter_ = barycenter - reference

        trails[0].set_data(R_1_[:, :2].T)
        trails[0].set_3d_properties(R_1_[:, 2:].T)

        trails[1].set_data(R_2_[:, :2].T)
        trails[1].set_3d_properties(R_2_[:, 2:].T)

        trails[2].set_data(barycenter_[:, :2].T)
        trails[2].set_3d_properties(barycenter_[:, 2:].T)

        margin = np.array([10, 10, 10])
        min_ = np.min(np.concatenate([R_1_, R_2_, barycenter_]), axis=0) - margin
        max_ = np.max(np.concatenate([R_1_, R_2_, barycenter_]), axis=0) + margin

        ax.set_xlim(min_[0], max_[0])
        ax.set_ylim(min_[1], max_[1])
        ax.set_zlim(min_[2], max_[2])
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        ax.set_title(f"Reference {ref_name}")


def animate(i):
    for (ref_name, reference), ax, lns in zip(refs, axs.flat, lnss):
        reference_ = reference[i : i + 1].T

        R_1_ = R_1[i : i + 1].T - reference_
        lns[0].set_data(R_1_[:2])
        lns[0].set_3d_properties(R_1_[2])

        R_2_ = R_2[i : i + 1].T - reference_
        lns[1].set_data(R_2_[:2])
        lns[1].set_3d_properties(R_2_[2])

        barycenter_ = barycenter[i : i + 1].T - reference_
        lns[2].set_data(barycenter_[:2])
        lns[2].set_3d_properties(barycenter_[2])


ani = FuncAnimation(
    fig, animate, init_func=init, frames=len(t_points), interval=10, repeat=True
)

plt.show()
