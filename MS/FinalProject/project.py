from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    import simpy
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: simpy\n"
        "Install with: pip install simpy numpy matplotlib pandas\n"
        f"Original error: {exc}"
    )

import matplotlib.pyplot as plt

try:
    import pandas as pd
except ImportError:
    pd = None



# -----------------------------
# Model definitions
# -----------------------------
SUSCEPTIBLE = 0
EXPOSED = 1
INFECTIOUS = 2
RECOVERED = 3

STATE_NAMES = {
    SUSCEPTIBLE: "S",
    EXPOSED: "E",
    INFECTIOUS: "I",
    RECOVERED: "R",
}


@dataclass(frozen=True)
class Scenario:
    name: str
    population: int = 600
    initial_infected: int = 5
    sim_days: int = 160

    # Transmission mechanics
    contacts_per_day: float = 12.0
    target_r0: float = 2.2

    # Intervention: reduce contacts after a given day
    intervention_day: Optional[int] = None
    contact_reduction: float = 0.0  # 0.5 => 50% fewer contacts

    # Disease timing distributions
    incubation_median_days: float = 5.1
    incubation_q975_days: float = 11.5
    infectious_mean_days: float = 7.0
    infectious_sd_days: float = 2.0

    # RNG seed
    seed: int = 42


def _lognormal_mu_sigma_from_median_q(median: float, q: float, q_prob: float) -> Tuple[float, float]:
    """
    For LogNormal: median = exp(mu), quantile q at probability q_prob:
        q = exp(mu + sigma * z_q)
    """
    if median <= 0 or q <= 0:
        raise ValueError("median and q must be > 0 for LogNormal.")
    if not (0.0 < q_prob < 1.0):
        raise ValueError("q_prob must be in (0,1).")

    z = float(np.quantile(np.random.standard_normal(5_000_000), q_prob))  # robust-ish approx
    # The above uses Monte Carlo to avoid pulling in SciPy for norm.ppf.
    # It is heavy once; we could cache, but it's fine for a single run.
    # For q_prob=0.975, z should be close to 1.96.

    mu = math.log(median)
    sigma = (math.log(q) - mu) / z
    if sigma <= 0:
        raise ValueError("Computed sigma <= 0; check median/q inputs.")
    return mu, sigma


def _sample_lognormal_days(rng: random.Random, mu: float, sigma: float) -> float:
    return max(0.0, rng.lognormvariate(mu, sigma))


def _gamma_k_theta_from_mean_sd(mean: float, sd: float) -> Tuple[float, float]:
    if mean <= 0 or sd <= 0:
        raise ValueError("mean and sd must be > 0 for Gamma.")
    k = (mean / sd) ** 2  # shape
    theta = (sd**2) / mean  # scale
    return k, theta


def _sample_gamma_days(rng: random.Random, shape_k: float, scale_theta: float) -> float:
    # random.gammavariate(alpha, beta) where beta is scale
    return max(0.0, rng.gammavariate(shape_k, scale_theta))


def _daily_contact_rate(day: int, scenario: Scenario) -> float:
    if scenario.intervention_day is None:
        return scenario.contacts_per_day
    if day < scenario.intervention_day:
        return scenario.contacts_per_day
    return scenario.contacts_per_day * (1.0 - scenario.contact_reduction)


def _transmission_probability_per_contact(scenario: Scenario) -> float:
    """
    Calibrate p_transmit per contact to match target R0 approximately:
        R0 ≈ contacts_per_day * p_transmit * mean_infectious_duration
    For intervention scenarios, calibration uses pre-intervention contact rate.
    """
    base_contacts = scenario.contacts_per_day
    mean_inf = scenario.infectious_mean_days
    p = scenario.target_r0 / max(1e-9, base_contacts * mean_inf)
    return min(max(p, 0.0), 1.0)


class EpidemicModel:
    def __init__(self, env: simpy.Environment, scenario: Scenario):
        self.env = env
        self.scenario = scenario
        self.rng = random.Random(scenario.seed)

        self.n = scenario.population
        self.state: List[int] = [SUSCEPTIBLE] * self.n

        # Track whether we've started a disease progression process for a person
        self._has_process: List[bool] = [False] * self.n

        self.p_transmit = _transmission_probability_per_contact(scenario)

        mu, sigma = _lognormal_mu_sigma_from_median_q(
            median=scenario.incubation_median_days,
            q=scenario.incubation_q975_days,
            q_prob=0.975,
        )
        self.inc_mu = mu
        self.inc_sigma = sigma

        k, theta = _gamma_k_theta_from_mean_sd(
            mean=scenario.infectious_mean_days,
            sd=scenario.infectious_sd_days,
        )
        self.inf_k = k
        self.inf_theta = theta

        self.history: Dict[str, List[int]] = {"day": [], "S": [], "E": [], "I": [], "R": []}
        self.cumulative_infected: List[int] = []

        self._ever_infected: List[bool] = [False] * self.n

    def seed_initial_infections(self) -> None:
        if self.scenario.initial_infected <= 0:
            return
        initial = self.rng.sample(range(self.n), k=min(self.scenario.initial_infected, self.n))
        for pid in initial:
            self._infect(pid)

    def _infect(self, pid: int) -> None:
        if self.state[pid] != SUSCEPTIBLE:
            return
        self.state[pid] = EXPOSED
        self._ever_infected[pid] = True
        if not self._has_process[pid]:
            self._has_process[pid] = True
            self.env.process(self._disease_progression(pid))

    def _disease_progression(self, pid: int):
        # E -> I after incubation time
        incubation = _sample_lognormal_days(self.rng, self.inc_mu, self.inc_sigma)
        yield self.env.timeout(incubation)

        if self.state[pid] != EXPOSED:
            return
        self.state[pid] = INFECTIOUS

        # While infectious: generate contacts as a Poisson process with rate lambda(day)
        self.env.process(self._infectious_contacts(pid))

        # I -> R after infectious duration
        infectious_duration = _sample_gamma_days(self.rng, self.inf_k, self.inf_theta)
        yield self.env.timeout(infectious_duration)

        if self.state[pid] == INFECTIOUS:
            self.state[pid] = RECOVERED

    def _infectious_contacts(self, pid: int):
        while self.state[pid] == INFECTIOUS:
            current_day = int(self.env.now)
            lambda_per_day = _daily_contact_rate(current_day, self.scenario)
            if lambda_per_day <= 0:
                # No contacts; advance a bit to avoid a tight loop
                yield self.env.timeout(0.5)
                continue

            # Time to next contact in days ~ Exp(rate=lambda_per_day)
            dt = self.rng.expovariate(lambda_per_day)
            yield self.env.timeout(dt)

            if self.state[pid] != INFECTIOUS:
                break

            other = self.rng.randrange(self.n)
            if other == pid:
                continue
            if self.state[other] == SUSCEPTIBLE:
                if self.rng.random() < self.p_transmit:
                    self._infect(other)

    def _count_states(self) -> Tuple[int, int, int, int]:
        s = sum(1 for x in self.state if x == SUSCEPTIBLE)
        e = sum(1 for x in self.state if x == EXPOSED)
        i = sum(1 for x in self.state if x == INFECTIOUS)
        r = sum(1 for x in self.state if x == RECOVERED)
        return s, e, i, r

    def monitor_daily(self):
        for day in range(self.scenario.sim_days + 1):
            s, e, i, r = self._count_states()
            self.history["day"].append(day)
            self.history["S"].append(s)
            self.history["E"].append(e)
            self.history["I"].append(i)
            self.history["R"].append(r)
            self.cumulative_infected.append(sum(1 for x in self._ever_infected if x))
            yield self.env.timeout(1.0)

    def run(self) -> Dict[str, List[int]]:
        self.seed_initial_infections()
        self.env.process(self.monitor_daily())
        self.env.run(until=float(self.scenario.sim_days + 1))
        return self.history


def run_scenario(scenario: Scenario) -> Dict[str, List[int]]:
    env = simpy.Environment()
    model = EpidemicModel(env, scenario)
    history = model.run()
    history["cum_infected"] = model.cumulative_infected
    return history


def _to_dataframe(history: Dict[str, List[int]]):
    if pd is None:
        return None
    return pd.DataFrame(history)


def plot_seir(history: Dict[str, List[int]], title: str):
    days = history["day"]
    plt.figure(figsize=(10, 5))
    plt.plot(days, history["S"], label="S")
    plt.plot(days, history["E"], label="E")
    plt.plot(days, history["I"], label="I")
    plt.plot(days, history["R"], label="R")
    plt.title(title)
    plt.xlabel("Day")
    plt.ylabel("People")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()


def plot_comparison(h1: Dict[str, List[int]], h2: Dict[str, List[int]], name1: str, name2: str):
    days = h1["day"]

    plt.figure(figsize=(10, 5))
    plt.plot(days, h1["I"], label=f"I(t) — {name1}")
    plt.plot(days, h2["I"], label=f"I(t) — {name2}")
    plt.title("Scenario comparison: Infectious over time")
    plt.xlabel("Day")
    plt.ylabel("Infectious (I)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.figure(figsize=(10, 5))
    plt.plot(days, h1["cum_infected"], label=f"Cumulative infected — {name1}")
    plt.plot(days, h2["cum_infected"], label=f"Cumulative infected — {name2}")
    plt.title("Scenario comparison: Cumulative infected")
    plt.xlabel("Day")
    plt.ylabel("Cumulative infected")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()


def summarize(history: Dict[str, List[int]]) -> Dict[str, float]:
    peak_i = max(history["I"])
    day_peak = history["day"][int(np.argmax(history["I"]))]
    final_cum = history["cum_infected"][-1]
    return {"peak_I": float(peak_i), "day_peak_I": float(day_peak), "final_cum_infected": float(final_cum)}


def main():
    baseline = Scenario(
        name="Baseline",
        population=600,
        initial_infected=5,
        sim_days=160,
        contacts_per_day=12.0,
        target_r0=2.2,
        intervention_day=None,
        contact_reduction=0.0,
        seed=42,
    )

    intervention = Scenario(
        name="Intervention (50% contact reduction @ day 20)",
        population=600,
        initial_infected=5,
        sim_days=160,
        contacts_per_day=12.0,
        target_r0=2.2,
        intervention_day=20,
        contact_reduction=0.50,
        seed=42,  # same seed for fair-ish comparison
    )

    print("Running scenarios...")
    h_base = run_scenario(baseline)
    h_int = run_scenario(intervention)

    p = _transmission_probability_per_contact(baseline)
    print(f"Calibrated transmission probability per contact p ≈ {p:.4f}")

    s_base = summarize(h_base)
    s_int = summarize(h_int)
    print("\nSummary:")
    print(f"- Baseline: peak I={s_base['peak_I']:.0f} on day {s_base['day_peak_I']:.0f}, final cumulative infected={s_base['final_cum_infected']:.0f}")
    print(f"- Intervention: peak I={s_int['peak_I']:.0f} on day {s_int['day_peak_I']:.0f}, final cumulative infected={s_int['final_cum_infected']:.0f}")

    # Required visualizations:
    # Plot 1: SEIR curves for one scenario (baseline)
    plot_seir(h_base, title=f"SEIR curves — {baseline.name}")

    # Plot 2: comparison plots (counts as second visualization; actually produces 2 figures)
    plot_comparison(h_base, h_int, baseline.name, intervention.name)

    plt.show()

    # Optional: produce a table / CSV output if pandas is available
    if pd is not None:
        df_base = _to_dataframe(h_base)
        df_int = _to_dataframe(h_int)
        print("\nFirst rows (baseline):")
        print(df_base.head(10).to_string(index=False))
        # Uncomment if you want to save outputs:
        # df_base.to_csv("scenario_baseline.csv", index=False)
        # df_int.to_csv("scenario_intervention.csv", index=False)


if __name__ == "__main__":
    main()