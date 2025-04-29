from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time

def extract_m3u8_from_nested_iframe(main_url):
    options = Options()
    options.add_argument("--headless")  # Mode sans interface
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(main_url)
        time.sleep(3)  # Laisse le JS charger

        # Accès au premier iframe
        iframes = driver.find_elements("tag name", "iframe")
        if len(iframes) == 0:
            print("❌ Aucun iframe trouvé.")
            return None

        driver.switch_to.frame(iframes[0])  # On entre dans le premier iframe
        time.sleep(2)

        # Accès à l’iframe secondaire s’il y en a un
        inner_iframes = driver.find_elements("tag name", "iframe")
        if len(inner_iframes) > 0:
            driver.switch_to.frame(inner_iframes[0])
            time.sleep(2)

        # Analyse du contenu du DOM de l’iframe final
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'jwplayer' in script.string and '.m3u8' in script.string:
                match = re.search(r'"(https?://[^"]+\.m3u8)"', script.string)
                if match:
                    return match.group(1)

        return None

    finally:
        driver.quit()


#url = "https://koriom.com/cywz0waiqhzf4/b/koriom/83303496"
#m3u8_url = extract_m3u8_from_nested_iframe(url)
#if m3u8_url:
#    print("✅ Lien m3u8 trouvé :", m3u8_url)
#else:
#    print("❌ Aucun lien trouvé.")
