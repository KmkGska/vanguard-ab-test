import pandas as pd

# ------- Config -------
STEP_ORDER = ['start','step_1','step_2','step_3','confirm']  # process steps in order
ARMS = ['Control','Test']                                     # experiment arms

# ------- Small helpers -------
def _ordered(df):
    # sort events by client, timestamp, and step
    return df.sort_values(['client_id','date_time','process_step'])

def _first_per_client(df, step):
    # first time each client hits a given step
    return df[df['process_step']==step] \
             .groupby('client_id')['date_time'] \
             .min() \
             .rename(f'first_{step}')

def _last_per_client(df, step):
    # last time each client hits a given step
    return df[df['process_step']==step] \
             .groupby('client_id')['date_time'] \
             .max() \
             .rename(f'last_{step}')

def _step_reach_rates(df):
    # fraction of clients reaching each step
    total = df['client_id'].nunique()
    return {
        s: round(df[df['process_step']==s]['client_id'].nunique()/total, 3)
        for s in STEP_ORDER
    }

def _completion_rate(df):
    # overall conversion rate (ever reached confirm)
    conv = df[df['process_step']=='confirm']['client_id'].nunique()
    total = df['client_id'].nunique()
    return round(conv/total if total else 0.0, 3)

def _restart_rate(df):
    # fraction of clients who restarted (multiple starts)
    starts = df[df['process_step']=='start'].groupby('client_id').size()
    return round((starts>1).mean() if len(starts) else 0.0, 3)

def _step_times(df):
    """
    compute mean times between steps and overall completion in minutes
    """
    # get first start & last confirm per client
    first_start  = _first_per_client(df, 'start')
    last_confirm = _last_per_client(df, 'confirm')
    clients      = df['client_id'].unique()
    snap         = pd.DataFrame(index=clients)

    times = {}
    # per-step mean dwell time
    firsts = {s: _first_per_client(df, s) for s in STEP_ORDER}
    for i, s in enumerate(STEP_ORDER[:-1]):
        nxt = STEP_ORDER[i+1]
        tmp = snap.join(firsts[s]).join(firsts[nxt])
        # compute dwell in minutes
        dwell_min = (tmp[f'first_{nxt}'] - tmp[f'first_{s}']) \
                       .dt.total_seconds().div(60)
        times[f'{s}_to_{nxt}_mean_min'] = (
            round(dwell_min.mean(),1) if not dwell_min.dropna().empty else None
        )

    # overall completion time mean in minutes
    comp_min = (last_confirm - first_start) \
                   .dt.total_seconds().div(60)
    times['completion_time_mean_min'] = (
        round(comp_min.mean(),1) if not comp_min.dropna().empty else None
    )

    return times

def _error_rate(df):
    # proxy error rate: out-of-order steps or retry without confirm
    dfo = _ordered(df)
    # detect backward step movements
    step_ix = {s:i for i, s in enumerate(STEP_ORDER)}
    def has_seq_error(gr):
        idxs = gr['process_step'].map(step_ix).tolist()
        return any(b < a for a, b in zip(idxs, idxs[1:]))
    seq_err = dfo.groupby('client_id').apply(has_seq_error)

    # retry after failure: more starts, no confirm
    starts    = df[df['process_step']=='start'].groupby('client_id').size()
    has_conf  = df[df['process_step']=='confirm'] \
                  .groupby('client_id').size() \
                  .reindex(starts.index, fill_value=0) > 0
    retry_fail = (starts > 1) & (~has_conf)

    return round((seq_err | retry_fail).mean() if len(seq_err) else 0.0, 3)

def kpi_pack(df):
    # bundle all KPIs for one arm
    return {
        'completion_rate': _completion_rate(df),
        'restart_rate':    _restart_rate(df),
        'error_rate':      _error_rate(df),
        'step_reach_rates': _step_reach_rates(df),
        'step_times':      _step_times(df)
    }

def compare_designs(df_full):
    # compute KPIs per arm (Control vs Test)
    out = {}
    for arm in ARMS:
        df_arm = df_full[df_full['Variation']==arm]
        out[arm] = kpi_pack(df_arm)

    # helper to format time dict
    def flat_times(times):
        return {k: (v if v is not None else 'NA') for k,v in times.items()}

    # print summary
    print("KPIs — Completion / Restart / Error:")
    for arm in ARMS:
        print(f"  {arm}: compl={out[arm]['completion_rate']}, "
              f"restart={out[arm]['restart_rate']}, "
              f"error={out[arm]['error_rate']}")

    print("\nStep reach rates (fraction of clients reaching each step):")
    for arm in ARMS:
        print(f"  {arm}: {out[arm]['step_reach_rates']}")

    print("\nMean times (per-step transitions and overall completion in minutes):")
    for arm in ARMS:
        print(f"  {arm}: {flat_times(out[arm]['step_times'])}")

    # suggest verdict based on completion lift
    lift = round(out['Test']['completion_rate'] - out['Control']['completion_rate'], 3)
    status = ('Promising' if lift>0 else
              'Regressive' if lift<0 else 'Neutral')
    print(f"\nVerdict: completion lift = {lift} → {status} "
          "(validate with stats tests).")

    return out

# Usage:
# results = compare_designs(df_full)