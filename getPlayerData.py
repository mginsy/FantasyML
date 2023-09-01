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

fullStatYears = ["2014",
             "2015",
             "2016",
             "2017",
             "2018",
             "2019",
             "2020",
             "2021",
             "2022"]

currentStatYears = [#"2014",
             #"2015",
             #"2016",
             "2017",
             "2018",
             "2019",
             "2020",
             "2021",
             "2022"]

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

for year in fullStatYears:
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

playerDataDF = pd.read_excel("tempStats/tempPlayerData.xlsx")

for year in fullStatYears:
    statYearsDFs[year] = pd.read_excel(f"tempStats/tempPlayerStats{year}.xlsx")
    
allLinks = pd.Series(statYearsDFs[min(currentStatYears)]["Link"])

for year in currentStatYears:
    if year != min(currentStatYears):
        allLinks = pd.concat([allLinks, statYearsDFs[year]["Link"]], ignore_index=True)
allLinks = list(pd.concat([allLinks, playerDataDF["Link"]], ignore_index=True).unique())
playersNoQ = [player.replace("?type=overall&amp;scoring=HALF&amp;week=draft","") for player in allLinks]
playersObtained = set(allLinks + playersNoQ)


perGameStats = ['Passing Cmp','Passing Att','Passing Yds','Passing Td','Passing Int','Passing Sacks','Rushing Att','Rushing Yds','Rushing Td','Rushing Fum','Rushing Fuml','Receiving Rec','Receiving Tgt','Receiving Yds','Receiving Td']
errorPlayers = []
kickerLinks = pd.read_excel("tempStats/kickerLinks.xlsx")

for year in currentStatYears:
    print(year)
    FPDF = pd.read_excel(f"FantasyRankings/FPDF{year}.xlsx").head(300)

    for index, row in FPDF.iterrows():
        if row["link"] not in playersObtained and row["link"] not in kickerLinks["Links"] and "/teams/" not in row["link"]:  
            print(row["name"])
            try:
                playerData, playerStats = getFPStats(driver, row["link"], row["name"])

                if playerData.empty and playerStats.empty:
                    playersObtained.add(row["link"])
                    kickerLinks["Links"].append(pd.Series([row["link"]]))
                else:
                    playerDataDF = pd.concat([playerDataDF, playerData], ignore_index=True, sort=False)

                    for PSindex, PSrow in playerStats.iterrows():
                        if int(PSrow["Season"]) >= 2014:
                            statYearsDFs[str(PSrow["Season"])] = pd.concat([statYearsDFs[str(PSrow["Season"])], PSrow.drop(labels=['Season']).to_frame().T], ignore_index=True, sort=False)   
                    
                    playersObtained.add(row["link"])

                    playerDataDF.to_excel(f"tempStats/tempPlayerData.xlsx",index=False)
                    kickerLinks.to_excel("tempStats/kickerLinks.xlsx",index=False)
                    for year2 in currentStatYears:
                        if year2 >= year:
                            statYearsDFs[year2].to_excel(f"tempStats/tempPlayerStats{year2}.xlsx",index=False)
            except Exception as e:
                print("ERROR: " + str(e))
                errorPlayers.append(row["link"])
                time.sleep(1)
    
    for perGameStat in perGameStats:
        try:
            statYearsDFs[year][perGameStat + " Per Game"] = statYearsDFs[year][perGameStat]/statYearsDFs[year]["Games"]
        except ZeroDivisionError:
            statYearsDFs[year][perGameStat + " Per Game"] = 0
        
    
    statYearsDFs[year] = statYearsDFs[year].infer_objects()
    statYearsDFs[year] = statYearsDFs[year].fillna(0)
    statYearsDFs[year]["yearlyFP"] = statYearsDFs[year]["Passing Yds"]*.04 + statYearsDFs[year]["Passing Td"]*4 + statYearsDFs[year]["Passing Int"]*-2 + statYearsDFs[year]["Rushing Yds"]*.1 + statYearsDFs[year]["Rushing Td"]*6 + statYearsDFs[year]["Rushing Fuml"]*-2 + statYearsDFs[year]["Receiving Rec"]*.5 + statYearsDFs[year]["Receiving Yds"]*.1 + statYearsDFs[year]["Receiving Td"]*6
    try:
        statYearsDFs[year]["FP/g"] = statYearsDFs[year]["yearlyFP"] / statYearsDFs[year]["Games"]
    except ZeroDivisionError:
        statYearsDFs[year]["FP/g"] = 0
    
    

    avgWaiverQB = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "QB"].nlargest(17, "yearlyFP")["yearlyFP"].tail(5).sum()/5 #defined as QB 12-17
    avgWaiverRB = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "RB"].nlargest(50, "yearlyFP")["yearlyFP"].tail(10).sum()/10 #defined as RB 40-50
    avgWaiverWR = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "WR"].nlargest(50, "yearlyFP")["yearlyFP"].tail(10).sum()/10 #defined as WR 40-50
    avgWaiverTE = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "TE"].nlargest(17, "yearlyFP")["yearlyFP"].tail(5).sum()/5 #defined as TE 12-17

    avgWaiverQBpg = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "QB"].nlargest(17, "FP/g")["FP/g"].tail(5).sum()/5
    avgWaiverRBpg = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "RB"].nlargest(50, "FP/g")["FP/g"].tail(10).sum()/10
    avgWaiverWRpg = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "WR"].nlargest(50, "FP/g")["FP/g"].tail(10).sum()/10
    avgWaiverTEpg = statYearsDFs[year].loc[statYearsDFs[year]['Position'] == "TE"].nlargest(17, "FP/g")["FP/g"].tail(5).sum()/5
                                     
    statYearsDFs[year]['FPAR'] = np.where(statYearsDFs[year]['Position'] == "QB", statYearsDFs[year]["yearlyFP"]-avgWaiverQB, 
                                          np.where(statYearsDFs[year]['Position'] == "RB", statYearsDFs[year]["yearlyFP"]-avgWaiverRB, 
                                          np.where(statYearsDFs[year]['Position'] == "WR", statYearsDFs[year]["yearlyFP"]-avgWaiverWR, 
                                          np.where(statYearsDFs[year]['Position'] == "TE", statYearsDFs[year]["yearlyFP"]-avgWaiverTE, 0))))
    
    statYearsDFs[year]['FPPGAR'] = np.where(statYearsDFs[year]['Position'] == "QB", statYearsDFs[year]["FP/g"]-avgWaiverQBpg, 
                                          np.where(statYearsDFs[year]['Position'] == "RB", statYearsDFs[year]["FP/g"]-avgWaiverRBpg, 
                                          np.where(statYearsDFs[year]['Position'] == "WR", statYearsDFs[year]["FP/g"]-avgWaiverWRpg, 
                                          np.where(statYearsDFs[year]['Position'] == "TE", statYearsDFs[year]["FP/g"]-avgWaiverTEpg, 0))))

    for year in currentStatYears:
        statYearsDFs[year].to_excel(f"PlayerStats/PlayerStats{year}.xlsx",index=False)

    
playerDataDF.to_excel(f"PlayerData/PlayerData.xlsx",index=False)

print(errorPlayers)

driver.close()




#get position and team. DONE
#get full NFL stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb. DONE
#get college stats. extrapolate per game avg stats and fantasy points. also get fantasy points against mean (WAR type). rushing and rec for wr/rb/te. rushing and passing for qb. get conference too
#rookie year / how many years in NFL. DONE
#link with other players on team. get historical depth charts.
#get oline ranking and historical oline rankings
#get HC and OC
#get defense ranking
#FP ranking. DONE