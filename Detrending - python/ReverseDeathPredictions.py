from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import random
import numpy as np

import sys
from math import log10
import math as m
import copy


CSV_PATH = Path("Data/COVID-19.csv")

c = "Germany"



def get_data(path):
    country_data = []

    data_path = Path.cwd() / path
    data_frame = pd.read_csv(data_path, usecols=[
        "cases", "deaths", "countriesAndTerritories", "dateRep"])
    group = data_frame.groupby("countriesAndTerritories")

    for country, df_country in group:
        cases = df_country["cases"]
        last_index = cases.to_numpy().nonzero()[0][-1] + 1
        df_trimmed = df_country.drop(df_country.index[last_index:])
        df_reversed = df_trimmed.iloc[::-1]
        country_data.append((country, df_reversed))
        
    return country_data


def unpackData(data, country):
    deaths = []
    cases  = []
    casesReached100 = False
    for c, df_country in data:
        if c == country:
            
            for i in range(len(df_country.cases.values)):
                if (not casesReached100):
                    if (df_country.cases.values[i] >= 100):
                        casesReached100 = True
                    else:
                        continue
                cases.append(df_country.cases.values[i])
                deaths.append(df_country.deaths.values[i])

    return deaths, cases



def detrendWeekdays(data):
    averageDay = 0
    model = [1 for i in range(7)]
    numberDatapoints = [0 for i in range(7)]

    for i in range(len(data)):
        averageDay += data[i]
        model[(i % 7)] += data[i]
        numberDatapoints[(i % 7)] +=1
    

    averageDay /= len(data)

    for i in range(7):
        model[i] = model[i] / numberDatapoints[i]
        model[i] =  averageDay / model[i]

    for i in range(len(data)):
        data[i] = data[i] * model[(i % 7)]

    return model, data



def removeTrendFromData(x,y):
    for i in range(len(x)):
        x[i] = x[i] - y[i]
    return x

def detrendByDifferencing(data):
    newData = [0 for i in range(len(data)-1)]
    for i in range(len(data)-1):
        newData[i] = data[i+1] - data[i]
    return newData


def main():


    data = get_data(CSV_PATH)


    f = open("detrendedDataAllCountries", "w")


    deaths, cases = unpackData(data, c)

    
    #plt.plot(cases, label = 'new infections')
    #plt.plot(deaths, label = 'deaths') 
    #plt.legend()
    #plt.xlabel("days since outbreak")
    #plt.ylabel("n")
    #plt.title("Official corona counts in " + c)

    #plt.show()

    #input()

    if (detrendOneCountry(deaths, cases, c, f)):
        pass



def confirm():
    x = input()
    if (x != ''):
        return False
    return True    


def detrendOneCountry(deaths, cases, c, f):

    originalDeaths = copy.deepcopy(deaths)


    #US
    #predictionsDeaths = [0.74548, 0.92713,0.93387,-0.75647, 0.17406, -0.67132, -0.60001 ]

    #Netherlands
    #predictionsDeaths = [-0.24860, 0.45175, -0.00387, -0.14417, -0.04351, -0.23001, -0.80216]

    #Germany
    predictionsDeaths = [-0.36001, -0.36102, -0.36437,-0.35062, -0.29802, -0.33310, -0.35482]



    for i in range(len(predictionsDeaths)):
        predictionsDeaths[i] = predictionsDeaths[i]**3

    predictionsDeaths[0] =  predictionsDeaths[0] + deaths[-8]
    
    for i in range(1,7):
        predictionsDeaths[i] = predictionsDeaths[i-1] + predictionsDeaths[i]


    predictionsDeaths.insert(0, originalDeaths[-8])


    t1 = [x for x in range(len(cases) -30, len(cases))]
    t2 = [len(cases)-8 + x for x in range(8)]

    plt.plot(t1, originalDeaths[-30:], label = 'real data') 
    plt.plot(t2, predictionsDeaths, label = 'mlp death predictions')
    plt.legend()
    plt.xlabel("days since outbreak")
    plt.ylabel("number of new deaths")
    plt.title("Mlp predictions for deaths in  " + c)

    plt.show()


    input()

    #detrend by differencing
    deaths = detrendByDifferencing(deaths)
    cases = detrendByDifferencing(cases)


    #Normalize data
    for i in range(len(cases)):

        if (deaths[i] > 0):
            deaths[i] = m.pow(deaths[i],float(1)/3)
        else:
            deaths[i] = m.pow(abs(deaths[i]),float(1)/3) * -1

        if (cases[i] > 0):
            cases[i] = m.pow(cases[i],float(1)/3)
        else:
            cases[i] = m.pow(abs(cases[i]),float(1)/3) * -1

    print(cases)


    f.write(c + " " + str(len(cases)) + "\n")

    for i in range(len(cases)):
        f.write(str(deaths[i]) + " " + str(cases[i])+ "\n")

    print("Data is used")
    return True


if __name__ == "__main__":
    main()
