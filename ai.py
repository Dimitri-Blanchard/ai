import sys
import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import sys
import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AssistantIA:
    def __init__(self, headless=False):
        """
        Initialise l'assistant IA avec le navigateur configuré.
        
        Args:
            headless (bool): Si True, le navigateur s'exécute en mode headless (sans interface graphique)
        """
        self.driver = None
        self.headless = headless
        self.configurer_navigateur()
    
    def configurer_navigateur(self):
        """Configure et initialise le navigateur Chrome avec les options appropriées."""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")  # Utiliser la nouvelle syntaxe headless
            
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1920,1080")  # Dimension fixe pour éviter les problèmes d'affichage
            
            # Désactiver les notifications et popups
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            # Définir la langue
            options.add_argument("--lang=fr-FR,fr")
            
            # Réduire la journalisation du navigateur
            options.add_argument("--log-level=3")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Paramètres supplémentaires pour éviter la détection
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Utiliser le chromedriver local s'il existe
            chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe")
            
            if os.path.exists(chromedriver_path):
                logger.info(f"[+] Utilisation du chromedriver local: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fallback: utiliser webdriver_manager pour télécharger automatiquement
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                    logger.info("[+] ChromeDriver téléchargé et installé via webdriver_manager.")
                except Exception as e:
                    logger.error(f" Erreur lors de l'installation automatique de ChromeDriver: {e}")
                    raise
            
            # Définir un timeout implicite
            self.driver.implicitly_wait(10)
            
            # Modifier les attributs du navigateur pour éviter la détection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f" Erreur lors de la configuration du navigateur: {e}")
            raise
    
    def attendre_et_cliquer(self, by, value, timeout=15, description="élément", retry_count=3):
        """
        Attend qu'un élément soit cliquable et clique dessus avec plusieurs tentatives.
        
        Args:
            by: Type de sélecteur (By.XPATH, By.CSS_SELECTOR, etc.)
            value: Valeur du sélecteur
            timeout: Délai d'attente en secondes
            description: Description de l'élément pour les logs
            retry_count: Nombre de tentatives en cas d'échec
            
        Returns:
            bool: True si le clic a réussi, False sinon
        """
        for attempt in range(retry_count):
            try:
                # Attendre que l'élément soit visible et cliquable
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
                
                # Faire défiler la page jusqu'à l'élément
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)  # Laisser le temps au défilement de se stabiliser
                
                # Plusieurs méthodes de clic pour contourner les problèmes potentiels
                try:
                    # Méthode 1: Clic direct
                    element.click()
                except ElementNotInteractableException:
                    try:
                        # Méthode 2: Clic via JavaScript
                        self.driver.execute_script("arguments[0].click();", element)
                    except:
                        # Méthode 3: Clic via ActionChains
                        ActionChains(self.driver).move_to_element(element).click().perform()
                
                logger.info(f"[+] '{description}' cliqué avec succès (tentative {attempt+1}).")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Tentative {attempt+1}/{retry_count} échouée pour cliquer sur '{description}': {e}")
                # Prendre une capture d'écran pour le débogage
                self.prendre_capture_ecran(f"erreur_clic_{description}_{attempt}")
                
                # Rafraîchir la page si c'est la dernière tentative
                if attempt == retry_count - 1:
                    logger.warning("Toutes les tentatives de clic ont échoué.")
                    return False
                
                # Petite pause avant la prochaine tentative
                time.sleep(2)
        
        return False
    
    def cliquer_sur_essayer(self):
        """Essaie de cliquer sur le bouton 'Essayez par vous-même'."""
        # Essayer différents sélecteurs possibles
        selectors = [
            (By.XPATH, "//button[contains(text(), 'Essayez par vous-même')]"),
            (By.XPATH, "//button[contains(text(), 'Try it yourself')]"),
            (By.XPATH, "//button[contains(text(), 'Get started')]"),
            (By.XPATH, "//button[contains(@class, 'start') or contains(@class, 'begin')]")
        ]
        
        for by, value in selectors:
            if self.attendre_et_cliquer(by, value, description="Bouton 'Essayez'"):
                return True
        
        return False

    def accepter_cgu(self):
        """Essaie d'accepter les conditions générales d'utilisation."""
        # Essayer différents sélecteurs possibles
        selectors = [
            (By.XPATH, "//button[contains(text(), \"Je suis d'accord\")]"),
            (By.XPATH, "//button[contains(text(), 'I agree')]"),
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
            (By.XPATH, "//button[contains(@class, 'accept') or contains(@class, 'agree')]")
        ]
        
        for by, value in selectors:
            if self.attendre_et_cliquer(by, value, description="Bouton CGU"):
                return True
        
        return False
    
    def entrer_texte(self, element, texte):
        """
        Entre du texte dans un élément de manière robuste.
        
        Args:
            element: L'élément dans lequel entrer le texte
            texte: Le texte à entrer
            
        Returns:
            bool: True si l'entrée a réussi, False sinon
        """
        try:
            # Effacer le contenu existant
            element.clear()
            
            # Méthode 1: Entrée directe
            element.send_keys(texte)
            return True
        except Exception as e1:
            logger.warning(f"⚠️ Méthode d'entrée directe échouée: {e1}")
            try:
                # Méthode 2: Entrée par morceau
                for char in texte:
                    element.send_keys(char)
                    time.sleep(0.01)  # Pause entre chaque caractère
                return True
            except Exception as e2:
                logger.warning(f"⚠️ Méthode d'entrée par morceau échouée: {e2}")
                try:
                    # Méthode 3: Entrée via JavaScript
                    self.driver.execute_script("arguments[0].value = arguments[1];", element, texte)
                    return True
                except Exception as e3:
                    logger.error(f" Toutes les méthodes d'entrée ont échoué: {e3}")
                    return False

    def consulter_ia(self, question):
        """
        Envoie une question à l'IA et récupère la réponse.
        
        Args:
            question (str): La question à envoyer à l'IA
            
        Returns:
            str: La réponse de l'IA
        """
        try:
            # Ouvrir la page DuckDuckGo AI Chat
            self.driver.get("https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1")
            logger.info("[+] Page DuckDuckGo AI Chat ouverte.")
            
            # Attendre que la page soit complètement chargée
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Pause supplémentaire pour stabilisation
            
            # Gestion des boutons initiaux
            self.cliquer_sur_essayer()
            time.sleep(1)
            self.accepter_cgu()
            time.sleep(1)
            
            # Alternative si l'interface change: redirection directe vers l'URL de chat
            try:
                current_url = self.driver.current_url
                if "duckai=1" not in current_url or "ia=chat" not in current_url:
                    self.driver.get("https://duckduckgo.com/?q=&ia=chat&duckai=1")
                    time.sleep(2)
            except:
                pass
            
            # Prendre une capture d'écran pour voir où nous en sommes
            self.prendre_capture_ecran("avant_saisie")
            
            # Liste des sélecteurs possibles pour le champ de saisie
            input_selectors = [
                (By.TAG_NAME, "textarea"),
                (By.CSS_SELECTOR, ".ia-input__textarea"),
                (By.CSS_SELECTOR, "[data-testid='chat-input']"),
                (By.CSS_SELECTOR, "textarea[placeholder]"),
                (By.XPATH, "//textarea[contains(@placeholder, 'message') or contains(@placeholder, 'chat') or contains(@placeholder, 'ask')]")
            ]
            
            # Rechercher le champ de saisie
            champ_input = None
            for by, value in input_selectors:
                try:
                    champ_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((by, value))
                    )
                    logger.info(f"[+] Champ de saisie trouvé avec sélecteur: {value}")
                    break
                except:
                    continue
            
            if not champ_input:
                # Dernier recours: rechercher tous les textareas et prendre le premier visible
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    if textarea.is_displayed():
                        champ_input = textarea
                        logger.info("[+] Champ de saisie trouvé par recherche de textareas visibles.")
                        break
            
            if not champ_input:
                self.prendre_capture_ecran("champ_input_non_trouve")
                raise Exception("Impossible de trouver le champ de saisie.")
            
            # Faire défiler jusqu'au champ d'entrée et attendre qu'il soit cliquable
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", champ_input)
            time.sleep(1)
            
            # Cliquer sur le champ d'entrée pour l'activer
            try:
                champ_input.click()
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", champ_input)
                except:
                    try:
                        ActionChains(self.driver).move_to_element(champ_input).click().perform()
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de cliquer sur le champ d'entrée: {e}")
            
            time.sleep(1)
            
            # Entrer le texte
            if not self.entrer_texte(champ_input, question):
                self.prendre_capture_ecran("erreur_saisie")
                raise Exception("Impossible d'entrer le texte dans le champ de saisie.")
            
            logger.info("[+] Question saisie dans le champ.")
            time.sleep(1)
            
            # Envoyer la question (plusieurs méthodes)
            try:
                # Méthode 1: Touche Entrée
                champ_input.send_keys(Keys.ENTER)
            except:
                try:
                    # Méthode 2: Rechercher et cliquer sur le bouton d'envoi
                    boutons_envoi = [
                        (By.CSS_SELECTOR, "button[type='submit']"),
                        (By.XPATH, "//button[@aria-label='Send' or @aria-label='Envoyer']"),
                        (By.XPATH, "//button[contains(@class, 'send') or contains(@class, 'submit')]")
                    ]
                    
                    for by, value in boutons_envoi:
                        try:
                            bouton = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((by, value))
                            )
                            bouton.click()
                            break
                        except:
                            continue
                except Exception as e:
                    logger.warning(f"⚠️ Problème lors de l'envoi du message: {e}")
                    # Méthode 3: Forcer l'envoi via JavaScript
                    try:
                        self.driver.execute_script("""
                            var inputs = document.getElementsByTagName('textarea');
                            for(var i=0; i<inputs.length; i++) {
                                if(inputs[i].value) {
                                    var event = new Event('submit');
                                    inputs[i].form.dispatchEvent(event);
                                    break;
                                }
                            }
                        """)
                    except:
                        pass
            
            logger.info("[+] Question envoyée à l'IA.")
            
            # Vérifier si le message a bien été envoyé
            time.sleep(3)
            self.prendre_capture_ecran("apres_envoi")
            
            # Récupérer la réponse
            reponse = self.recuperer_reponse()
            return reponse
        
        except Exception as e:
            logger.error(f" Erreur lors de la consultation de l'IA: {e}")
            # Prendre une capture d'écran pour faciliter le débogage
            self.prendre_capture_ecran("erreur_consultation")
            return f"Erreur lors de la consultation de l'IA: {str(e)}"

    def recuperer_reponse(self, timeout=120, stable_duration=3):
        """
        Attend et récupère la réponse de l'IA.
        
        Args:
            timeout (int): Délai maximum d'attente en secondes
            stable_duration (int): Durée en secondes pendant laquelle la réponse doit être stable
            
        Returns:
            str: La réponse de l'IA
        """
        logger.info(f" Attente de la réponse (timeout: {timeout}s, stable: {stable_duration}s)...")

        try:
            # Liste des sélecteurs possibles pour la réponse
            response_selectors = [
                (By.CSS_SELECTOR, ".VrBPSncUavA1d7C9kAc5"),  # Sélecteur actuel
                (By.CSS_SELECTOR, ".chat-result-response"),   # Sélecteur alternatif
                (By.CSS_SELECTOR, "[data-testid='chat-response']"),  # Autre sélecteur possible
                (By.XPATH, "//div[contains(@class, 'chat') and contains(@class, 'response')]"),  # Sélecteur XPATH générique
                (By.XPATH, "//div[@role='region' or @role='log']//div[contains(@class, 'chat') or contains(@class, 'message')]")  # Zone de messages
            ]
            
            # Rechercher l'élément de réponse avec les différents sélecteurs
            reponse_element = None
            for by, value in response_selectors:
                try:
                    reponse_element = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((by, value))
                    )
                    logger.info(f"[+] Élément de réponse trouvé avec sélecteur: {value}")
                    break
                except:
                    continue
            
            if not reponse_element:
                # Essayer de trouver n'importe quel élément de texte qui pourrait contenir la réponse
                logger.warning("⚠️ Aucun sélecteur prédéfini n'a fonctionné, recherche alternative...")
                try:
                    # Attendre que la page ne charge plus
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    
                    # Chercher des éléments qui pourraient contenir la réponse
                    potential_elements = self.driver.find_elements(By.TAG_NAME, "div")
                    
                    # Filtrer pour trouver les éléments avec du texte substantiel
                    for elem in potential_elements:
                        text = elem.text.strip()
                        if len(text) > 100:  # Texte assez long pour être une réponse
                            reponse_element = elem
                            logger.info("[+] Élément de réponse trouvé par méthode alternative.")
                            break
                except:
                    pass
            
            if not reponse_element:
                # Dernier recours: prendre tout le contenu de la page
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if len(body_text) > 200:  # S'assurer qu'il y a du contenu substantiel
                        logger.info("[+] Utilisation du contenu global de la page comme réponse.")
                        return body_text
                except:
                    pass
                
                self.prendre_capture_ecran("reponse_introuvable")
                return "Erreur : impossible de localiser la réponse de l'IA sur la page."

            # Attendre que la réponse soit stable (ne change plus)
            previous_text = ""
            stable_time = 0
            start_time = time.time()

            while True:
                try:
                    current_text = reponse_element.text.strip()
                
                    # Vérifier si la réponse contient du texte significatif
                    if current_text and not current_text.lower().startswith(("loading", "chargement")):
                        # Vérifier si la réponse est stable
                        if current_text == previous_text:
                            stable_time += 0.5
                            if stable_time >= stable_duration:
                                break
                        else:
                            stable_time = 0
                            previous_text = current_text
                
                    # Vérifier si le timeout est atteint
                    if time.time() - start_time > timeout:
                        logger.warning("⚠️ Délai d'attente dépassé pour la stabilisation de la réponse.")
                        break
                
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f" Erreur pendant l'attente de la stabilisation: {e}")
                    # Si l'élément n'est plus accessible, utiliser la dernière réponse connue
                    if previous_text:
                        break
                    else:
                        self.prendre_capture_ecran("erreur_stabilisation")
                        return "Erreur pendant la récupération de la réponse."

            if not previous_text:
                # Essayer d'obtenir le texte une dernière fois
                try:
                    previous_text = reponse_element.text.strip()
                except:
                    pass
                
                if not previous_text:
                    self.prendre_capture_ecran("reponse_vide")
                    return "Erreur : réponse vide ou non détectée."
                
            logger.info("[+] Réponse récupérée avec succès.")
            return previous_text

        except TimeoutException:
            logger.error(" Délai d'attente dépassé pour la réponse.")
            self.prendre_capture_ecran("timeout_reponse")
            return "Erreur : délai d'attente dépassé pour la réponse."
        except Exception as e:
            logger.error(f" Échec de récupération de la réponse : {e}")
            self.prendre_capture_ecran("erreur_reponse")
            return f"Erreur lors de la récupération de la réponse : {str(e)}"

    def prendre_capture_ecran(self, nom_fichier):
        """
        Prend une capture d'écran pour le débogage.
        
        Args:
            nom_fichier (str): Préfixe du nom de fichier
        """
        try:
            if self.driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                fichier = f"{nom_fichier}_{timestamp}.png"
                self.driver.save_screenshot(fichier)
                logger.info(f" Capture d'écran sauvegardée: {fichier}")
        except Exception as e:
            logger.error(f" Impossible de prendre une capture d'écran: {e}")

    def fermer(self):
        """Ferme le navigateur s'il est ouvert."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("[+] Navigateur fermé.")
                self.driver = None
        except Exception as e:
            logger.error(f" Erreur lors de la fermeture du navigateur: {e}")

def afficher_aide():
    """Affiche l'aide du programme."""
    print("""
Usage: python ai.py [options] prompt.txt

Options:
  -h, --help      Affiche cette aide
  --headless      Exécute le navigateur en mode headless (sans interface graphique)

Arguments:
  prompt.txt      Fichier contenant la question à envoyer à l'IA
""")

def main():
    """Fonction principale du programme."""
    # Analyser les arguments
    headless_mode = False
    prompt_file = None
    
    if len(sys.argv) < 2:
        afficher_aide()
        return 1
    
    # Parcourir les arguments
    for arg in sys.argv[1:]:
        if arg in ("-h", "--help"):
            afficher_aide()
            return 0
        elif arg == "--headless":
            headless_mode = True
        elif not prompt_file and not arg.startswith("-"):
            prompt_file = arg
    
    if not prompt_file:
        logger.error("Aucun fichier prompt spécifié.")
        afficher_aide()
        return 1
    
    # Lire le contenu du fichier prompt
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier prompt: {e}")
        return 1
    
    if not prompt.strip():
        logger.error("Le fichier prompt est vide.")
        return 1
    
    # Initialiser l'assistant IA
    assistant = None
    try:
        logger.info(f"Démarrage de l'assistant IA (mode headless: {headless_mode})")
        assistant = AssistantIA(headless=headless_mode)
        
        # Consulter l'IA avec le prompt
        logger.info(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
        reponse = assistant.consulter_ia(prompt)
        
        # Afficher la réponse
        print("\n" + "="*50)
        print("RÉPONSE DE L'IA:")
        print("="*50)
        print(reponse)
        print("="*50 + "\n")
        
        # Sauvegarder la réponse dans un fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fichier_reponse = f"reponse_{timestamp}.txt"
        with open(fichier_reponse, "w", encoding="utf-8") as f:
            f.write(reponse)
        logger.info(f"[+] Réponse sauvegardée dans {fichier_reponse}")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("⚠️ Programme interrompu par l'utilisateur.")
        return 1
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return 1
    
    finally:
        # Fermer le navigateur
        if assistant:
            assistant.fermer()

if __name__ == "__main__":
    sys.exit(main())