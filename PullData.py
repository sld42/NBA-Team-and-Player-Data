import urllib
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

url_blank='http://www.basketball-reference.com/leagues/NBA_{i}_per_game.html#per_game::none'
total_df=pd.DataFrame()
for i in range(1990,2017):
    url = url_blank.format(i=i)    
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'lxml')
    #Get stat categories
    column_headers = [th.getText() for th in 
                      soup.findAll('tr', limit=1)[0].findAll('th')]
    #grab data                  
    data_rows = soup.findAll('tr')[1:]
    player_data = [[td.getText() for td in data_rows[row].findAll('td')]
                for row in range(len(data_rows))]
    df = pd.DataFrame(player_data, columns=column_headers)
    
    #Get rid of null rows
    df=df[df['Player'].notnull()]
    #Get rid of NaNs
    df = df[:].fillna(0)
    #Format so % symbol isnt in columns
    df.columns = df.columns.str.replace('%', '_Perc')
    #Change datatype so everything isnt an object
    df = df.convert_objects(convert_numeric=True)
    #Get rid of multiple rows for players that were traded in a season
#    df=df.drop_duplicates('Rk')
    #Get rid of the total row for traded players
    df=df[df.Tm != 'TOT' ]
    df=df[df.Pos != 'G']
    df=df[df.Pos != 'F'] 
    df=df[df.Pos != 'G-F']
    df.insert(0, 'year', i)
    total_df=total_df.append(df,ignore_index=True)
#positions=list(np.unique(total_df['Pos']))
#Get rid of replacement no longer needed
#replacement=['C', 'C', 'SF', 'SF', 'SF', 'PF', 'PF', 'PF', 'PG',
#       'PG', 'PG', 'SF', 'SF', 'SF', 'SG', 'SG', 'SG', 'SG']
#total_df=total_df.replace(positions, replacement)    

url_blank='http://www.basketball-reference.com/leagues/NBA_{i}_advanced.html'
adv_df=pd.DataFrame()
for i in range(1990,2017):
    url = url_blank.format(i=i)    
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'lxml')
    #Get stat categories
    column_headers = [th.getText() for th in 
                      soup.findAll('tr', limit=1)[0].findAll('th')]
    #grab data                  
    data_rows = soup.findAll('tr')[1:]
    player_data = [[td.getText() for td in data_rows[row].findAll('td')]
                for row in range(len(data_rows))]
    df = pd.DataFrame(player_data, columns=column_headers)
    
    #Get rid of null rows
    df=df[df['Player'].notnull()]
    #Get rid of NaNs
    df = df[:].fillna(0)
    #Format so % symbol isnt in columns
    df.columns = df.columns.str.replace('%', '_Perc')
    #Change datatype so everything isnt an object
    df = df.convert_objects(convert_numeric=True)
    #Get rid of multiple rows for players that were traded in a season
#    df=df.drop_duplicates('Rk')
    df=df[df.Tm != 'TOT' ]
    df=df[df.Pos != 'G']
    df=df[df.Pos != 'F'] 
    df=df[df.Pos != 'G-F']
    df=df.drop(df.columns[[19,24]], axis=1)
    df=df.ix[:,'PER':]
    adv_df=adv_df.append(df,ignore_index=True)
total_df=pd.concat([total_df, adv_df], axis=1)
#Replace team identifier for the new Charlotte Hornets with the old identifier        
total_df=total_df.replace('CHO','CHH')
total_df.to_csv("1990-2016 player data.csv")

url_blank='http://www.basketball-reference.com/leagues/NBA_{i}.html#team::none'
team_df=pd.DataFrame()
for i in range(1990,2017):
    url = url_blank.format(i=i)    
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'lxml')
    if i==1990:
    #Get stat categories
        tables = soup.find_all("thead")
        rightTableheader=tables[2].find_all('th')
        column_headers=[th.getText() for th in rightTableheader]
    #grab data
    tables = soup.find_all("tbody")
    rightTabledata=tables[2].find_all('tr')
    #For some reason the 2016 season webpage is different from all other years
    if i==2016:
        rightTabledata=tables[4].find_all('tr')
    data=[[td.getText() for td in rightTabledata[row].findAll('td')]
                for row in range(len(rightTabledata))]

    df = pd.DataFrame(data, columns=column_headers)
    #insert playoff appearance data
    df.insert(1, 'Playoff', df['Team'].str.contains('\*'))
    
    #Get rid of null rows
    df=df[df['Team'].notnull()]
    #Get rid of NaNs
    df = df[:].fillna(0)
    #insert year data
    df.insert(0, 'year', i)
    #Format so % symbol isnt in columns
    df.columns = df.columns.str.replace('%', '_Perc')
    #Change datatype so everything isnt an object
    df = df.convert_objects(convert_numeric=True)
    team_df=team_df.append(df,ignore_index=True)
    old_names=list(np.unique(team_df['Team']))
    new_names=['',]
 
#Remove * for playoff teams
all_names=list(np.unique(team_df['Team']))
no_ast=list(np.unique(team_df['Team']))
ast=[]
for i in range(0,len(all_names)):
    if re.search('.*\*',all_names[i]) != None:
        ast.append(all_names[i])
        no_ast.remove(re.search('.*\*',all_names[i]).group(0)) 
no_ast.remove('League Average')
no_ast.remove('Vancouver Grizzlies')
team_df=team_df.replace(ast, no_ast) 
team_df=team_df.replace('New Orleans/Oklahoma City Hornets','New Orleans Hornets')    
#Replace long team names with abbreviations   
full_name=list(np.unique(team_df['Team']))
full_name.remove('League Average')
abrv=list(np.unique(total_df['Tm']))
abrv.remove('NOK')
team_df=team_df.replace(full_name, abrv)  
team_df.to_csv("1990-2016 team data.csv")
