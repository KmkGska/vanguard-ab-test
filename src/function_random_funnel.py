import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def compare_session_rules(df_full, sample_size=50, random_state=None):
    """
    Compare First, Longest, and Deepest session rules on a sample.
    Metrics: conversion rate, mean time-to-convert (min),
    mode time-to-convert (min), std of time-to-convert,
    correlation with #sessions.
    """
    ### select clients with >1 visit
    multi = df_full.groupby('client_id')['visit_id'].nunique()
    multi_clients = multi[multi > 1].index

    ### sample a subset of those clients
    rng = np.random.RandomState(random_state) if random_state is not None else np.random
    sampled = rng.choice(multi_clients, size=min(sample_size, len(multi_clients)), replace=False)
    df_sample = df_full[df_full['client_id'].isin(sampled)].copy()

    results = {}
    labels = {'first':'First Session','longest':'Longest Session','deepest':'Deepest Session'}

    for rule in ['first','longest','deepest']:
        if rule == 'first':
            ### pick earliest visit per client
            visits = df_sample.sort_values('date_time').groupby('client_id').first().reset_index()
            df_rule = df_sample.merge(visits[['client_id','visit_id']], on=['client_id','visit_id'])
        elif rule == 'longest':
            ### pick visit with most logs
            lengths = df_sample.groupby(['client_id','visit_id']).size().reset_index(name='n_logs')
            idx = lengths.groupby('client_id')['n_logs'].idxmax()
            df_rule = df_sample.merge(lengths.loc[idx, ['client_id','visit_id']], on=['client_id','visit_id'])
        else:
            ### pick visit reaching deepest step
            order = {'start':0,'step_1':1,'step_2':2,'step_3':3,'confirm':4}
            df_sample['step_index'] = df_sample['process_step'].map(order)
            depth = df_sample.groupby(['client_id','visit_id'])['step_index'].max().reset_index()
            idx = depth.groupby('client_id')['step_index'].idxmax()
            df_rule = df_sample.merge(depth.loc[idx, ['client_id','visit_id']], on=['client_id','visit_id'])

        ### compute conversion rate
        conv_rate = df_rule.groupby('client_id')['process_step'].apply(lambda x: (x=='confirm').any()).mean()

        ### compute time-to-convert list in minutes
        ttc = []
        for cid, grp in df_rule.groupby('client_id'):
            if (grp['process_step']=='confirm').any():
                start = grp['date_time'].min()
                end   = grp.loc[grp['process_step']=='confirm','date_time'].max()
                ttc.append((end - start).total_seconds() / 60)

        if ttc:
            mean_ttc = float(np.mean(ttc))
            std_ttc  = float(np.std(ttc))
            mode_ttc = float(stats.mode(ttc, keepdims=True).mode[0])
        else:
            mean_ttc, std_ttc, mode_ttc = np.nan, np.nan, np.nan

        ### compute correlation sessions vs conversion
        flag = df_rule.groupby('client_id')['process_step'].apply(lambda x: (x=='confirm').any()).astype(int)
        sessions = df_sample.groupby('client_id')['visit_id'].nunique()
        corr = flag.corr(sessions)

        results[labels[rule]] = {
            'conversion_rate': round(conv_rate,3),
            'mean_time_to_convert_min': round(mean_ttc,1) if pd.notna(mean_ttc) else None,
            'mode_time_to_convert_min': round(mode_ttc,1) if pd.notna(mode_ttc) else None,
            'std_time_to_convert': round(std_ttc,1) if pd.notna(std_ttc) else None,
            'corr_sessions_vs_conversion': round(corr,3) if pd.notna(corr) else None
        }

    return pd.DataFrame(results).T

def plot_session_metrics(metrics_df):
    """
    Plot conversion rate, mean & mode time-to-convert from metrics.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15,5))

    ### plot conversion rate
    metrics_df['conversion_rate'].plot(kind='bar', ax=axes[0], color='skyblue')
    axes[0].set_title("Conversion Rate"); axes[0].set_ylim(0,1)

    ### plot mean time-to-convert
    metrics_df['mean_time_to_convert_min'].plot(kind='bar', ax=axes[1], color='lightgreen')
    axes[1].set_title("Mean Time to Convert (min)")

    ### plot mode time-to-convert
    metrics_df['mode_time_to_convert_min'].plot(kind='bar', ax=axes[2], color='salmon')
    axes[2].set_title("Mode Time to Convert (min)")

    plt.tight_layout()
    plt.show()