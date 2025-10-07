import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def gender_piechart(df_clients): #Pie Chart for Gender % visualization
    gender_counts = df_clients['gender'].value_counts()

    color_map = {'M': 'lightblue', 'F': 'lightgreen', 'U': 'lightgray'}
    colors = [color_map.get(g, 'gray') for g in gender_counts.index]

    plt.figure(figsize=(3, 3))
    plt.pie(
        gender_counts,
        labels=gender_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors
    )
    plt.title('Gender Distribution')
    plt.axis('equal')
    plt.show()


def all_charts(df_columns):
    # List of numeric columns
    numeric_cols = [
        'client_tenure_years',
        'age',
        'number_of_accounts',
        'balance',
        'calls_6_months',
        'logons_6_months'
    ]

    plt.figure(figsize=(9, 12))
    for i, col in enumerate(numeric_cols, 1):
        # Apply log transformation for 'balance' only
        data = df_columns[col]  # <-- use the argument name here
        if col == 'balance':
            data = np.log1p(data)  # log(1 + x) to handle zeros safely

        # Histogram
        plt.subplot(len(numeric_cols), 2, 2*i - 1)
        sns.histplot(data, kde=True, bins='auto', color='blue')
        plt.title(f'Histogram of {col}' + (' (log scale)' if col == 'balance' else ''))
        plt.xlabel(col)
        plt.ylabel('Count')

        # Boxplot
        plt.subplot(len(numeric_cols), 2, 2*i)
        sns.boxplot(x=data, color='lightgreen')
        plt.title(f'Boxplot of {col}' + (' (log scale)' if col == 'balance' else ''))
        plt.xlabel(col)

    plt.tight_layout()
    plt.show()

def correlation_matrix(df_full):

    df_numeric = df_full.drop(columns=["client_id", "gender", "variation", "visitor_id", "visit_id", "date_time", "process_step"])

    correlation_matrix = df_numeric.corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        round(correlation_matrix, 2),
        annot=True,
        ax=ax,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        cbar_kws={"label": "Correlation Coefficient"}
    )

    plt.title("Correlation Heatmap", fontsize=8)
    plt.xticks(ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.show()

def completion_rate(df_full):
    funnel = ['start', 'step_1', 'step_2', 'step_3', 'confirm']

    fig, ax = plt.subplots(figsize=(6, 3))
    sns.countplot(
        x='process_step',
        data=df_full,
        order = funnel,
        hue='variation',
        palette=['lightyellow', 'lightblue'] 
    )
    for container in ax.containers:
        ax.bar_label(container, color='black', fmt='%d', label_type='center', fontsize=8)

    plt.title('Funnel registered for the two variations of all process that start')
    plt.tight_layout()
    plt.show()

def page_visits(df_full):
    df_visits = df_full.groupby(['client_id', 'variation']).agg(
        total_visits=('visit_id', 'count')
    ).reset_index() 
    
    print(df_visits.head())
    return df_visits

def boxplot_histogram(df_visits):
    
    # Boxplot and Histogram 

    # Set up the figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 6), gridspec_kw={'height_ratios': [3, 1]})

    # Loop through each variation
    for i, variation in enumerate(['Test', 'Control']):
        data = df_visits[df_visits['variation'] == variation]['total_visits'].dropna()

    # Compute quartiles and whisker
        q1 = np.percentile(data, 25)
        q2 = np.percentile(data, 50)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        upper_whisker = q3 + 1.5 * iqr

    # Histogram
        sns.histplot(data, bins='auto', kde=True, ax=axes[0, i],
                     color='lightyellow' if variation == 'Test' else 'lightblue')
        axes[0, i].axvline(q1, color='green', linestyle='--', label='Q1')
        axes[0, i].axvline(q2, color='black', linestyle='-', label='Q2 (Median)')
        axes[0, i].axvline(q3, color='orange', linestyle='--', label='Q3')
        axes[0, i].axvline(upper_whisker, color='red', linestyle=':', label='Upper Whisker')
        axes[0, i].set_title(f'{variation} Group - Histogram')
        axes[0, i].set_xlabel('Total Visits')
        axes[0, i].set_ylabel('Frequency')
        axes[0, i].legend()

    # Boxplot
        sns.boxplot(x=data, ax=axes[1, i],
                    color='lightyellow' if variation == 'Test' else 'lightblue')
        axes[1, i].set_title(f'{variation} Group - Boxplot')
        axes[1, i].set_xlabel('Total Visits')

    plt.tight_layout()
    plt.show()

def exceed_upper_whisker(df_visits):
    # Clients that visits excede the upper whisker
    # Calculate Q1 and Q3
    Q1 = df_visits['total_visits'].quantile(0.25)
    Q3 = df_visits['total_visits'].quantile(0.75)

    # Compute IQR and upper whisker
    IQR = Q3 - Q1
    upper_whisker = Q3 + 1.5 * IQR

    # Find clients exceeding the upper whisker
    outliers_visits_clients = df_visits[df_visits['total_visits'] > upper_whisker]['client_id']
    # check the number of cients that exceed the upper whisker
    print(f"There are {len(outliers_visits_clients)} clients that exceed the upper whisker.")
    print()
    return outliers_visits_clients
