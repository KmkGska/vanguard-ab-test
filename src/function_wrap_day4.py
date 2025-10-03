import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind, norm, t

# ---- Plot helpers ---------------------------------------------------------
def plot_z_test(z_stat, alpha=0.05):
    """
    # Plot standard normal null, shade two‐sided rejection, mark z_stat
    """
    x = np.linspace(-4, 4, 400)
    y = norm.pdf(x)
    crit = norm.ppf(1 - alpha/2)                    # two‐sided critical
    plt.figure(figsize=(6,3))
    plt.plot(x, y, label='Null PDF')
    plt.fill_between(x, 0, y, where=(x <= -crit)|(x >= crit), color='gray', alpha=0.3)
    plt.axvline(z_stat, color='red', label=f'z={z_stat}')
    plt.axvline(-crit, color='black', linestyle='--')
    plt.axvline(crit,  color='black', linestyle='--', label=f'±{crit:.2f}')
    plt.title('Z-Test Null Distribution')
    plt.legend()
    plt.show()

def plot_t_test(t_stat, df, alpha=0.05):
    """
    # Plot t null with df, shade two‐sided rejection, mark t_stat
    """
    x = np.linspace(-4, 4, 400)
    y = t.pdf(x, df)
    crit = t.ppf(1 - alpha/2, df)                  # two‐sided critical
    plt.figure(figsize=(6,3))
    plt.plot(x, y, label=f't_df={df}')
    plt.fill_between(x, 0, y, where=(x <= -crit)|(x >= crit), color='gray', alpha=0.3)
    plt.axvline(t_stat, color='red', label=f't={t_stat}')
    plt.axvline(-crit, color='black', linestyle='--')
    plt.axvline(crit,  color='black', linestyle='--', label=f'±{crit:.2f}')
    plt.title('Welch t-Test Null Distribution')
    plt.legend()
    plt.show()

# ---- Statistical tests ----------------------------------------------------
def test_completion_rate(df, lift_thresh=0.05):
    # build 0/1 conversion flag per client
    conv = (
        df.groupby('client_id')['process_step']
          .apply(lambda s: s.eq('confirm').any())
          .astype(int)
    )
    # arm label per client
    grp = df.groupby('client_id')['Variation'].first()
    tbl = pd.DataFrame({'grp': grp, 'conv': conv})

    # counts & sizes
    counts = tbl.groupby('grp')['conv'].sum()
    ns     = tbl.groupby('grp')['conv'].size()

    # proportions z-test H0: p_Test - p_Control = lift_thresh
    z_stat, p_val = proportions_ztest(
        counts.values, ns.values,
        value=lift_thresh,
        alternative='two-sided'
    )

    rates = (counts / ns).round(3)
    lift  = round(rates['Test'] - rates['Control'], 3)
    return rates.to_dict(), lift, round(z_stat,3), round(p_val,4)

def test_completion_time(df):
    # compute per-client completion time in minutes
    starts   = df[df['process_step']=='start'].groupby('client_id')['date_time'].min()
    confirms = df[df['process_step']=='confirm'].groupby('client_id')['date_time'].max()
    times    = (confirms - starts).dt.total_seconds().div(60)

    grp = df.groupby('client_id')['Variation'].first()
    tbl = pd.DataFrame({'grp': grp, 'time': times}).dropna()

    # split groups
    ctrl = tbl.loc[tbl['grp']=='Control','time']
    test = tbl.loc[tbl['grp']=='Test',   'time']
    means = {'Control': round(ctrl.mean(),1), 'Test': round(test.mean(),1)}

    # Welch’s t-test H0: μ_Test = μ_Control
    t_stat, p_val = ttest_ind(test, ctrl, equal_var=False)
    return means, round(t_stat,3), round(p_val,4), ctrl, test

# ---- Main wrap ------------------------------------------------------------
def day4_wrap(df):
    alpha = 0.05
    lift_thresh = 0.05

    # --- run z-test on rates ---
    print("=== z-Test: Completion Rates ===")
    print("Why: rates are 0/1 → proportions z-test. Test if lift ≠ 5%")
    print(f"H0: p_Test - p_Control = {lift_thresh}")
    print("H1: p_Test - p_Control ≠ 5%")
    rates, lift, z, p1 = test_completion_rate(df, lift_thresh)
    verdict1 = ("Reject H0" if p1<=alpha else "Fail to reject H0")
    print(f"Result: z={z}, p={p1} → {verdict1}")
    print(f"Observed lift: {lift*100}%\n")
    plot_z_test(z, alpha)

    # --- run t-test on means ---
    print("=== Welch t-Test: Completion Times ===")
    print("Why: times are continuous → Welch’s t-test. Test if means differ")
    print("H0: μ_Test = μ_Control")
    print("H1: μ_Test ≠ μ_Control")
    means, t_stat, p2, ctrl_times, test_times = test_completion_time(df)
    verdict2 = ("Reject H0" if p2<=alpha else "Fail to reject H0")
    print(f"Result: t={t_stat}, p={p2} → {verdict2}")
    print(f"Means (min): Control={means['Control']}, Test={means['Test']}\n")
    # approximate df for plotting
    df_welch = (
        (ctrl_times.var()/ctrl_times.size + test_times.var()/test_times.size)**2
        / ((ctrl_times.var()/ctrl_times.size)**2/(ctrl_times.size-1)
           + (test_times.var()/test_times.size)**2/(test_times.size-1))
    )
    plot_t_test(t_stat, df=int(df_welch), alpha=alpha)

    return {
        'rate_test': {'rates': rates, 'lift': lift, 'z': z, 'p': p1, 'verdict': verdict1},
        'time_test': {'means': means, 't': t_stat, 'p': p2, 'verdict': verdict2}
    }

# Usage:
# results = day4_wrap(df_full)