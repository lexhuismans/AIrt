import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import PoissonRegressor, LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.experimental import enable_hist_gradient_boosting  # noqa
from sklearn.ensemble import HistGradientBoostingRegressor

from sklearn import preprocessing

import get_data as gd

"""
!!TO DO!!
Make separate function for cleaning data. Maybe clean data right after import.
Make separate function for training and saving the result. (pickle)
"""

columns = ['Price', 'Artist', 'Hoogte', 'Breedte', 'Birth', 'Death', 'Ingelijst', 'Area']

def filter_artists():
    """
    Filter to only take subset of artists.
    """
    pass

def filter_words():
    """
    Filter to only take subset of title words.
    """
    pass

def train_on_data(data_path = r'../data/zeefdrukken_data_cleaned.csv'):
    df = pd.read_csv(data_path)
    df['Area'] = df['Hoogte']*df['Breedte']

    df = df[columns].iloc[0:7100,:]
    df['Death'] = df['Death'].fillna(3000)
    df.dropna(inplace = True)

    #-------------------------Preprocessing-------------------------------------
    # Artists
    artist_count = df['Artist'].value_counts()
    high_freq_artist = artist_count[artist_count > 100].index.tolist()
    df = df.loc[df['Artist'].isin(high_freq_artist)]

    # Generate binary values using get_dummies
    dum_df = pd.get_dummies(df['Artist'], columns=['Artist'], prefix=None)
    df.drop(columns = ['Artist'], inplace=True)

    # Title words
    word_list = pd.DataFrame(re.findall(r'\w+', df['Title'].to_string(header=False, index=False)))
    word_count = word_list.value_counts()
    high_freq_words = word_count[word_count>300].index.tolist()

    X = df.iloc[:,1:]
    y = df.iloc[:,0]

    # Add polynomial features
    #polyfeatures = preprocessing.PolynomialFeatures(2)
    #X = polyfeatures.fit_transform(X)

    # Add artists
    X = np.concatenate((X, dum_df), axis=1)
    print('Test shape: \n', X.shape)

    #--------------------------------Training-----------------------------------
    # Split data
    rng = np.random.RandomState(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=rng)

    # Scale data
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    # Train
    glm = PoissonRegressor()
    glm.fit(X_train, y_train)
    print('Poisson Regression: ', glm.score(X_test, y_test))

    #reg = LinearRegression()
    #reg.fit(X_train, y_train)
    #print('Linear Regression: ', reg.score(X_test, y_test))

    reg = MLPRegressor(random_state=1, max_iter=500)
    reg.fit(X_train, y_train)
    print('MLP Regressor: ', reg.score(X_test, y_test) )

    #gbdt = HistGradientBoostingRegressor(loss='poisson', learning_rate=.01)
    #gbdt.fit(X_train, y_train)
    #print(gbdt.score(X_test, y_test))
    return reg, high_freq_artist, scaler

def predict_current_offer():
    """
    Predict the prizes of the current offer.

    !TO DO!
    Now have to machine learn every time.
    Make general place to clean the data.
    """
    reg, artists, scaler = train_on_data()

    # Get current offer
    df = gd.get_current_offer()
    df = df[columns]
    print('Current offer: \n', df[['Artist', 'Price']])

    df = df.loc[df['Artist'].isin(artists)]
    urls = df.index.to_numpy()

    df['Death'] = df['Death'].fillna(3000)
    df.dropna(inplace = True)

    # Add artist columns
    df = df.reindex(columns = df.columns.tolist() + artists)
    for artist in artists:
        df[[artist]] = df['Artist'].eq(artist)

    df.drop(columns = ['Artist'], inplace=True)

    X = df.iloc[:,1:]
    print(X)
    X = scaler.transform(X)
    print(X)
    prediction = reg.predict(X)

    current_vs_predict = np.array([[urls], [df.iloc[:,0]], [prediction]])
    print(current_vs_predict)

if __name__ == '__main__':
    predict_current_offer()
