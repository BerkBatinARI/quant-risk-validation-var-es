import numpy as np
import pandas as pd
from scipy.stats import chi2

TICKER = "SPY"

# Chi-square p-values:
# - Kupiec LR_uc ~ Chi^2(df=1)
# - Christoffersen LR_ind ~ Chi^2(df=1)
# - Christoffersen LR_cc ~ Chi^2(df=2)


def add_kupiec_pvalues(path_in: str, path_out: str) -> None:
    df = pd.read_csv(path_in).copy()

    if "LR_uc" not in df.columns:
        raise ValueError(f"Expected LR_uc column in {path_in}")

    df["p_uc"] = 1.0 - chi2.cdf(df["LR_uc"].astype(float), df=1)

    df.to_csv(path_out, index=False)
    print(f"Saved {path_out}")


def add_christoffersen_pvalues(path_in: str, path_out: str) -> None:
    df = pd.read_csv(path_in).copy()

    for col in ["LR_uc", "LR_ind", "LR_cc"]:
        if col not in df.columns:
            raise ValueError(f"Expected {col} column in {path_in}")

    df["p_uc"] = 1.0 - chi2.cdf(df["LR_uc"].astype(float), df=1)
    df["p_ind"] = 1.0 - chi2.cdf(df["LR_ind"].astype(float), df=1)
    df["p_cc"] = 1.0 - chi2.cdf(df["LR_cc"].astype(float), df=2)

    df.to_csv(path_out, index=False)
    print(f"Saved {path_out}")


def main() -> None:
    print("RUNNING add_pvalues.py main()")

    # Kupiec
    kupiec_in = f"data/{TICKER}_kupiec_summary.csv"
    kupiec_out = f"reports/tables/{TICKER}_kupiec_summary_with_pvalues.csv"
    add_kupiec_pvalues(kupiec_in, kupiec_out)

    # Christoffersen
    christ_in = f"data/{TICKER}_christoffersen_summary.csv"
    christ_out = f"reports/tables/{TICKER}_christoffersen_summary_with_pvalues.csv"
    add_christoffersen_pvalues(christ_in, christ_out)


if __name__ == "__main__":
    main()