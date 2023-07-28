from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
import pandas as pd
import random
import time
import os

choice = input("""Choose from the choices:
    Enter 1 - Products
    Enter 2 - Recipe Module
    Enter 3 - Shopping List
    Enter 4 - Group
    Enter 5 - AI Wine Pairing kemerut
I choose - """)

class LoginPage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
    
    # LOGIN
    def navigate(self):
        self.driver.get('PROVIDE URL THAT YOU WANT TO VISIT')

    def input_email(self, email):
        # wait for the email input element to be visible
        email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "input-login-username")))
        email_input.send_keys(email)

    def input_password(self, password):
        input_pw = self.driver.find_element(By.ID, "PW")
        input_pw.send_keys(password)

    def click_login_button(self):
        login_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-login/div/div[2]/app-signin/div/div/div[10]/button")
        login_button.click()


class MainPage:
    def __init__(self, driver):
        # Create a Service object to initialize the WebDriver
        #service = Service(ChromeDriverManager().install())
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def Home(self):
        # Go to the home page/ Main Dashboard
        self.driver.get('https://appasiaqa.calcmenu.com/Home/Dashboard')

    def navigate(self):
        # navigate to the main page after login
        pass

    def btn_click(self, xpath):
        # where xpath is the XPATH of the button
        # Wait for the button to be visible
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        
    def nav_to_tabs(self):
        # navigate to the tabs
        """#click that tab
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, tab_xpath)
        )).click()"""
        # Wait for the mat-tab-labels element to be present
        wait = WebDriverWait(self.driver, 10)
        mat_tab_labels_locator = (By.CLASS_NAME, 'mat-tab-labels')
        mat_tab_labels_element = wait.until(EC.presence_of_element_located(mat_tab_labels_locator))

        # Switch to the iframe if necessary
        if mat_tab_labels_element.tag_name == 'iframe':
            self.driver.switch_to.frame(mat_tab_labels_element)

        # traverse through the tab elements and click them
        tab_elements = mat_tab_labels_element.find_elements(By.XPATH, ".//div[starts-with(@id, 'mat-tab-label-')]")
        for tab_element in tab_elements:
            tab_element.click()
            time.sleep(1)  # Wait for the tab to load, adjust sleep duration as needed


    @staticmethod
    def save_to_excel(words, save_path):
        try:
            # Create a pandas DataFrame with the words
            df = pd.DataFrame(words, columns=['Translated Word'])

            # Drop empty cells and move populated cells together
            df_filtered = df.dropna().reset_index(drop=True)

            if df_filtered.empty:
                print("No data to save. Exiting.")
                return

            # Save the filtered DataFrame to an Excel file
            df_filtered.to_excel(save_path, index=False)
            print("Text saved to Excel successfully.")

        except Exception as e:
            print("Error occurred while saving to Excel:", e)


    def retrieve_text_from_current_frame(self, element, texts, parent_elements=None):
        # Initialize parent elements set if it is not passed
        if parent_elements is None:
            parent_elements = set()

        # Approach 1: Find immediate parent div element
        parent_element = None
        try:
            parent_element = element.find_element(By.XPATH, './parent::div')
        except NoSuchElementException:
            pass

        # Approach 2: Find parent div element by class
        if parent_element is None:
            try:
                parent_element = element.find_element(By.XPATH, './ancestor::div[contains(@class, "parent-div")]')
            except NoSuchElementException:
                pass

        # Approach 3: Find parent div element by ID
        if parent_element is None:
            try:
                parent_element = element.find_element(By.XPATH, './ancestor::div[@id="parent-div-id"]')
            except NoSuchElementException:
                pass

        # Retrieve text from parent div element if found
        if parent_element is not None and parent_element.is_displayed() and parent_element.text.strip() != '':
            texts.add(parent_element.text.strip())

        # Check if the element is visible and contains text
        if element.is_displayed() and element.text.strip() != '':
            text_content = element.text.strip()

            # Check if the text content is unique for this parent element
            if text_content not in parent_elements:
                texts.add(text_content)
                parent_elements.add(text_content)

        # Recursively traverse child elements
        for child_element in element.find_elements(By.XPATH, ".//*"):
            # Check if the child element is visible and contains text
            if child_element.is_displayed() and child_element.text.strip() != '':
                text_content = child_element.text.strip()

                # Check if the text content is unique for this parent element
                if text_content not in parent_elements:
                    texts.add(text_content)
                    parent_elements.add(text_content)

        # Retrieve text from each iframe recursively
        for iframe in element.find_elements(By.TAG_NAME, 'iframe'):
            self.driver.switch_to.frame(iframe)
            self.retrieve_text_from_current_frame(self.driver.find_element(By.TAG_NAME, 'body'), texts, parent_elements)
            self.driver.switch_to.default_content()

        return texts


    def get_all_text(self):
        try:
            # Wait for the page to fully load
            time.sleep(5)  # Adjust the sleep duration as needed

            # Wait for the page to load completely
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Switch to the main page content
            self.driver.switch_to.default_content()

            # Retrieve text from each tab
            all_texts = set()

            # Navigate to the tabs
            self.nav_to_tabs()

            # Switch back to the main page content
            self.driver.switch_to.default_content()

            # Retrieve text from each tab
            tab_elements = self.driver.find_elements(By.XPATH, "//div[starts-with(@id, 'mat-tab-content-')]")
            for i, tab_element in enumerate(tab_elements):
                print(f"Retrieving text from Tab {i + 1}...")
                
                # Retrieve text from the current tab
                self.retrieve_text_from_current_frame(tab_element, all_texts)

                # Switch to the next tab
                if i < len(tab_elements) - 1:
                    next_tab_button = self.driver.find_element(By.XPATH, "//div[contains(@id, 'mat-tab-label-') and not(contains(@class, 'mat-tab-disabled'))][last() + 1]")
                    next_tab_button.click()
                    wait.until(EC.staleness_of(tab_element))

            # Check if there are any texts to save
            if all_texts:
                # Print the retrieved text
                print("Retrieved text:")
                print('\n'.join(all_texts))

                # Save the retrieved text to an Excel file
                save_path = "F:/Self Study/Automation/all_text.xlsx"
                self.save_to_excel(all_texts, save_path)
            else:
                print("No data to save. Exiting.")

            return all_texts

        except Exception as e:
            print("Error occurred while retrieving text:", e)
            return None
        4

    def wine_pairing_automation(self):
        # Wine Pairing Automation
        # Click Account button
        self.btn_click("//*[@id='parentOfAll']/div[2]/div[1]/app-header/div/div[4]/div[10]/table/tr/td[2]/div/button")
        # Click Settings button
        self.btn_click("//*[@id='mat-menu-panel-2']/div/div[1]")
        # Click on the Languages tab
        self.btn_click("//*[@id='mat-tab-content-0-0']/div/div/div[2]/div/div[1]/div")

        # Find the parent element that contains the buttons
        parent_element_locator = (By.XPATH, '//*[@id="mat-tab-content-0-0"]/div/div/div[2]/div/div[1]/div')
        parent_element = self.wait.until(EC.visibility_of_element_located(parent_element_locator))

        # Find all the language buttons within the parent element
        language_buttons = parent_element.find_elements(By.TAG_NAME, 'button')

        for button in language_buttons:
            print("Current Language is " + button.text)
            button.click()

            try:
                # Wait for the overlay or element that intercepts the click to disappear
                overlay_locator = (By.XPATH, "//*[@class='close ng-star-inserted']")
                self.wait.until(EC.invisibility_of_element_located(overlay_locator))
            except TimeoutException:
                # Handle the case if the overlay does not disappear within the timeout
                print("Overlay did not disappear. Skipping click for the current language.")
                continue

            # Save the selected language after selecting the button
            self.btn_click("//*[@id='parentOfAll']/div[2]/div[2]/div[1]/app-settings/div[4]/div/div/button[1]")
            # Perform the automation function specific to the selected language
            #self.perform_automation()



    # Wine Pairing Automation that calls 3 functions
    def perform_automation(self):
        print("Performing automation...")

        # 2 ingredients is required
        self.select_2_ingredients()

        # proceed to ai wine pairing
        self.ai_tab_automation()

        #then check if there is a proceed button/prompt (for first time prompt)
        self.check_proceedbtn()

        #validate suggestion if it is really saved
        self.save_and_check()
            

    def select_2_ingredients(self):
        # Go to Recipe Module
        self.btn_click("//*[@id='nav']/div[2]/button[3]")
        # Use New recipe button
        self.btn_click('//*[@id="scrollTo"]/div[2]/button[2]')
        # Set the parent element locator
        parent_element_locator = (By.XPATH, '//*[@id="parentOfAll"]/div[2]/div[2]/div[1]/app-recipe-edition/div')
        parent_element = self.wait.until(EC.visibility_of_element_located(parent_element_locator))

        # Need 2 Ingredients, go to the INGREDIENTS TAB
        self.btn_click("//*[@id='mat-tab-label-0-1']")

        # Click on the first ingredient input
        self.btn_click("//*[@id='cdk-drop-list-0']/div[3]/div[2]/input")

        # Find the mat-option elements within the dropdown element
        mat_option_locator = (By.XPATH, '//*[@id="mat-autocomplete-4"]')

        # Wait for the options to be fully loaded, if needed
        time.sleep(2)  

        #___________________________________________________________________________________

        optionss = self.wait.until(EC.visibility_of_all_elements_located(mat_option_locator))

        # Select randomly from the choices
        random_option = random.choice(optionss)
        ingredient_text = random_option.text  # Retrieve the ingredient text immediately


        # Click on the first ingredient input
        self.btn_click("//*[@id='cdk-drop-list-0']/div[3]/div[2]/input")


        # Get all the options for the first input
        options1 = self.wait.until(EC.visibility_of_all_elements_located(mat_option_locator))
        if not options1:
            print("No options found in the dropdown.")
            exit()

        # Select a random ingredient for the first input
        random_option1 = random.choice(options1)
        ingredient_text1 = random_option1.text

        # Enter the first ingredient manually
        input_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cdk-drop-list-0"]/div[3]/div[2]/input')))
        input_element.clear()
        input_element.send_keys(ingredient_text1)

        # Click on the second ingredient input using JavaScript
        input_xpath2 = '//*[@id="cdk-drop-list-0"]/div[5]/div[2]/input'
        input_element2 = self.wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath2)))
        self.driver.execute_script("arguments[0].click();", input_element2)


        # Get all the options for the second input
        options2 = self.wait.until(EC.visibility_of_all_elements_located(mat_option_locator))
        if not options2:
            print("No options found in the dropdown.")
            exit()

        # Select a random ingredient for the second input
        random_option2 = random.choice(options2)
        ingredient_text2 = random_option2.text

        # Enter the second ingredient manually
        input_element2.clear()
        input_element2.send_keys(ingredient_text2)




    def ai_tab_automation(self):
        # Click AI TAB
        self.btn_click("//*[@id='mat-tab-label-0-7']/div")

        parent_radio_btn = (By.XPATH, "//*[@id='mat-tab-content-2-0']/div/div[2]/div[2]")
        # Increase the timeout duration and use element_to_be_clickable() expected condition
        parent_radio = self.wait.until(EC.element_to_be_clickable(parent_radio_btn))

        # Find all the radio buttons within the parent element
        radio_buttons = parent_radio.find_elements(By.TAG_NAME, 'mat-radio-button')
        #click last choice
        radio_buttons[3].click()


        # A case where wine is suggested based on the region and dropdown is used
        dropdown_locator = (By.XPATH, "//*[@id='mat-tab-content-2-0']/div/div[2]/div[3]/input")
        dropdown_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(dropdown_locator)
        )

        # Click dropdown first to make options visible
        dropdown_element.click()


        # Wait for the dropdown options to be populated
        options_locator = (By.XPATH, "/html/body/div[4]/div/div/div/div[1]/mat-checkbox")
        checkboxes = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_all_elements_located(options_locator)
        )

        # Select randomly from the choices
        random_option = random.choice(checkboxes)
        random_option.click()

        print("Selected Region is " + random_option.text)

        # Wait for the AI button to be displayed
        ai_btn_locator = (By.XPATH, "//*[@id='mat-tab-content-2-0']/div/div[2]/div[1]/app-aibtn/div/span[1]")
        self.wait.until(EC.presence_of_all_elements_located(ai_btn_locator))

        # Click Suggest Button to make AI suggestion
        ai_btn = self.driver.find_element(*ai_btn_locator)
        ai_btn.click()





    def check_proceedbtn(self):
        # Define the locator for the proceed button
        proceed_btn_locator = (By.XPATH, "/html/body/ngb-modal-window/div/div/div/div[5]/button[1]")

        # Case for first time clicking suggest and prompts user to proceed
        # Try if it pops up
        try:
            proceed_btn = WebDriverWait(self.driver, 10).until( 
            EC.visibility_of_element_located(proceed_btn_locator)
            )  # Wait for the proceed button to be visible
        except NoSuchElementException:
            proceed_btn = None

        # If it is displayed, then click it
        if proceed_btn and proceed_btn.is_displayed():
            proceed_btn.click()
        else:
            pass

    def save_and_check(self):
        save_btn_locator = (By.XPATH, "/html/body/app-root/app-home/div/div[2]/div[2]/div[1]/app-recipe-edition/div/div/div[1]/button[1]")

        # Wait for the AI ongoing popup window to finish
        ai_popup_locator = (By.XPATH, "//*[@id='mat-tab-content-0-7']/div/app-t-ai/app-aiblock/div[2]/div/div")
        ai_popup_present = True

        while ai_popup_present:
            try:
                self.driver.find_element(*ai_popup_locator)
                time.sleep(1)  # Wait for 1 second before checking again
            except NoSuchElementException:
                ai_popup_present = False

        try:
            save_btn = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable(save_btn_locator)
            )

            # Click save button
            save_btn.click()
        except TimeoutException:
            print("Save button not found within the specified timeout.")
        """
        # Wait for the success popup to be visible
        success_popup_locator = (By.XPATH, "/ngb-alert")
        success_popup = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(success_popup_locator)
        )
        
        # Proceed with further logic if the success popup is displayed
        try:
            if success_popup.is_displayed():
                # Your logic for handling the successful save
                print("Wine pairing suggestion saved successfully.")
                # Continue with your desired actions here
            else:
                print("Wine pairing suggestion save failed.")
             # Handle the failure scenario or raise an exception
        except:
            pass
        """
        # Click the close button of the success popup
        close_btn_locator = (By.XPATH, "//*[@id='parentOfAll']/div[2]/div[2]/div[1]/app-recipe-edition/div/div/div[1]/button[2]")
        close_btn = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(close_btn_locator)
        )
        close_btn.click()

        # Click AI TAB
        self.btn_click("//*[@id='mat-tab-label-0-7']/div")

        # check if wine suggestion is saved by checking if the suggestioon exists
        try:
            element = self.driver.find_element(By.XPATH, "//*[@id='mat-tab-content-10-0']/div/div[2]/div[2]/span")
            print("Suggestion SAVED successfully.")
        except NoSuchElementException:
            print("Suggestion NOT SAVED.")



# leave the browser open even if tasks are complete
options = Options()
options.add_experimental_option("detach", True)
try:
    print("Trying to use ChromeDriverManager...")
    # Create a webdriver instance
    # https://googlechromelabs.github.io/chrome-for-testing/ this is the URL for availability of Chrome versions
    chrome_version = "115.0.5790.102"  # Replace this with the version you want to use
    driver = webdriver.Chrome(executable_path=ChromeDriverManager(chrome_type='google-chrome', version=chrome_version).install(), options=options)
except Exception as e:
    # If the current Chrome version is not available in the link above, use this (NOTE: YOU MUST HAVE A CHROMEDRIVER.EXE IN THE SAME DIRECTORY WHERE YOUR SCRIPT IS SAVED)
    print("Chrome version not available. Using chromedriver.exe instead.")
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)


# create login page object
login_page = LoginPage(driver)

# navigate to the CMC login page
login_page.navigate()

# Input email and password
login_page.input_email("inputyourusernamehere")
login_page.input_password("inputyourpasswordhere")


# click login button
login_page.click_login_button()

# create main page object
main_page = MainPage(driver)

# navigate to the main page after login
main_page.navigate()

if choice == "1":
    # Products
    main_page.btn_click("//*[@id='nav']/div[2]/button[2]")

elif choice == "2": 
    # Recipe Module
    main_page.btn_click("//*[@id='nav']/div[2]/button[3]")
    # 2 BUTTONS AI NEW RECIPE AND NEW RECIPE
    choice_ai = input("""Choose from the choices:
    Enter 1 - AI Recipe
    Enter 2 - New Recipe
    Enter 3 - Select First Recipe
                    I choose - """)

    if choice_ai == "1":
        # Use AI recipe button
        main_page.btn_click('//*[@id="parentOfAll"]/div[2]/div[2]/div[2]/ng-component/app-search/div/div/div[1]/div[2]/button')
    elif choice_ai == "2":
        # Use New recipe button
        main_page.btn_click('//*[@id="scrollTo"]/div[2]/button')


    elif choice_ai == "3":
        # placeholder of all the text (except for the left navigation bar)
        section_xpath = '//*[@id="parentOfAll"]/div[2]/div[2]/div[1]/app-recipe-details'

        # Select First recipe
        main_page.btn_click('//*[@id="parentOfAll"]/div[2]/div[2]/div[2]/ng-component/app-search/div/div/div[3]/div[2]/div[1]/div[1]/div/button')

        # Call get_all_text method to retrieve the text and save it to an excel file
        main_page.get_all_text()

elif choice == "3":
    # Shopping List
    main_page.btn_click("//*[@id='nav']/div[2]/button[5]")
elif choice == "4":
    # Group
    main_page.btn_click("//*[@id='nav']/div[2]/button[7]")

    # navigate through the tabs
    main_page.nav_to_tabs()
elif choice == "5":
    #main_page.wine_pairing_automation()
    main_page.perform_automation()
else:
    print("Please choose only from 1 to 5")
