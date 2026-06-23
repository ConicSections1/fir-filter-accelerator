#!/usr/bin/env python3
"""Generate portfolio images for the FIR filter project.

This script creates three reproducible documentation assets from the existing
simulation artifacts:
- a noisy-input vs filtered-output plot
- a waveform-style capture of the FIR signals
- a block diagram of the pipelined datapath
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIM = ROOT / "sim"


def load_samples(name: str) -> np.ndarray:
    return np.loadtxt(SIM / name, dtype=np.int32)


def save_signal_plot(input_samples: np.ndarray, output_samples: np.ndarray) -> None:
    idx = np.arange(len(input_samples))
    fig, ax = plt.subplots(figsize=(12, 5), dpi=180)
    ax.plot(idx, input_samples, linewidth=1.0, color="#8a4b08", alpha=0.72, label="Noisy input")
    ax.plot(idx, output_samples, linewidth=1.8, color="#0b6e4f", label="FIR output")
    ax.set_title("4-Tap FIR Filter: Noisy Input vs Clean Output")
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Amplitude (signed 16-bit)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(ASSETS / "fir_signal_plot.png", bbox_inches="tight")
    plt.close(fig)


def save_waveform_capture(input_samples: np.ndarray, output_samples: np.ndarray) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 7), dpi=180, sharex=True)
    plot_len = min(160, len(input_samples))
    t = np.arange(plot_len)
    valid_in = np.ones(plot_len, dtype=int)
    valid_out = np.zeros(plot_len, dtype=int)
    latency = 4
    valid_out[max(0, latency):plot_len] = 1

    axes[0].step(t, valid_in, where="post", color="#1f77b4", linewidth=1.5)
    axes[0].set_ylabel("valid_in")
    axes[0].set_ylim(-0.2, 1.4)
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(t, input_samples[:plot_len], color="#8a4b08", linewidth=1.1)
    axes[1].set_ylabel("data_in")
    axes[1].grid(True, alpha=0.25)

    axes[2].step(t, valid_out, where="post", color="#2ca02c", linewidth=1.5)
    axes[2].plot(t[:plot_len - latency], output_samples[:plot_len - latency], color="#0b6e4f", linewidth=1.1)
    axes[2].set_ylabel("data_out / valid_out")
    axes[2].set_xlabel("Sample index")
    axes[2].grid(True, alpha=0.25)

    fig.suptitle("Simulation Capture: FIR Data Path and Valid Transitions", y=0.98)
    fig.tight_layout()
    fig.savefig(ASSETS / "fir_waveform_capture.png", bbox_inches="tight")
    plt.close(fig)


def save_block_diagram() -> None:
    fig, ax = plt.subplots(figsize=(14, 5), dpi=180)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")

    boxes = [
        (0.6, 2.2, 1.3, 1.1, "data_in\nvalid_in"),
        (2.4, 2.2, 1.3, 1.1, "DFF\nTap 0"),
        (4.2, 2.2, 1.3, 1.1, "DFF\nTap 1"),
        (6.0, 2.2, 1.3, 1.1, "DFF\nTap 2"),
        (7.8, 2.2, 1.3, 1.1, "Current\nSample"),
        (3.0, 4.2, 1.6, 1.0, "x0 * c0"),
        (4.9, 4.2, 1.6, 1.0, "x1 * c1"),
        (6.8, 4.2, 1.6, 1.0, "x2 * c2"),
        (8.7, 4.2, 1.6, 1.0, "x3 * c3"),
        (5.2, 1.0, 2.1, 1.0, "Pipeline adder tree\nwith saturation"),
        (9.6, 2.2, 1.6, 1.1, "data_out\nvalid_out"),
    ]
    for x, y, w, h, label in boxes:
        rect = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1.3, edgecolor="#1f2937", facecolor="#f3f4f6"
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10)

    arrows = [
        ((1.9, 2.75), (2.4, 2.75)),
        ((3.7, 2.75), (4.2, 2.75)),
        ((5.5, 2.75), (6.0, 2.75)),
        ((7.3, 2.75), (7.8, 2.75)),
        ((8.6, 2.75), (9.6, 2.75)),
        ((4.05, 3.2), (3.8, 4.2)),
        ((5.65, 3.2), (5.7, 4.2)),
        ((7.45, 3.2), (7.6, 4.2)),
        ((9.1, 3.2), (9.5, 4.2)),
        ((4.6, 4.7), (5.2, 4.7)),
        ((6.5, 4.7), (6.8, 4.7)),
        ((8.4, 4.7), (8.7, 4.7)),
        ((6.25, 2.0), (6.25, 1.0)),
        ((7.3, 1.5), (9.6, 1.5)),
    ]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12,
                                     linewidth=1.2, color="#2563eb"))

    ax.text(6.9, 5.55, "4-Tap Pipelined FIR Datapath", ha="center", va="center", fontsize=15, weight="bold")
    ax.text(
        6.9,
        0.35,
        "Multiplier outputs and adder stages are registered; final sum is saturated to signed 16-bit output.",
        ha="center",
        va="center",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / "fir_block_diagram.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    input_samples = load_samples("fir_input.txt")
    output_samples = load_samples("fir_output.txt")

    save_signal_plot(input_samples, output_samples)
    save_waveform_capture(input_samples, output_samples)
    save_block_diagram()

    print("Generated:")
    print("- assets/fir_signal_plot.png")
    print("- assets/fir_waveform_capture.png")
    print("- assets/fir_block_diagram.png")


if __name__ == "__main__":
    main()