from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd

def getFPRankings(driver, link,year):
    driver.get(link)
    
    pre2017 = year < 2017
    pre2021 = year < 2021

    if pre2017:
        players = []

        playerTable = driver.find_element(By.XPATH, "//table[@id = 'data']")
        playerBody = playerTable.find_element(By.XPATH, ".//tbody")
        playersRows = playerBody.find_elements(By.XPATH, ".//tr[not(contains(@class,'table-ad'))]")
        for playerRow in playersRows:
            ranks = playerRow.find_elements(By.XPATH, ".//td")
            playerLabel = ranks[1]
            nameInnerHTML = driver.execute_script("return arguments[0].innerHTML;",playerLabel).replace('<div class="pull-left">','')
            link = nameInnerHTML[nameInnerHTML.index("href=\"")+6:nameInnerHTML.index("\">")]
            link = link[link.index("http"):]
            if "full-name" in nameInnerHTML:
                name = driver.execute_script("return arguments[0].innerHTML;",playerLabel.find_element(By.XPATH, ".//span[@class = 'full-name']"))
            else:
                name = nameInnerHTML[nameInnerHTML.index(">")+1:nameInnerHTML.index("</a>")]
            
            print(name)
            rank = float(driver.execute_script("return arguments[0].innerHTML;",ranks[0]))
            ECRvsADPText = driver.execute_script("return arguments[0].innerHTML;",ranks[8])
            ECRvsADP = 0 if ECRvsADPText == "-" or  ECRvsADPText == "" else float(ECRvsADPText)
            adp = rank + ECRvsADP
            players.append({"name":name,"link":link,"rank":rank,"adp":adp})

        return pd.DataFrame.from_dict(players)
    
    elif pre2021:
        players = []

        playersRows = driver.find_elements(By.XPATH, f"//tr[contains(@class,'mpb-player')]")
        for playerRow in playersRows:
            if "player-label sticky-cell sticky-cell-two" in driver.execute_script("return arguments[0].innerHTML;",playerRow):
                playerLabelClass = "player-label sticky-cell sticky-cell-two"
            else:
                playerLabelClass = 'player-label'
            playerLabel = playerRow.find_element(By.XPATH, f".//td[@class = '{playerLabelClass}']")
            nameInnerHTML = driver.execute_script("return arguments[0].innerHTML;",playerLabel)
            link = nameInnerHTML[nameInnerHTML.index("href=\"")+6:nameInnerHTML.index("\">")]
            link = link[link.index("https:"):]
            if "full-name" in nameInnerHTML:
                name = driver.execute_script("return arguments[0].innerHTML;",playerLabel.find_element(By.XPATH, ".//span[@class = 'full-name']"))
            else:
                name = nameInnerHTML[nameInnerHTML.index(">")+1:nameInnerHTML.index("</a>")]
            
            ranks = playerRow.find_elements(By.XPATH, ".//td[@class = 'view-options ranks']")
            rank = float(driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//td")))
            ECRvsADPText = driver.execute_script("return arguments[0].innerHTML;",ranks[5])
            ECRvsADP = 0 if ECRvsADPText == "-" or  ECRvsADPText == "" else float(ECRvsADPText)
            adp = rank + ECRvsADP
            players.append({"name":name,"link":link,"rank":rank,"adp":adp})

        return pd.DataFrame.from_dict(players)

    else:
        players = []

        playersRows = driver.find_elements(By.XPATH, f"//tr[contains(@class,'player-row')]")
        for playerRow in playersRows:
            nameInnerHTML = driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//div[@class = 'player-cell player-cell__td']"))
            name = nameInnerHTML[nameInnerHTML.index(">")+1:nameInnerHTML.index("</a>")]
            link = nameInnerHTML[nameInnerHTML.index("href=\"")+6:nameInnerHTML.index("\">")]
            pre2023 = year < 2023
            
            if pre2023:
                rank = float(driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//td[@class = ' sticky-cell sticky-cell-one']")))
                ECRvsADPText = driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//div[@class = 'ecr-vs-adp-wrap']"))
                ECRvsADP = 0 if ECRvsADPText == "-" or  ECRvsADPText == "" else float(ECRvsADPText)
                adp = rank + ECRvsADP
            else:
                rank = float(driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//td[@class = 'sticky-cell sticky-cell-one']")))
                ECRvsADPText = driver.execute_script("return arguments[0].innerHTML;",playerRow.find_element(By.XPATH, ".//div[@class = 'tooltip-left ecr-vs-adp-wrap']"))
                ECRvsADP = 0 if ECRvsADPText == "-" or  ECRvsADPText == "" else float(ECRvsADPText)
                adp = rank + ECRvsADP

            players.append({"name":name,"link":link,"rank":rank,"adp":adp})

        return pd.DataFrame.from_dict(players)