#!/usr/bin/env python3
"""Generate input/output sample files for the 4-tap FIR filter.

The script creates a noisy sine wave, quantizes it to signed 16-bit integers,
applies a 4-tap FIR using fixed-point Q15 coefficients, and exports the raw
integer input and golden-reference output streams as text files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


Q_FORMAT = 15
COEFFICIENTS = np.array([4096, 8192, 8192, 4096], dtype=np.int64)
DEFAULT_SAMPLES = 1024
DEFAULT_SEED = 7


def saturate_int16(values: np.ndarray) -> np.ndarray:
    """Clamp values to the signed 16-bit range."""

    return np.clip(values, -32768, 32767).astype(np.int16)


def generate_noisy_sine(sample_count: int, seed: int) -> np.ndarray:
    """Create a quantized noisy sine wave suitable for fixed-point testing."""

    rng = np.random.default_rng(seed)
    time = np.arange(sample_count, dtype=np.float64)
    sine = 12000.0 * np.sin(2.0 * np.pi * 5.0 * time / sample_count)
    noise = rng.normal(0.0, 1800.0, sample_count)
    samples = np.rint(sine + noise)
    return saturate_int16(samples)


def fir_reference(input_samples: np.ndarray) -> np.ndarray:
    """Compute the Q15 FIR golden reference with saturation."""

    history = np.zeros(len(COEFFICIENTS), dtype=np.int64)
    outputs = np.zeros(len(input_samples), dtype=np.int16)

    for index, sample in enumerate(input_samples.astype(np.int64)):
        history[1:] = history[:-1]
        history[0] = sample

        accumulator = np.int64(0)
        for coeff, tap in zip(COEFFICIENTS, history, strict=True):
            accumulator += coeff * tap

        filtered = accumulator >> Q_FORMAT
        outputs[index] = saturate_int16(np.array([filtered], dtype=np.int64))[0]

    return outputs


def write_samples(path: Path, samples: np.ndarray) -> None:
    """Write one signed integer sample per line."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_handle:
        for value in samples.tolist():
            file_handle.write(f"{int(value)}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate FIR golden reference samples")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES, help="Number of samples to generate")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for the noise source")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "sim" / "fir_input.txt",
        help="Output path for the raw input samples",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "sim" / "fir_output.txt",
        help="Output path for the filtered golden-reference samples",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_samples = generate_noisy_sine(args.samples, args.seed)
    output_samples = fir_reference(input_samples)

    write_samples(args.input_file, input_samples)
    write_samples(args.output_file, output_samples)


if __name__ == "__main__":
    main()