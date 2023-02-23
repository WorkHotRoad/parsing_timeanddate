from selenium import webdriver
from pathlib import Path
import pickle, time
from utils import URL_FOR_LOGIN

BASE_DIR = Path(__file__).parent
option = webdriver.FirefoxOptions()
option.headless = True

        # for proxy
# ip = '103.171.5.33'
# port = 8080
# firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
# firefox_capabilities["marionette"] = True
# option.set_preference('network.proxy.type', 1)
# option.set_preference('network.proxy.http', ip)
# option.set_preference('network.proxy.http_port', port)
# option.set_preference('network.proxy.https', ip)
# option.set_preference('network.proxy.https_port', port)
# option.set_preference('network.proxy.ssl', ip)
# option.set_preference('network.proxy.ssl_port', port)

driver = webdriver.Firefox(
    # executable_path=r'F:\python\Dev\homework\geckodriver.exe',
    executable_path=f'{BASE_DIR}\\geckodriver\\geckodriver.exe',
    options = option
)

# url_for_login = "https://www.timeanddate.com/custom/login.html"

def get_cookies():
    try:
        name = 0
        while not name:
            auth_email = input("Для авторизации введите свою почту: ")
            auth_password = input("Введите пароль: ")
            print("Passing authorization...")
            driver.get(url=URL_FOR_LOGIN)
            time.sleep(1)
            email_imput = driver.find_element("id", "email")
            email_imput.clear()
            email_imput.send_keys(auth_email)
            password_imput = driver.find_element("id", "password")
            password_imput.clear()
            password_imput.send_keys(auth_password)
            time.sleep(1)
            button = driver.find_element("xpath",'//input[@type="submit"]').click()
            name = driver.find_element("xpath", '//header[@class="tc pdflexi"]')
            if not name:
                print("authorization has not been successfully, try again")
            else:
                name = 1
                cookies = driver.get_cookies()
                with open("cookies", 'wb') as f:
                    pickle.dump(cookies, f)
                print("authorization has been successfully completed")
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
        return cookies
