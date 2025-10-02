import pandas as pd
from datetime import timedelta

# ---- Config -------------------------------------------------------------
STEP_ORDER = ['start','step_1','step_2','step_3','confirm']
TENURE_THRESHOLD_DAYS = 90  # 'new' means first start was within 90 days of dataset start

# ---- Helpers ------------------------------------------------------------
def add_age_band(df):
    """
    ### assign each client to an age bracket or 'unknown' if missing
    """
    if 'clnt_age' in df.columns and df['clnt_age'].notna().any():
        return df.assign(age_band=pd.cut(
            df['clnt_age'], [0,30,50,150],
            labels=['<30','30–50','50+'], right=False
        ))
    return df.assign(age_band='unknown')

def add_gender_group(df):
    """
    ### normalize gender into M, F, or U
    """
    g = df['gendr'].fillna('U').str.upper()
    return df.assign(gender_group=g.where(g.isin(['M','F','U','X']), 'U'))

def compute_client_tenure(df):
    """
    ### label clients 'new' or 'long-standing' based on first start date
    """
    first_start = (
        df[df['process_step']=='start']
        .groupby('client_id')['date_time']
        .min()
        .rename('first_start_dt')
    )
    base = df[['client_id']].drop_duplicates().merge(first_start, on='client_id')
    ref = df['date_time'].min()
    days = (ref - base['first_start_dt']).dt.days
    return base.assign(tenure_group=pd.cut(
        days, [-1, TENURE_THRESHOLD_DAYS, 10**6],
        labels=['new','long-standing']
    ).fillna('new'))

def client_snapshot(df):
    """
    ### build one-row-per-client summary with demographics, counts, times, tenure
    """
    df2 = add_age_band(add_gender_group(df))

    visits   = df2.groupby('client_id')['visit_id'].nunique().rename('visits')
    starts   = df2[df2['process_step']=='start'].groupby('client_id').size().rename('starts_count')
    confirms = df2[df2['process_step']=='confirm'].groupby('client_id').size().rename('confirms_count')

    first_s = df2[df2['process_step']=='start'].groupby('client_id')['date_time'].min().rename('first_start_dt')
    last_c  = df2[df2['process_step']=='confirm'].groupby('client_id')['date_time'].max().rename('last_confirm_dt')
    comp_t  = (last_c - first_s).rename('completion_time')

    demo    = df2.groupby('client_id')[['age_band','gender_group']].first()
    tenure  = compute_client_tenure(df2).set_index('client_id')['tenure_group']

    snap = (
        demo.join(visits,   how='left')
            .join(starts,   how='left')
            .join(confirms, how='left')
            .join(first_s,  how='left')
            .join(last_c,   how='left')
            .join(comp_t,   how='left')
            .join(tenure,   how='left')
            .fillna({
                'visits':0,
                'starts_count':0,
                'confirms_count':0,
                'tenure_group':'new'
            })
    )
    return snap

def behavior_metrics(df):
    """
    ### compute client counts, retry/restart rates, completion rate, mean+std time in minutes
    """
    snap = client_snapshot(df)
    total   = len(snap)
    retry   = (snap['visits'] > 1).mean()
    restart = (snap['starts_count'] > 1).mean()
    complete= (snap['confirms_count'] > 0).mean()

    times = snap['completion_time'].dropna().dt.total_seconds() / 60
    mean_t = times.mean() if not times.empty else None
    std_t  = times.std()  if not times.empty else None

    return {
        'clients': total,
        'retry_rate': round(retry,   3),  # fraction of clients with >1 visit
        'restart_rate': round(restart,3),  # fraction with >1 start
        'completion_rate': round(complete,3),
        'mean_completion_time_min': round(mean_t,1) if mean_t is not None else None,
        'std_completion_time_min':  round(std_t,1)  if std_t  is not None else None
    }

def primary_segments(df):
    """
    ### find the most common age band, gender, and tenure group
    """
    snap = client_snapshot(df)
    return {
        'primary_age_band':  snap['age_band'].mode()[0],
        'primary_gender':    snap['gender_group'].mode()[0],
        'primary_tenure':    snap['tenure_group'].mode()[0]
    }

def stepwise_rates(df):
    """
    ### fraction of clients who reached each process step
    """
    total = df['client_id'].nunique()
    return {
        step: round(df[df['process_step']==step]['client_id'].nunique() / total, 3)
        for step in STEP_ORDER
    }

def variation_comparison(df):
    """
    ### compute conversion rate by variation without warnings
    """
    client = df.groupby('client_id').agg(
        assign    = ('Variation',   'first'),                     # first variation assigned
        converted = ('process_step', lambda x: x.eq('confirm').any())  # True if any confirm
    )
    return client.groupby('assign')['converted'].mean().round(3).to_dict()

# ---- Run Day 1 summary --------------------------------------------------
def day1_wrap(df_full):
    """
    ### print primary segments, behavior metrics, step rates, and variation conversion
    """
    prim  = primary_segments(df_full)
    beh   = behavior_metrics(df_full)
    steps = stepwise_rates(df_full)
    var   = variation_comparison(df_full)

    print("Primary segments:", prim)
    print(f"  Note: 'new' tenure = first start within {TENURE_THRESHOLD_DAYS} days")
    print("Behavior metrics:")
    print(f"  Clients: {beh['clients']}")
    print(f"  Retry rate (>1 visit): {beh['retry_rate']}")
    print(f"  Restart rate (>1 start): {beh['restart_rate']}")
    print(f"  Completion rate: {beh['completion_rate']}")
    print(f"  Mean completion time: {beh['mean_completion_time_min']} min "
          f"(std: {beh['std_completion_time_min']} min)")
    print("Stepwise reach rates:", steps)
    print("Client-level conversion by Variation:", var)