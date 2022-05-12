from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

"""
Kit de commandes:
va à une fenetre
    -driver.switch_to.window(driver.window_handles[numDeLaFenetre])
ouvre une fenetre
    -driver.execute_script("window.open('');")
ouvrir un lien
    -driver.get(link)
"""

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response
latence=0.5

def ouvrirGoFluent(Id,Mdp):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=8000")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=caps)     #options.add_argument("--headless")
    driver.maximize_window()
    driver.get("https://leonard-de-vinci.net/")
    time.sleep(latence)

    driver.find_element(By.NAME,("login")).send_keys(Id)     #entrer adresse e-mail

    wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Suivant']"))).click()  #appuyer sur connection
    time.sleep(latence)

    driver.find_element(By.NAME,("Password")).send_keys(Mdp)
    wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Connexion']"))).click()
    driver.get("https://www.leonard-de-vinci.net/langues/gofluent")
    return(driver)

#récupère les liens de chaque page dispo dans le code directement
def ensLinks(driver):
    time.sleep(3)
    l=[]
    Llinks=[]
    liste = driver.find_elements(By.CSS_SELECTOR, ".slider__slide div[role=link]")
    for i in liste:    
        link=i.get_attribute("href")
        if "training-path" in link:
            code=link.split("/")[-1]
            l+=[code]
    for i in range(len(l)):
        driver.get("https://portal.gofluent.com/app/dashboard/training-path/"+l[i])
        time.sleep(2)
        liste = driver.find_elements(By.CSS_SELECTOR, ".resource-link[role=link]")
#        time.sleep()
        for j in liste:
            link=j.get_attribute("href")
            Llinks+=["https://portal.gofluent.com"+link+"/practice"]
            #driver.execute_script("window.open('');")
            #driver.switch_to.window(driver.window_handles[1+len(Llinks)])
    return(Llinks)
    


    return(Llinks)

def reponseDuLog(driver):
    driver.refresh()
    time.sleep(3)
    rep=[]
    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.request' in event['method'] and "request" in event["params"] and "url" in event["params"]["request"] and "/ws/quiz" in event["params"]["request"]["url"]]
    save=(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[0]["params"]["requestId"]})["body"])
    save.replace("true","True")
    for j in range (len(json.loads(save)["q"])):
        rep+=[json.loads(save)["q"][j]["ans"]]
    return(rep)

def cleanList(driver,Llinks):
    rep=[]
    for i in Llinks:
        driver.get(i)
        rep+=[reponseDuLog(driver)]
    for i in range (len(rep)):
        for j in range (len(rep[i])):
            if (type(rep[i][j])==list):
                if (len(rep[i][j])==1):
                    rep[i][j]=rep[i][j][0]
            if(type(rep[i][j])==list):
                if(type(rep[i][j][0])==dict):
                    for g in range(len(rep[i][j])):
                            rep[i][j][g]=rep[i][j][g]["ans"]
            if (type(rep[i][j])==dict):
                rep[i][j]=rep[i][j]["ans"]
            if (type(rep[i][j])==list and len(rep[i][j])==1):
                rep[i][j]=rep[i][j][0]
    return(rep)

def appuyerRestart(driver):
    time.sleep(3)
    if (len(driver.find_elements(By.CLASS_NAME, ("QuizResults__actions")))==1):
        wait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='RECOMMENCER LE QUIZ']"))).click()
    return(+len (driver.find_elements(By.CLASS_NAME, ("QuizProgressLine__item")))-len (driver.find_elements(By.CLASS_NAME, ("QuizProgressLine__item_answered_wrong")))-len (driver.find_elements(By.CLASS_NAME, ("QuizProgressLine__item_answered_correct"))))

def repondre(ans2,driver):
    print (ans2)
    time.sleep(0.2)
    for i in range(len(ans2)):
        rep=[]
        if(isinstance(ans2[i], int)):
            clicklist1 (driver,ans2[i])
        if(isinstance(ans2[i], str)):
            if(ans2[i][0].isnumeric()):
                clickmot(driver,ans2[i])
            elif(len(driver.find_elements(By.CLASS_NAME, ("ScrambledLettersOption")))>0):
                clickletter(driver,ans2[i])
            else:
                if (len(driver.find_elements(By.XPATH, "//input[@class='Stem__answer_non-arabic']"))==0):
                    eleminput=driver.find_element(By.XPATH, "//textarea[@class='Stem__answer_non-arabic']")
                else:
                    eleminput=driver.find_element(By.XPATH, "//input[@class='Stem__answer_non-arabic']")
                eleminput.send_keys(ans2[i])
        if(type(ans2[i])==list):
            if (isinstance(ans2[i][0], int)):
                clicklist2(driver,ans2[i])
            else:
                lereste(driver,ans2[i])
        driver.find_element(By.CLASS_NAME, ("sc-bdfBQB")).click()
        time.sleep(0.5)
        driver.find_element(By.CLASS_NAME, ("sc-bdfBQB")).click()

def repRestantes(ans,n,nbNF):
    ans2=[]
    for i in range(len(ans[n])):
        if ((len(ans[n])-i)<=nbNF):
            ans2+=[ans[n][i]]
    return(ans2)

def clicklist1 (driver,Lliste):
    elembut=driver.find_elements(By.CLASS_NAME, ("Question__fill-button"))
    if (len(elembut)==0):
        elembut=driver.find_elements(By.CLASS_NAME, ("Question__option"))
    elembut[Lliste-1].click()

def clicklist2 (driver,Lliste):
    elembut=driver.find_elements(By.CLASS_NAME, ("Question__fill-button"))
    if (len(elembut)==0):
        elembut=driver.find_elements(By.CLASS_NAME, ("Question__option"))
    for j in Lliste:
        elembut[j-1].click()

def clickmot(driver,Lliste):
    Lliste = Lliste.replace(" ", "")
    elembut=driver.find_elements(By.CLASS_NAME,("Question__fill-button "))
    if (len(elembut)==0):
        elembut=driver.find_elements(By.CLASS_NAME,("ScrambledSentenceOption"))
    liste=list(Lliste)
    for g in range(0,len(liste),2):
        elembut[int(liste[g])-1].click()

def clickletter(driver,Lliste):
    if(len(driver.find_elements(By.XPATH, "//textarea"))==0):
        liste=list(Lliste)
        for i in range(len(liste)):
            elembut=driver.find_elements(By.CLASS_NAME, ("ScrambledLettersOption"))
            elementclicked=driver.find_elements(By.CSS_SELECTOR, ("div .Question_type_scrambled-letters__selected-box .ScrambledLettersOption"))
            time.sleep(2)
            click=0
            num=0
            while (click==0):
                if(elembut[num].text==liste[i].upper()):       
        #            if (count==0):
                    val=0
                    for j in elementclicked:
                        if (elembut[num]==j):
                            val+=1
                    if(val==0):
                        elembut[num].click()
                        click=1
                num+=1
    else:
        lereste(driver,Lliste)

def lereste(driver,Lliste):
    eleminput=driver.find_elements(By.XPATH, "//input[@class='Stem__answer_non-arabic']")
    if (len(eleminput)==0):
        eleminput=driver.find_element(By.XPATH, "//textarea[@class='Stem__answer_non-arabic']")
        if(type(Lliste)==list):
            eleminput.send_keys(Lliste[0])
        else:
            eleminput.send_keys(Lliste)
    else:
        for j in range(len(eleminput)):
            eleminput[j].send_keys(Lliste[j])

def close(driver):
    time.sleep(5)
    driver.close()

def programme(i):
    driver=ouvrirGoFluent(Id[i],Mdp[i])
    Llinks=ensLinks(driver)
    ans=cleanList(driver,Llinks)
    for n in range(len(Llinks)):
        driver.get(Llinks[n])
        time.sleep(2)
        if ((len(driver.find_elements(By.CLASS_NAME, ("QuizResults__value")))!=2) or (len(driver.find_elements(By.CLASS_NAME, ("QuizProgressLine__item_answered_wrong")))>0)):
            nbNF=appuyerRestart(driver)
            ans2=repRestantes(ans,n,nbNF)   
            if (nbNF<len(ans[n])):
                repondre(ans2,driver)
                time.sleep(2)
                nbNF=appuyerRestart(driver)
                driver.get(Llinks[n])
                ans2=repRestantes(ans,n,nbNF)
            repondre(ans2,driver)
    close(driver)

Id=[]
Mdp=[]

i=0
a=0
def gofluent(elem):
    for i in range(len(Id)):
        programme(i)
    


while i<10:
    try:
        gofluent()
        break
    except:
        i+=1
        print(f"{i} | crash du programme, relancement")
