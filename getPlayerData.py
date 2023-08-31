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
import numpy as np

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
                           'Age': pd.Series(dtype='int'),
                           'Height (in)': pd.Series(dtype='int'),
                           'Weight (lbs)': pd.Series(dtype='int'),
                           'College': pd.Series(dtype='str')
                           })

for year in statYears:
    statYearsDFs[year] = pd.DataFrame({'Name': pd.Series(dtype='str'),
                                       'Link': pd.Series(dtype='str'),
                                       'Position': pd.Series(dtype='str'),
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
    

perGameStats = ['Passing Cmp','Passing Att','Passing Yds','Passing Td','Passing Int','Passing Sacks','Rushing Att','Rushing Yds','Rushing Td','Rushing Fum','Rushing Fuml','Receiving Rec','Receiving Tgt','Receiving Yds','Receiving Td']
errorPlayers = []

for year in statYears:
    FPDF = pd.read_excel(f"FPDF{year}.xlsx")

    for index, row in FPDF.iterrows():
        if row["link"] not in playersObtained and "/teams/" not in row["link"]:  
            print(row["name"])
            try:
                playerData, playerStats = getFPStats(driver, row["link"], row["name"])

                if playerData.empty and playerStats.empty:
                    playersObtained.add(row["link"])
                else:
                    playerDataDF = pd.concat([playerDataDF, playerData], ignore_index=True, sort=False)

                    for PSindex, PSrow in playerStats.iterrows():
                        if int(PSrow["Season"]) >= 2014:
                            statYearsDFs[str(PSrow["Season"])] = pd.concat([statYearsDFs[str(PSrow["Season"])], PSrow.drop(labels=['Season']).to_frame().T], ignore_index=True, sort=False)   
                    
                    playersObtained.add(row["link"])
            except Exception as e:
                print(e)
                errorPlayers.append(row["link"])
                time.sleep(1)
    
    for perGameStat in perGameStats:
        try:
            statYearsDFs[year][perGameStat + " Per Game"] = statYearsDFs[year][perGameStat]/statYearsDFs[year]["Games"]
        except ZeroDivisionError:
            statYearsDFs[year][perGameStat + " Per Game"] = 0
        
    statYearsDFs[year]["yearlyFP"] = statYearsDFs[year]["Passing Yds"]*.04 + statYearsDFs[year]["Passing Td"]*4 + statYearsDFs[year]["Passing Int"]*-2 + statYearsDFs[year]["Rushing Yds"]*.1 + statYearsDFs[year]["Rushing Td"]*6 + statYearsDFs[year]["Rushing Fuml"]*-2 + statYearsDFs[year]["Receiving Rec"]*.5 + statYearsDFs[year]["Receiving Yds"]*.1 + statYearsDFs[year]["Receiving Td"]*6
    
    avgTop10QB = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "QB"].nlargest(10, "yearlyFP")["yearlyFP"].sum()/10
    avgTop35RB = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "RB"].nlargest(35, "yearlyFP")["yearlyFP"].sum()/35 #35 to account for flex
    avgTop35WR = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "WR"].nlargest(35, "yearlyFP")["yearlyFP"].sum()/35
    avgTop10TE = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "TE"].nlargest(10, "yearlyFP")["yearlyFP"].sum()/10
                                     
    statYearsDFs[year]['FPAR'] = np.where(statYearsDFs[year]['Position'] == "QB", statYearsDFs[year]["yearlyFP"]-avgTop10QB, 
                                          np.where(statYearsDFs[year]['Position'] == "RB", statYearsDFs[year]["yearlyFP"]-avgTop35RB, 
                                          np.where(statYearsDFs[year]['Position'] == "WR", statYearsDFs[year]["yearlyFP"]-avgTop35WR, 
                                          np.where(statYearsDFs[year]['Position'] == "TE", statYearsDFs[year]["yearlyFP"]-avgTop10TE))))

    statYearsDFs[year].to_excel(f"PlayerStats{year}.xlsx",index=False)

    
playerDataDF.to_excel(f"PlayerData.xlsx",index=False)

print(errorPlayers)




#get position and team. DONE
#get full NFL stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb. DONE
#get college stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb. get conference too
#rookie year / how many years in NFL. DONE
#link with other players on team. get historical depth charts.
#get oline ranking and historical oline rankings
#get HC and OC
#get defense ranking
#FP ranking. DONE