from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd

def getFPStats(driver, link, playerName):
    driver.execute_script("window.open('');")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.get(link.replace("/players/","/stats/"))

    print(playerName)

    playerPosTeamOuter = driver.execute_script("return arguments[0].innerHTML;",driver.find_element(By.XPATH, "//div[@class = 'pull-left primary-heading-subheading']"))
    playerPosTeam = playerPosTeamOuter[playerPosTeamOuter.index("<h2>")+4:playerPosTeamOuter.index("</h2>")]
    playerPos, playerTeam = playerPosTeam.split(" - ")

    bio = driver.find_element(By.XPATH, "//div[@class = 'bio']")
    innerBio = bio.find_elements(By.XPATH, "//div[@class = 'clearfix']")[1]
    details = innerBio.find_elements(By.XPATH, "//span[@class = 'bio-detail']")

    for detail in details:
        detailText = driver.execute_script("return arguments[0].innerHTML;",detail)
        cat = detailText[detailText.index("<b>")+3:detailText.index("</b>")]

        match cat:
            case "Height":
                height = int(detailText[detailText.index(": ")+2:detailText.index("'")])*12 + int(detailText[detailText.index("' ")+2:].replace("\"",""))
            case "Weight":
                weight = int(detailText[detailText.index(": ")+2:detailText.index(" lbs")])
            case "Age":
                print(detailText)
                age = int(detailText[detailText.index(": ")+2:].replace("\"",""))
            case "College":
                college = detailText[detailText.index(": ")+2:].replace("\"","")

    tables = driver.find_elements(By.XPATH, "//div[@class = 'mobile-table']")
    stats = []
    for table in tables:
        tableText = driver.execute_script("return arguments[0].innerHTML;",table)
        colSpanPost = tableText[tableText.index("colspan=\"")+9:]
        colSpan = int(colSpanPost[:colSpanPost.index("\"")])
        match colSpan:
            case 9:
                tableType = "Receiving"
            case 10:
                tableType = "Rushing"
            case 12:
                tableType = "Passing"
        head = table.find_element(By.XPATH, ".//thead")
        tableColsOuter = head.find_elements(By.XPATH, ".//tr")[1]
        tableColsElems = tableColsOuter.find_elements(By.XPATH, ".//th")
        tableCols = []
        for tableColsElem in tableColsElems:
            name = driver.execute_script("return arguments[0].innerHTML;",tableColsElem).capitalize()
            if name in ("Team","Games"):
                tableCols.append(name)
            elif name != "Season":
                tableCols.append(tableType + " " + name)

        body = table.find_element(By.XPATH, ".//tbody")
        seasons = body.find_elements(By.XPATH, ".//tr")
        data = {}
        for season in seasons:
            count = 0
            elems = season.find_elements(By.XPATH, ".//td")
            seasonData = []
            for elem in elems:
                if not count:
                    season = int(driver.execute_script("return arguments[0].innerHTML;",elem))
                elif count == 1:
                    seasonData.append(driver.execute_script("return arguments[0].innerHTML;",elem))
                else:
                    seasonData.append(float(driver.execute_script("return arguments[0].innerHTML;",elem).replace(",","")))
                count+=1
            data[season] = seasonData
        
        seasonDF = pd.DataFrame.from_dict(data, orient='index', columns=tableCols)
        seasonDF = seasonDF.reset_index().rename(columns={"index":"Season"})
        seasonDF["Name"] = playerName
        seasonDF["Link"] = link
        stats.append(seasonDF)


    totStats = stats[0].merge(stats[1], on=["Season",'Team','Games'], how='left')
    rookieYear = int(totStats["Season"].min())
    yearsInNFL = 2023-rookieYear
    
    print(playerName)
    print(totStats)
    return pd.DataFrame({'Name': playerName,
                           'Link': link,
                           'Position': playerPos,
                           'Rookie Year': rookieYear,
                           'Current Years in NFL': yearsInNFL,
                           'Age': age,
                           'Height (in)': height,
                           'Weight (lbs)': weight,
                           'College': college
                           }), totStats
    




