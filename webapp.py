# imports
import pandas as pd
import numpy as np
import regex as re
from flask import Flask, request, redirect, url_for, render_template
import os


# helper functions
# define function to get the genre(s) of an artist
def isGenre(row, genre):
    '''
    inputs: dataframe column with genre information, genre of interest
    output: dataframe column (or similar) with boolean value for specified genre
    '''
    gen_string = " ".join(str(elem) for elem in row) # joins all the elements of list together into one string
    if gen_string.count(genre.lower()) > 0:
        return True
    else: return False # looks for any instance of the genre in the resulting string

def cleanData(df):
    '''
    function cleans the original pandas dataframe imported from .csv and returns a clean frame
    :param df:
    :return: cleaned pandas dataframe
    '''
    df = df.iloc[: , 1:] # remove uneeded index column
    df['genres'] = df['genres'].replace(["na", '[]'], "['na']")
    df['rel_artists'] = df['rel_artists'].replace(["na", '[]'], "['na']")
    df['genres'] = df['genres'].apply(lambda x:eval(x, {'__builtins__': None}, {}))
    df['rel_artists'] = df['rel_artists'].apply(lambda x: eval(x, {'__builtins__': None}, {}))
    return df

PATH_ = '/home/arolson/concert-finder-webapp'
os.chdir(PATH_)
df = pd.read_csv('DC_Concerts.csv')
df = cleanData(df)


# App creattion
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        genres = request.form['genres'].split(':')
        max_cost = request.form['maxcost']
        days = request.form.getlist('checkboxes')
        x = request.form['x']
        # try and except blocks to force numerics into type int
        try: max_cost = int(max_cost)
        except: max_cost = 100
        try: x = int(x)
        except: x = 10
        # generate search queries based on user input
        cost_query = f'(clean_cost <= {max_cost})'
        day_query = '(' + ' | '.join(f'weekday == "{day}"' for day in days) + ')'
        if len(genres[0]) > 0:
            genre_query = '(' + ' | '.join(f'{gen} == True' for gen in genres) + ')'
            for genre in genres:
                df[genre] = df['genres'].apply(isGenre, args=([genre]))
            queries = [cost_query, day_query, genre_query]
        else:
            genre_query = ''
            queries = [cost_query, day_query]
        query = ' & '.join(queries)
        out = df.query(query)
        out = out.sort_values('clean_date')
        out['date_only'] = pd.to_datetime(out['clean_date']).dt.date
        out['artists'] = out['rel_artists'].apply(lambda x:", ".join(a for a in x))
        out.reset_index(inplace=True, drop=True)

        shows = [ ]
        for index, row in out[0:x].iterrows():
            shows.append({"Artist": row['name'], "Date": row['date_only'], "Venue": row['venue'], "Day of Week": row['weekday'], "Cost": row['cost'], "Related Artists": row['artists']})
        return render_template('main.html',
                                     original_input={'Max Cost': max_cost, 'Max Events to Show': x, 'Days': days, 'Genres': genres},
                                     result=shows,
                                     )
    else:
        return render_template('main.html')

