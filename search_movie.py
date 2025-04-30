from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import difflib
import re

def nettoyer_titre(titre):
    # Supprime les années entre parenthèses, les ":" et les suffixes comme "HD"
    titre = re.sub(r"\(\d{4}\)", "", titre)       # supprime (2025)
    titre = re.sub(r"\s*:\s*", " ", titre)         # remplace ":" par espace
    titre = re.sub(r"\bHD\b", "", titre)           # supprime HD
    return titre.strip().lower()

def find_film_link(search_name, seuil_bon_match=0.85, seuil_min=0.5):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    site_url="https://koriom.com/cywz0waiqhzf4/home/koriom"
    
    try:
        driver.get(site_url)
        time.sleep(2)

        search_input = driver.find_element(By.ID, "mod_search_searchword")
        search_input.clear()
        search_input.send_keys(search_name)
        search_input.submit()
        time.sleep(2)

        links = driver.find_elements(By.CSS_SELECTOR, "#hann p span a")

        candidates = []

        for link in links:
            title = link.text.strip()
            href = link.get_attribute("href")
            if not title or not href or "http" not in href:
                continue
            cleaned_title = nettoyer_titre(title)
            candidates.append((cleaned_title, href, title))

        cleaned_search = nettoyer_titre(search_name)

        #print(candidates)

        matches = []
        for cleaned_title, href, original_title in candidates:
            score = difflib.SequenceMatcher(None, cleaned_search, cleaned_title).ratio()
            if score >= seuil_min:
                matches.append((score, original_title, href))

        # Trier du plus pertinent au moins
        matches.sort(reverse=True)

        if matches:
            print(f"\n🔎 Résultats similaires à « {search_name} » :")
            for score, title, url in matches[:5]:
                print(f"- {title} ({score:.2f}) → {url}")

            # Prendre le premier si assez pertinent
            if matches[0][0] >= seuil_bon_match:
                print(f"\n✅ Meilleur match automatique : {matches[0][1]} ({matches[0][0]:.2f})")
                return matches[0][2]
            else:
                print("\n⚠️ Résultats trop proches, sélection manuelle recommandée.")
                print(matches)
                return matches
        else:
            print("❌ Aucun résultat suffisamment proche trouvé.")
            return None

    finally:
        driver.quit()



#find_film_link("Captain America : Civil War")
