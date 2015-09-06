# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 14:45:22 2015

@author: NancyLi
"""

import pandas as pd

from datetime import datetime

from chorogrid import Colorbin, Chorogrid

import seaborn as sns
import matplotlib.pyplot as plt

## import data --------------------------------------------------------------------------------------

drive = '/Users/NancyLi/Desktop/GitHub/prosper_loan_credit_quality/data/'
columns = ['ListingStartDate','ListingStatus','ListingStatusDescription',
           'ProsperRating','BorrowerRate','ListingTerm','ScoreX',
           'FICOScore','ProsperScore','IncomeRange',
           'IncomeRangeDescription','StatedMonthlyIncome','IncomeVerifiable',
           'EmploymentStatusDescription','Occupation','MonthsEmployed',
           'BorrowerState','BorrowerCity','IsHomeowner','InvestmentTypeID',
           'InvestmentTypeDescription','ListingAmountFunded']

listings = pd.read_csv(drive + 'ListingsFull.csv', usecols= columns)
population = pd.read_csv(drive + 'Population.csv')

## data cleaning --------------------------------------------------------------------------------------

listings.dropna(inplace = True)
listings =listings[listings['IncomeVerifiable']==True]
listings = listings.reset_index(drop=True)

## parse date time --------------------------------------------------------------------------------------

def try_parsing_date(text):
    for fmt in ('%m/%d/%Y  %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            ind = text.find('.')
            return datetime.strptime(text[:ind], fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

listings['dates_object'] = listings.ListingStartDate.map(lambda x: try_parsing_date(x))
listings['Year'] = listings.dates_object.map(lambda x:  x.year)

## data visualization --------------------------------------------------------------------------------------

# 1.1 number of loans issued by states, normalized by state population -  choropleth map 
counts = listings.groupby(['BorrowerState']).ListingAmountFunded.count()
population.index = population['state']
df = population.join(counts, how = 'right')
df['percentage'] = df['ListingAmountFunded']/df['population']*10000

mycolors = ['#e0e9f0', '#c1d4e2',  '#a3bed4', '#84a9c6','#6694b8', '#517693', '#3d586e']
mybin = Colorbin(df['percentage'], mycolors, proportional=True, decimals=None)
mybin.set_decimals(1)
mybin.recalc(fenceposts=True)
mybin.fenceposts
mybin.calc_complements(0.5, '#e0e0e0', '#101010')
states = list(df.index)
colors_by_state = mybin.colors_out
font_colors_by_state = mybin.complements
legend_colors = mybin.colors_in
legend_labels = mybin.labels
cg = Chorogrid('chorogrid/databases/usa_states.csv', states, colors_by_state)
cg.set_title('Number of P2P Loans Normalized by State Population', font_dict={'font-size': 16})
cg.set_legend(legend_colors, legend_labels, title='# of Loans scaled by population')
cg.draw_hex(spacing_dict={'margin_right': 210}, font_colors=font_colors_by_state)
cg.done(show=True)

# 1.2 number of loans issued by states -  choropleth map 
df = listings.groupby(['BorrowerState']).ListingAmountFunded.count()

mycolors = ['#e0e9f0', '#c1d4e2',  '#a3bed4', '#84a9c6','#6694b8', '#517693', '#3d586e']
mybin = Colorbin(df, mycolors, proportional=True, decimals=None)
mybin.set_decimals(1)
mybin.recalc(fenceposts=True)
mybin.fenceposts
mybin.calc_complements(0.5, '#e0e0e0', '#101010')
states = list(df.index)
colors_by_state = mybin.colors_out
font_colors_by_state = mybin.complements
legend_colors = mybin.colors_in
legend_labels = mybin.labels
cg = Chorogrid('chorogrid/databases/usa_states.csv', states, colors_by_state)
cg.set_title('Number of P2P Loans Issued', font_dict={'font-size': 16})
cg.set_legend(legend_colors, legend_labels, title='# of Loans Issued')
cg.draw_hex(spacing_dict={'margin_right': 210}, font_colors=font_colors_by_state)
cg.done(show=True)

# 2. borrowing rate per Prosper rating per year  -  heat map
pivot = pd.pivot_table(listings, index = ['Year'], columns = ['ProsperRating'], values = ['BorrowerRate'], aggfunc = 'median')
col_rearrange = ['AA', 'A', 'B', 'C', 'D', 'E', 'HR'] 
data = pivot['BorrowerRate'][col_rearrange]
f = plt.figure(figsize=(10,5))
ax1 = plt.subplot2grid((1, 1), (0, 0))
sns.heatmap(data, annot=True, fmt=".2f", ax=ax1);
f.suptitle('Prosper Rate per Credit Rating', fontsize=16, fontweight="bold")
f.savefig(drive+'prosper rate per year.png', transparent=True)

# 3. per income range - box plot
income_count = pd.pivot_table(listings, index = ['IncomeRangeDescription'], values = ['BorrowerRate'], aggfunc = 'count')/1000.0
income_count = income_count.sort_index(axis=0, by = 'BorrowerRate', ascending = False)

f = plt.figure(figsize=(9,5))
ax1 = plt.subplot2grid((1, 3), (0, 0))
ax2 = plt.subplot2grid((1, 3), (0, 1), colspan=2)

order = ['$100,000+', '$75,000-99,999', '$50,000-74,999', '$25,000-49,999', '$1-24,999'] 
g = sns.barplot(x = income_count[:5].index,  y = 'BorrowerRate', data = income_count[:5], palette="Greys_d", order = order, ax=ax1)
g.set_xticklabels(order, rotation=45, ha='right', fontsize = 12); g.set_xlabel(''); 
g.set_ylabel('# of Loans Issued in 000', fontsize = 12); 

# 4. top 10 occupation - box plot
occupation_count = pd.pivot_table(listings, index = ['Occupation'], values = ['BorrowerRate'], aggfunc = 'count')/1000.0
occupation_count = occupation_count.sort_index(axis=0, by = 'BorrowerRate', ascending = False)

g = sns.barplot(x = occupation_count[2:12].index,  y = 'BorrowerRate', data = occupation_count[2:12], palette="Oranges_d", ax=ax2)
g.set_xticklabels(occupation_count[2:12].index,rotation=45, ha='right', fontsize = 12); g.set_xlabel(''); 
g.set_ylabel('', fontsize = 12); 

f.suptitle('Income Range and Top Occupations according to # of Loans Issued', fontsize = 14, fontweight="bold")
f.savefig(drive+'top occupations bar plot.png', transparent=True, bbox_inches='tight')