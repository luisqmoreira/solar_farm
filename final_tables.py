import pandas as pd

data = pd.read_csv('/Users/luismoreira/Desktop/Final_project/final_project/missing_cloud_cover.csv')

data = data.drop('Unnamed: 0', axis=1)

# January

prec_jan = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal01.csv')


def split(row):
    return row.split()


prec_jan['split'] = prec_jan['19500131'].apply(split)

drop = []
for i in prec_jan['split']:
    if len(i) < 3:
        drop.append(i)
    else:
        continue

index_drop = []
for lis in drop:
    for num in lis:
        index_drop.append(prec_jan[prec_jan['19500131'] == num].index[0])

prec_jan = prec_jan.drop(index_drop)


def find_lat(row):
    return row[0]


def find_long(row):
    return row[1]


def find_value(row):
    return row[2]


prec_jan['lat'] = prec_jan['split'].apply(find_lat)
prec_jan['long'] = prec_jan['split'].apply(find_long)
prec_jan['value'] = prec_jan['split'].apply(find_value)

prec_clean_jan = prec_jan.drop(['19500131', 'split'], axis=1)

prec_clean_jan = prec_clean_jan.astype('float64')

prec_fev = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal02.csv')
prec_mar = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal03.csv')
prec_apr = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal04.csv')
# prec_may = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal05.csv')
prec_jun = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal06.csv')
prec_jul = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal07.csv')
prec_aug = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal08.csv')
prec_sep = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal09.csv')
prec_oct = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal10.csv')
prec_nov = pd.read_csv('/Users/luismoreira/Downloads/PRECIP_PT_mensal11.csv')

# splitting the column from one string with coordinates and value to a list

prec_fev['split'] = prec_fev[prec_fev.columns[0]].apply(split)
prec_mar['split'] = prec_mar[prec_mar.columns[0]].apply(split)
prec_apr['split'] = prec_apr[prec_apr.columns[0]].apply(split)

prec_jun['split'] = prec_jun[prec_jun.columns[0]].apply(split)
prec_jul['split'] = prec_jul[prec_jul.columns[0]].apply(split)
prec_aug['split'] = prec_aug[prec_aug.columns[0]].apply(split)
prec_sep['split'] = prec_sep[prec_sep.columns[0]].apply(split)
prec_oct['split'] = prec_oct[prec_oct.columns[0]].apply(split)
prec_nov['split'] = prec_nov[prec_nov.columns[0]].apply(split)

drop_fev = []
for i in prec_fev['split']:
    if len(i) < 3:
        drop_fev.append(i)
    else:
        continue
drop_mar = []
for i in prec_mar['split']:
    if len(i) < 3:
        drop_mar.append(i)
    else:
        continue

drop_apr = []
for i in prec_apr['split']:
    if len(i) < 3:
        drop_apr.append(i)
    else:
        continue

drop_jun = []
for i in prec_jun['split']:
    if len(i) < 3:
        drop_jun.append(i)
    else:
        continue

drop_jul = []
for i in prec_jul['split']:
    if len(i) < 3:
        drop_jul.append(i)
    else:
        continue

drop_aug = []
for i in prec_aug['split']:
    if len(i) < 3:
        drop_aug.append(i)
    else:
        continue

drop_sep = []
for i in prec_sep['split']:
    if len(i) < 3:
        drop_sep.append(i)
    else:
        continue

drop_oct = []
for i in prec_oct['split']:
    if len(i) < 3:
        drop_oct.append(i)
    else:
        continue

drop_nov = []
for i in prec_nov['split']:
    if len(i) < 3:
        drop_nov.append(i)
    else:
        continue

index_drop_fev = []
for lis in drop_fev:
    for num in lis:
        index_drop_fev.append(prec_fev[prec_fev[prec_fev.columns[0]] == num].index[0])

index_drop_mar = []
for lis in drop_mar:
    for num in lis:
        index_drop_mar.append(prec_mar[prec_mar[prec_mar.columns[0]] == num].index[0])

index_drop_apr = []
for lis in drop_apr:
    for num in lis:
        index_drop_apr.append(prec_apr[prec_apr[prec_apr.columns[0]] == num].index[0])

index_drop_jun = []
for lis in drop_jun:
    for num in lis:
        index_drop_jun.append(prec_jun[prec_jun[prec_jun.columns[0]] == num].index[0])

index_drop_jul = []
for lis in drop_jul:
    for num in lis:
        index_drop_jul.append(prec_jul[prec_jul[prec_jul.columns[0]] == num].index[0])

index_drop_aug = []
for lis in drop_aug:
    for num in lis:
        index_drop_aug.append(prec_aug[prec_aug[prec_aug.columns[0]] == num].index[0])

index_drop_sep = []
for lis in drop_sep:
    for num in lis:
        index_drop_sep.append(prec_sep[prec_sep[prec_sep.columns[0]] == num].index[0])

index_drop_oct = []
for lis in drop_oct:
    for num in lis:
        index_drop_oct.append(prec_oct[prec_oct[prec_oct.columns[0]] == num].index[0])

index_drop_nov = []
for lis in drop_nov:
    for num in lis:
        index_drop_nov.append(prec_nov[prec_nov[prec_nov.columns[0]] == num].index[0])

# dropping lines that include titles

prec_fev = prec_fev.drop(index_drop_fev)
prec_mar = prec_mar.drop(index_drop_mar)
prec_apr = prec_apr.drop(index_drop_apr)
prec_jun = prec_jun.drop(index_drop_jun)
prec_jul = prec_jul.drop(index_drop_jul)
prec_aug = prec_aug.drop(index_drop_aug)
prec_sep = prec_sep.drop(index_drop_sep)
prec_oct = prec_oct.drop(index_drop_oct)
prec_nov = prec_nov.drop(index_drop_nov)



prec_fev['lat'] = prec_fev['split'].apply(find_lat)
prec_fev['long'] = prec_fev['split'].apply(find_long)
prec_fev['value'] = prec_fev['split'].apply(find_value)

prec_mar['lat'] = prec_mar['split'].apply(find_lat)
prec_mar['long'] = prec_mar['split'].apply(find_long)
prec_mar['value'] = prec_mar['split'].apply(find_value)

prec_apr['lat'] = prec_apr['split'].apply(find_lat)
prec_apr['long'] = prec_apr['split'].apply(find_long)
prec_apr['value'] = prec_apr['split'].apply(find_value)

prec_jun['lat'] = prec_jun['split'].apply(find_lat)
prec_jun['long'] = prec_jun['split'].apply(find_long)
prec_jun['value'] = prec_jun['split'].apply(find_value)

prec_jul['lat'] = prec_jul['split'].apply(find_lat)
prec_jul['long'] = prec_jul['split'].apply(find_long)
prec_jul['value'] = prec_jul['split'].apply(find_value)

prec_aug['lat'] = prec_aug['split'].apply(find_lat)
prec_aug['long'] = prec_aug['split'].apply(find_long)
prec_aug['value'] = prec_aug['split'].apply(find_value)

prec_sep['lat'] = prec_sep['split'].apply(find_lat)
prec_sep['long'] = prec_sep['split'].apply(find_long)
prec_sep['value'] = prec_sep['split'].apply(find_value)

prec_oct['lat'] = prec_oct['split'].apply(find_lat)
prec_oct['long'] = prec_oct['split'].apply(find_long)
prec_oct['value'] = prec_oct['split'].apply(find_value)

prec_nov['lat'] = prec_nov['split'].apply(find_lat)
prec_nov['long'] = prec_nov['split'].apply(find_long)
prec_nov['value'] = prec_nov['split'].apply(find_value)

prec_fev = prec_fev.drop(prec_fev.columns[0:2], axis=1)
prec_mar = prec_mar.drop(prec_mar.columns[0:2], axis=1)
prec_apr = prec_apr.drop(prec_apr.columns[0:2], axis=1)
prec_jun = prec_jun.drop(prec_jun.columns[0:2], axis=1)
prec_jul = prec_jul.drop(prec_jul.columns[0:2], axis=1)
prec_aug = prec_aug.drop(prec_aug.columns[0:2], axis=1)
prec_sep = prec_sep.drop(prec_sep.columns[0:2], axis=1)
prec_oct = prec_oct.drop(prec_oct.columns[0:2], axis=1)
prec_nov = prec_nov.drop(prec_nov.columns[0:2], axis=1)

prec_jan = prec_clean_jan
prec_fev = prec_fev.astype('float64')
prec_mar = prec_mar.astype('float64')
prec_apr = prec_apr.astype('float64')
prec_jun = prec_jun.astype('float64')
prec_jul = prec_jul.astype('float64')
prec_aug = prec_aug.astype('float64')
prec_sep = prec_sep.astype('float64')
prec_oct = prec_oct.astype('float64')
prec_nov = prec_nov.astype('float64')

final = pd.concat([prec_jan, prec_fev, prec_mar, prec_apr, prec_jun, prec_jul, prec_aug, prec_sep, prec_oct, prec_nov])

final_grouped = final.groupby(['lat', 'long']).agg({'value': 'mean'})

