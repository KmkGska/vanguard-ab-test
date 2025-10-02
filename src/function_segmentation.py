import pandas as pd
from scipy.stats import chi2_contingency

def get_segment(df_full, funnel_step, verbose=True, run_chi=True, first_only=False):
    """
    Segment analysis for a given funnel step (or 'all').
    
    Parameters
    ----------
    df_full : DataFrame
        Full dataset of sessions.
    funnel_step : str
        Funnel step to filter ('start','step_1','step_2','step_3','confirm','all').
    verbose : bool
        Print descriptive stats.
    run_chi : bool
        Run chi-square tests.
    first_only : bool
        If True, restrict to FIRST session of each multi-session client.
        If False, use all sessions (session-oriented).
    """
    step_order = ['start','step_1','step_2','step_3','confirm']
    funnel_step = funnel_step.lower()

    # --- Toggle: first-only vs all sessions ---
    if first_only:
        multi_clients = df_full.groupby('client_id')['visit_id'].nunique()
        multi_clients = multi_clients[multi_clients > 1].index
        df_multi = df_full[df_full['client_id'].isin(multi_clients)].copy()
        first_visits = (
            df_multi.sort_values('date_time')
            .groupby('client_id')
            .first()
            .reset_index()[['client_id','visit_id']]
        )
        df_base = df_multi.merge(first_visits, on=['client_id','visit_id'])
    else:
        df_base = df_full.copy()

    # --- Funnel filtering ---
    if funnel_step == "all":
        df = df_base[df_base['Variation'].isin(['Test','Control'])] \
                .drop_duplicates(subset=['client_id','process_step']).copy()
    else:
        df = df_base[
            (df_base['process_step'] == funnel_step) &
            (df_base['Variation'].isin(['Test','Control']))
        ].drop_duplicates(subset=['client_id']).copy()

    # --- Demographics & engagement flags ---
    if 'clnt_age' in df.columns and df['clnt_age'].notna().sum() > 0:
        df['age_band'] = pd.cut(df['clnt_age'], bins=[0,30,50,150],
                                labels=['<30','30–50','50+'], right=False)
    else:
        df['age_band'] = 'unknown'

    df['gender_group'] = df['gendr'].fillna('U').astype(str).str.upper()
    df['gender_group'] = df['gender_group'].where(df['gender_group'].isin(['M','F','U','X']), 'U')

    if 'bal' in df.columns and df['bal'].notna().sum() > 0:
        try:
            df['bal_quartile'] = pd.qcut(df['bal'], q=4,
                                         labels=['Low','Medium','High','Highest'],
                                         duplicates='drop')
        except ValueError:
            df['bal_quartile'] = 'unknown'
    else:
        df['bal_quartile'] = 'unknown'

    df['logon_flag'] = df.get('logons_6_mnth', 0).apply(lambda x: 'active' if x >= 1 else 'inactive')
    df['call_flag'] = df.get('calls_6_mnth', 0).apply(lambda x: 'support-heavy' if x >= 2 else 'low-touch')
    df['converted'] = df['process_step'] == 'confirm'

    # --- Verbose summary ---
    if verbose:
        mode = "FIRST sessions only" if first_only else "ALL sessions"
        if funnel_step == "all":
            print(f"{mode} — ALL STEPS — {df.shape[0]} rows (clients × steps)")
            print("Step distribution:", df['process_step'].value_counts().to_dict())
        else:
            print(f"{mode} — {funnel_step.upper()} — {df.shape[0]} clients")
        print("Variation split:", df['Variation'].value_counts().to_dict())
        print("Age Bands:", df['age_band'].value_counts().to_dict())
        print("Gender:", df['gender_group'].value_counts().to_dict())
        print("Balance Quartiles:", df['bal_quartile'].value_counts().to_dict())
        print("Logon flag:", df['logon_flag'].value_counts().to_dict())
        print("Call flag:", df['call_flag'].value_counts().to_dict())

    # --- Chi-square tests ---
    if run_chi:
        if funnel_step == "all":
            contingency = pd.crosstab(df['Variation'], df['process_step'])
            chi2, p, dof, _ = chi2_contingency(contingency)
            print("\nChi-square across ALL funnel steps:")
            print(contingency)
            print(f"Chi²={chi2:.2f}, p={p:.4f}, dof={dof}")
        elif funnel_step == 'confirm':
            contingency = pd.crosstab(df['Variation'], df['converted'])
            chi2, p, dof, _ = chi2_contingency(contingency)
            print("\nChi-square on conversion:")
            print(contingency)
            print(f"Chi²={chi2:.2f}, p={p:.4f}, dof={dof}")
        else:
            try:
                next_index = step_order.index(funnel_step) + 1
                next_step = step_order[next_index]
                df['reached_next'] = df['client_id'].isin(
                    df_base[df_base['process_step'] == next_step]['client_id']
                )
                contingency = pd.crosstab(df['Variation'], df['reached_next'])
                chi2, p, dof, _ = chi2_contingency(contingency)
                print(f"\nChi-square on progression to {next_step.upper()}:")
                print(contingency)
                print(f"Chi²={chi2:.2f}, p={p:.4f}, dof={dof}")
                print("\nDrop-off by Age Band:")
                print(df.groupby(['Variation','age_band'], observed=True)['reached_next'].mean().round(3).unstack())
                print("\nDrop-off by Balance Quartile:")
                print(df.groupby(['Variation','bal_quartile'], observed=True)['reached_next'].mean().round(3).unstack())
            except IndexError:
                print("No next step available for chi-square progression test.")

    return df