# Vanguard A/B Test Analysis  

## 📌 Project Overview  
This project analyzes the results of Vanguard’s digital A/B test, designed to evaluate whether a redesigned user interface with in-context prompts improves client completion rates compared to the traditional interface.  

The analysis includes:  
- Data cleaning and integration  
- Exploratory Data Analysis (EDA)  
- Key performance metrics definition  
- Hypothesis testing and experiment evaluation  
- Tableau visualizations  

Final deliverables include cleaned datasets, reproducible notebooks, functions in `.py` files, Tableau dashboards, and a project presentation.  

---
## Role : DA in CX at Vanguard
  
## Business Proposal / Research Teams Findings.  
Vanguard is one of the highest investments companies in the world, founded in 1975 their assets are nearly 8 Trillion USD! If you heard of mutual fund, index funds etc you heard of Vanguard.

Their premise and reputation is as "a reliability and low cost investment company"

Clients are both individuals or institutions, so for a company as vanguard the digital chanels are very important whether is an investor checking his balance at the website or a financial advisor managing portafolios online, their UI direct impacts in user engage, trust an ultimatelly the business outcome.

So, they run experiments on their website and mobile platform to figure out what work best for users. This can mean testing buttons places, layout or some specific wording; and we know if this have impact if a client complete and investment transaction, sign up for an account etc etc

## The Experiment A/B Test:
We assign our clients randomly (as flip a coin) as variance test, who will use the new UI or variance control who use the old UI.

They need to be as similar as possible (we we'll check that)

As for Effectiveness, this lasted for a period of 97 days from 15/3/17 to 20/6/17 since is a Cost of Regret associated, this means that you are losing opportunities for showing clients the "wrong" UI while you conduct the experiment. 

Both variances went into a funnel of initial page, steps 1-3 and confirmation page signaling the completition.

## Goal
Get the completition rate of Test vs Control.

This will allow you optimize digital experience faster, minimizing lost of opportunity in the future and make better data driven decistions. 

## Sources
David Sweet - Experimentation for Engineers_ From A_B testing to Bayesian optimization (2023, Manning Publications)
Leemay Nassery - Practical A_B Testing_ Creating Experimentation-Driven Products (2023, Pragmatic Bookshelf)
Snacks Weekly on Data Science Podcast - Vanguard A/B testing vs Multi-armed bandits. 

---
---

## 🔬 Hypotheses  
1. **Completion Rate**  
   - The Test group will have a higher completion rate than the Control group.  
2. **Time on Steps**  
   - The Test group will spend less time on average at each process step.  
3. **Error Rate**  
   - The Test group will show fewer backward navigation errors.
   
## 📂 Repository Structure  
```p    ├── data
│ ├── raw # Original datasets
│ └── clean # Cleaned datasets
├── notebooks
│ ├── functions.py # Utility functions for config, cleaning, EDA, etc.
│ └── (Jupyter notebooks for analysis)
├── figures # Visualizations and plots
├── slides # Google Slides link for presentation
├── config.yaml # Config file for dataset paths
├── README.md # Project documentation
```
## ⚙️ Tech Stack  
- **Python**: pandas, numpy, seaborn, matplotlib, scipy  
- **SQL**: queries and checks  
- **Tableau**: interactive dashboards  
- **GitHub & Trello**: collaboration and project management  

---

## 📊 Deliverables  
- Clean datasets  
- EDA and analysis notebooks  
- Functions in `.py` scripts  
- Tableau dashboard  
- Project presentation (Google Slides link)  
- GitHub repo with full documentation  

---

## 🔗 Useful Links  
- [Kanban Board (Trello)](your-link-here)  
- [Google Slides Presentation](your-link-here)  

--- increased by 5%.


## **Deliverables**


