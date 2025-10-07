# Manipulating Data
import pandas as pd
import numpy as np

# Visualizing Data
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

# Statistical Analysis
from scipy.stats import (
    ttest_ind,
    chi2_contingency,
    norm,
    mannwhitneyu,
    shapiro,
    probplot
)
from statsmodels.stats.proportion import (
    proportions_ztest,
    proportions_chisquare
)
import statsmodels.api as sm

import sys
sys.path.append("../src")

pd.set_option('display.float_format', '{:.2f}'.format)

client_url = "../data/clean_data_txt/df_full.csv"
df_clients = pd.read_csv(client_url)
df_full = pd.read_pickle('../data/clean_data_txt/df_full.pkl')
