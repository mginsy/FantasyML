from getFPStats import getFPStats
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd

options = Options()
#options.add_argument("-headless") 
driver = webdriver.Firefox(options=options)

statYears = ["2014","2015","2016","2017","2018","2019","2020","2021","2022"]
playersObtained = set({})

statYearsDFs = {}

playerDataDF = pd.DataFrame({'Name': pd.Series(dtype='str'),
                           'Link': pd.Series(dtype='str'),
                           'Position': pd.Series(dtype='str'),
                           'Rookie Year': pd.Series(dtype='int'),
                           'Current Years in NFL': pd.Series(dtype='int'),
                           'Age': pd.Series(dtype='int'),
                           'Height (in)': pd.Series(dtype='int'),
                           'Weight (lbs)': pd.Series(dtype='int'),
                           'College': pd.Series(dtype='str')
                           })

for year in statYears:
    statYearsDFs[year] = pd.DataFrame({'Name': pd.Series(dtype='str'),
                                       'Link': pd.Series(dtype='str'),
                                       'Team': pd.Series(dtype='str'),
                                       'Games': pd.Series(dtype='int'),
                                       'Passing Qb Rat': pd.Series(dtype='float'),
                                       'Passing Cmp': pd.Series(dtype='int'),
                                       'Passing Att': pd.Series(dtype='int'),
                                       'Passing Pct': pd.Series(dtype='float'),
                                       'Passing Yds': pd.Series(dtype='int'),
                                       'Passing Y/a': pd.Series(dtype='float'),
                                       'Passing Td': pd.Series(dtype='int'),
                                       'Passing Int': pd.Series(dtype='int'),
                                       'Passing Sacks': pd.Series(dtype='int'),
                                       'Rushing Att': pd.Series(dtype='int'),
                                       'Rushing Yds': pd.Series(dtype='int'),
                                       'Rushing Y/a': pd.Series(dtype='float'),
                                       'Rushing Lg': pd.Series(dtype='int'),
                                       'Rushing Td': pd.Series(dtype='int'),
                                       'Rushing Fum': pd.Series(dtype='int'),
                                       'Rushing Fuml': pd.Series(dtype='int'),
                                       'Receiving Rec': pd.Series(dtype='str'),
                                       'Receiving Tgt': pd.Series(dtype='str'),
                                       'Receiving Yds': pd.Series(dtype='str'),
                                       'Receiving Y/r': pd.Series(dtype='str'),
                                       'Receiving Lg': pd.Series(dtype='str'),
                                       'Receiving Td': pd.Series(dtype='str')})
    

for year in statYears:
    FPDF = pd.read_excel(f"FPDF{year}.xlsx")

    for index, row in FPDF.iterrows():
        if row["link"] not in playersObtained:
            print(row["name"])
            playerData, playerStats = getFPStats(driver, row["link"], row["name"])

            playerDataDF = pd.concat([playerDataDF, playerData], ignore_index=True, sort=False)

            for PSindex, PSrow in playerStats.itterrows():
                statYearsDFs[PSrow["Season"]] = pd.concat([statYearsDFs[PSrow["Season"]], PSrow.drop('Season', axis=1)], ignore_index=True, sort=False)

            
            
            playersObtained.add(row["link"])

        print(playerDataDF)
        print(statYearsDFs)





#get position and team. DONE
#get full NFL stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb
#get college stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb
#rookie year / how many years in NFL
#link with other players on team
#get oline ranking and historical oline rankings
#get HC and OC
#get defense ranking
#FP ranking. DONE