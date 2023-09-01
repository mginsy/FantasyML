from getPlayerRankingsFantasyPros import getFPRankings
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd

driver = webdriver.Firefox()

years = {
         #"2014": 'https://web.archive.org/web/20140825162908/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2015": 'https://web.archive.org/web/20150827071021/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2016": 'https://web.archive.org/web/20160708123616/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2017": 'https://web.archive.org/web/20170830083527/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2018": 'https://web.archive.org/web/20180830131437/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2019": 'https://web.archive.org/web/20190729082622/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2020": 'https://web.archive.org/web/20200827033122/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2021": 'https://web.archive.org/web/20210831053826/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php', #have to load whole page for this one
         #"2022": 'https://web.archive.org/web/20220830113943/https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
         #"2023": 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php'
         }

for year in years:
    link = years[year]
    FPDF = getFPRankings(driver, link, int(year))
    print(FPDF)
    FPDF.to_excel(f"FantasyRankings/FPDF{str(year)}.xlsx",index=False)

driver.close()

#get position and team. DONE
#get full NFL stats. extrapolate per game stats and fantasy points. rushing and rec for wr/rb/te. rushing and passing for qb
#get college stats. extrapolate per game stats and fantasy points. rushing and rec for wr/rb/te. rushing and passing for qb
#rookie year / how many years in NFL
#link with other players on team
#get oline ranking and historical oline rankings
#get HC and OC
#get defense ranking
#FP ranking. DONE