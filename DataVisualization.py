import os, warnings, importlib, subprocess

dependencies = ('pandas', 'plotly', 'pycountry_convert')
for module in dependencies:
    try:
        importlib.import_module(module)
    except ImportError:
        subprocess.check_call(['pip', 'install', module], stdout = subprocess.DEVNULL)

import pandas as pd
import plotly.express as px
import pycountry_convert as pc

os.chdir(os.path.dirname(os.path.realpath(__file__)))
warnings.filterwarnings('ignore')

def country_to_continent(country_name):
    if country_name in ['Antigua And Barbuda', 'Saint Kitts And Nevis', 'Saint Pierre And Miquelon', 'Saint Vincent And The Grenadines', 'Sint Maarten', 'Svalbard And Jan Mayen', 'Turks And Caicas Islands', 'Virgin Islands']:
        return 'North America'
    if country_name in ['Bonaire, Saint Eustatius And Saba', 'Falkland Islands (Islas Malvinas)', 'Trinidad And Tobago']:
        return 'South America'
    if country_name in ['Åland', 'Bosnia And Herzegovina', 'Denmark (Europe)', 'France (Europe)', 'Isle Of Man', 'Netherlands (Europe)', 'United Kingdom (Europe)']:
        return 'Europe'
    if country_name in ['Baker Island', 'Federated States Of Micronesia', 'Kingman Reef', 'Palmyra Atoll']:
        return 'Oceania'
    if country_name in ['Burma', 'Gaza Strip', 'Palestina', 'Timor Leste']:
        return 'Asia'
    if country_name in ['Côte D\'Ivoire', 'Congo (Democratic Republic Of The)', 'Guinea Bissau', 'Reunion', 'Sao Tome And Principe']:
        return 'Africa'
    if country_name in ['French Southern And Antarctic Lands', 'Heard Island And Mcdonald Islands', 'South Georgia And The South Sandwich Isla']:
        return 'Antartica'
    if country_name in ['Asia', 'Africa', 'Europe', 'North America', 'Oceania', 'South America']:
        return country_name
    
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    if country_alpha2 == 'AQ':
        return 'Antartica'
    if country_alpha2 == 'EH':
        return 'Africa'
    
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name

df                = pd.read_csv('./GlobalLandTemperaturesByCountry.csv', usecols = ['dt', 'AverageTemperature', 'Country'])
df.dt             = pd.to_datetime(df.dt)
df['Year']        = df.dt.dt.year
df.dropna(subset  = ['AverageTemperature'], inplace = True)
df['Continent']   = df.Country.apply(country_to_continent)
df.drop(columns   = ['dt', 'Country'], inplace = True)
df.rename(columns = {'AverageTemperature': 'Average Temperature'}, inplace = True)
largest           = 0

for i in df.Continent.unique():
    if df[df.Continent == i].Year.min() >= largest:
        largest = df[df.Continent == i].Year.min()

df = df[df.Year >= largest]
df = df.groupby(['Continent', 'Year']).mean('Average Temperature')
df.reset_index(inplace = True)

year = [i for i in range(1874, 2014)]
df2  = {'Continent'           : [],
        'Year'                : [],
        'Average Temperature' : []}

for i in year:
    if i not in df[df.Continent == 'Antartica']['Year'].unique():
        df2['Continent'].append('Antartica')
        df2['Year'].append(i)
        df2['Average Temperature'].append(df[df.Continent == 'Antartica']['Average Temperature'].mean())
    
df2  = pd.DataFrame(df2)
df   = pd.concat([df, df2])
df2  = {'Continent'           : [],
        'Year'                : [],
        'Average Temperature' : []}

for i in year:
    df2['Continent'].append('World')
    df2['Year'].append(i)
    df2['Average Temperature'].append(df[df.Year == i]['Average Temperature'].mean())

df2 = pd.DataFrame(df2)
df  = pd.concat([df, df2])

fig = px.bar(df,
             x = "Continent",
             y = "Average Temperature",
             color = "Continent",
             animation_frame = "Year",
             range_y=[0 ,30])

del dependencies, largest, df2, year
fig.show()