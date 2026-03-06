# Time Series Risk Engine (Volatility → VaR/ES)

> Work in progress — I’m building this incrementally and checking everything with walk-forward tests.  
> Last updated: 2026-03-03

This repo is a small risk engine that turns a volatility forecast into 1-day **VaR** / **Expected Shortfall (ES)** estimates, then checks whether those risk numbers actually hold up in a simple backtest.

The goal is not “one perfect model”, but a clean comparison of sensible baselines (EWMA, GARCH, different return distributions) with transparent evaluation.


## Project structure

- `src/` — scripts (data download, feature engineering, risk models, backtests)
- `data/` — raw and processed datasets (generated locally)
- `reports/figures/` — key tracked outputs (plots embedded in this README)
- `notebooks/` — exploration / scratch work

## What this project does

This repository builds a small, reproducible risk-model validation pipeline for daily ETF returns.

Given historical prices, it:

- downloads market data (SPY/TLT/GLD) and computes daily log returns
- estimates 1-day volatility using multiple models (EWMA, GARCH)
- converts volatility into **1-day 99% Value-at-Risk (VaR)** estimates under different distributional assumptions (Normal vs Student-t)
- evaluates the quality of VaR forecasts using:
  - simple breach-rate backtesting (expected ≈ 1% at 99% VaR)
  - Kupiec unconditional coverage test (LR statistic)

The focus is not to “find one perfect model”, but to compare sensible baselines transparently, with tracked figures and clear diagnostics.


## Results so far (SPY, 1-day 99% VaR)

- **EWMA + Normal VaR** breaches: **2.36%** (expected ~1.00%) → underestimates tail risk.
- **EWMA + Student-t (df=6) VaR** breaches: **1.77%** → improved, still higher than expected.
- Kupiec unconditional coverage test (df=1):  
  - EWMA + Normal: **LR = 70.80** (rejects correct 99% coverage)  
  - EWMA + Student-t: **LR = 25.48** (still rejects, but closer)

### Diagnostics plots
The plots below show the EWMA Normal-VaR threshold against realised 1-day losses, and highlight when the model is breached (loss exceeds VaR).

#### VaR backtest (EWMA, 99%)
![SPY VaR backtest](reports/figures/SPY_var99_backtest.png)

#### Breach timeline (EWMA, 99%)
Markers indicate VaR exceptions (days where realised loss exceeds the predicted 99% VaR threshold).
![SPY VaR breaches](reports/figures/SPY_var99_breaches.png)

### GARCH(1,1) VaR (99%) — Walk-forward backtest

- Obs used: 4,821
- Breaches: 111
- Breach rate: 2.3024%


![SPY GARCH VaR(99%) Backtest](reports/figures/SPY_var99_garch_backtest.png)

### Christoffersen conditional coverage (independence + coverage)

This checks both:
- **coverage** (are breaches ~1% at 99% VaR?)
- **independence** (are breaches clustered or roughly independent over time?)

Results (LR statistics; lower is better):

- **EWMA + Normal**: `LR_uc` **70.80**, `LR_ind` **4.36**, `LR_cc` **75.16**
- **EWMA + Student-t (df=6)**: `LR_uc` **25.48**, `LR_ind` **4.66**, `LR_cc` **30.15**
- **GARCH(1,1) + Normal**: `LR_uc` **60.39**, `LR_ind` **0.73**, `LR_cc` **61.12**

**P-values (Chi-square approximation):**
- Kupiec `LR_uc` uses **df = 1**
- Christoffersen `LR_ind` uses **df = 1**
- Christoffersen `LR_cc` uses **df = 2**

Interpretation (rule of thumb): if **p < 0.05**, reject the model’s 99% VaR coverage assumptions.

| Model | Obs | Breaches | Breach rate | `LR_uc` | `p_uc` | `LR_ind` | `p_ind` | `LR_cc` | `p_cc` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EWMA + Normal | 5263 | 124 | 2.356% | 70.80 | ~0.000 | 4.36 | ~0.037 | 75.16 | ~0.000 |
| EWMA + Student-t (df=6) | 5263 | 93 | 1.767% | 25.48 | ~0.000 | 4.66 | ~0.031 | 30.15 | ~0.000 |
| GARCH(1,1) + Normal | 4822 | 111 | 2.302% | 60.39 | ~0.000 | 0.73 | ~0.392 | 61.12 | ~0.000 |

Full summary table: [`reports/tables/SPY_christoffersen_summary_with_pvalues.csv`](reports/tables/SPY_christoffersen_summary_with_pvalues.csv)

## Reproducibility

The commands below are **examples** of how to run the pipeline (you do **not** need to run them unless you want to regenerate outputs).

```bash
# Environment setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Fast pipeline (recommended)
python src/download_data.py
python src/make_features.py
python src/risk_ewma.py
python src/risk_t_var_es.py
python src/backtest_var.py
python src/backtest_var_t.py
python src/kupiec_test.py

# GARCH walk-forward VaR (slow; expanding-window refit)
python src/risk_garch.py
python src/backtest_var_garch.py
```