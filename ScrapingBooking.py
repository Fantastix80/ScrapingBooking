from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd


def scrapeData(lien, ville, nbrHotelARecup, nbrCommentairesMaxParHotel):
    # On vient initialiser la liste de résultat
    data = []

    # On vient rentrer l'URL du site à scraper
    driver.get(lien)

    # On vient fermer la page des cookies
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
    except:
        print("Il n'y avait pas de cookies à accepter")
        pass

    # On vient fermer la popup qui demande de rentrer des dates précises
    x = 5
    y = 5

    # On utilise un scrit javascript afin de pouvoir cliquer à des coordonnées précises de la page 
    script = f"var element = document.elementFromPoint({x}, {y}); element.click();"
    driver.execute_script(script)

    # On vient fermer la popup qui nous demande de nous connecter à un compte afin de bénéficier de réductions
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@aria-label='Ignorer les infos relatives à la connexion']"))).click()
    except:
        print("Il n'y avait pas de popup de connexion à un compte à fermer")
        pass

    # On vient trier les résultats par ceux ayant le plus d'avis postitif
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='sorters-dropdown-trigger']"))).click()
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-id='bayesian_review_score']"))).click()


    # On vient récupérer tous les résultats de la page
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='a78ca197d0']")))

    sleep(1)

    links = driver.find_elements(By.XPATH, "//a[@class='a78ca197d0']")

    # On vient vérifier que le nombre d'hotel à récupérer n'est pas supérieur au nombre d'hotels présents
    # Sinon on met le nombre d'hotels à récupérer au nombre d'hotels présents
    if nbrHotelARecup > len(links):
        nbrHotelARecup = len(links)
        print(f"Il n'y a pas autant d'hotels à scraper: {nbrHotelARecup} hotels trouvés")

    for index in range(nbrHotelARecup):
        # On re-récupère la liste des éléments à cliquer une fois revenue sur la page principale
        links = driver.find_elements(By.XPATH, "//a[@class='a78ca197d0']")

        # On vient scroller jusqu'à l'élément sur lequel on veut cliquer
        actions.move_to_element(links[index]).perform()

        links[index].click()

        # On vient se mettre sur l'onglet que l'on vient d'ouvrir
        driver.switch_to.window(driver.window_handles[1])

        hotelName = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//h2[@class='d2fee87262 pp-header__title']"))).text

        # On clique sur "voir tous les commentaires" s'il y en a un
        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='read-all-actionable']"))).click()

            for index in range(int(nbrCommentairesMaxParHotel/10)):
                # On vérifie que l'élément contenant les commentaires sont bien visibles
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//ul[@class='review_list']//li[@class='review_list_new_item_block']")))

                # On récupère la liste des conteneurs des commentaires
                listeCommentaires = driver.find_elements(By.XPATH, "//ul[@class='review_list']//li[@class='review_list_new_item_block']")

                for idx, commentaire in enumerate(listeCommentaires):
                    try:
                        print(idx, commentaire.find_element(By.XPATH, ".//span[@class='bui-avatar-block__title']").text)
                        # Récupérer le nom
                        auteur = commentaire.find_element(By.XPATH, ".//span[@class='bui-avatar-block__title']").text
                        # Récupérer la date
                        date = commentaire.find_element(By.XPATH, ".//span[@class='c-review-block__date']").text
                        note = commentaire.find_element(By.XPATH, ".//div[@class='bui-review-score__badge']").text
                        # Récupérer le titre du commentaire
                        titre = commentaire.find_elements(By.XPATH, ".//h3")[0].text
                        # Récupérer la partie positive du commentaire
                        try:
                            commentairePositif = commentaire.find_elements(By.XPATH, ".//p[@class='c-review__inner c-review__inner--ltr']")[0].text
                        except:
                            commentairePositif = ""
                        # Récupérer la partie négative du commentaire
                        try:
                            commentaireNegatif = commentaire.find_elements(By.XPATH, ".//p[@class='c-review__inner c-review__inner--ltr']")[1].text
                        except:
                            commentaireNegatif = ""

                        # On vient ajouter le commentaire dans la liste contenant les résultats
                        data.append([ville, hotelName, auteur, date, note, titre, commentairePositif, commentaireNegatif])
                    except:
                        pass

                driver.find_element(By.XPATH, "//a[@class='pagenext']").click()
        except:
            print("Aucun commentaire présent")
            pass

        # On ferme l'onglet sur lequel on est actuellement
        driver.close()
        
        # On revient à l'onglet principale
        driver.switch_to.window(driver.window_handles[0])

        # On vient attendre que les liens se chargent
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='a78ca197d0']")))
        sleep(1)

    driver.close()

    return data

baseURL = "https://www.booking.com/"
nbrHotelARecup = 2
nbrCommentairesMaxParHotel = 20
chemin_excel = "C:\\Users\\jeanv\\Desktop\\Cours\\Dev applis\\python\\ScrapingBooking\\commentaires.xlsx"
villes = ["Strasbourg", "Paris"]

data = []
for ville in villes:
    lien = baseURL + f"searchresults.fr.html?ss={ville}"
    print(lien)

    # On vient initialiser le driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.delete_all_cookies()

    actions = ActionChains(driver)

    data.append(scrapeData(lien, ville, nbrHotelARecup, nbrCommentairesMaxParHotel))

    driver.quit()

# Optimiser cette partie car si on met plus ou moins que 2 villes dans la liste villes, le script plantera
df = pd.DataFrame(data[0], columns=["Ville", "Hotel", "AuteurCommentaire", "DateCommentaire", "Note", "TitreCommentaire", "CommentairePositif", "CommentaireNégatif"])
df2 = pd.DataFrame(data[1], columns=["Ville", "Hotel", "AuteurCommentaire", "DateCommentaire", "Note", "TitreCommentaire", "CommentairePositif", "CommentaireNégatif"])

FinalDF = pd.concat([df, df2], ignore_index=True)

print(FinalDF.head())

FinalDF.to_excel(chemin_excel, index=False)
