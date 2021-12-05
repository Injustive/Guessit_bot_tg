from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
from selenium.common.exceptions import TimeoutException
from .queries_to_server import get_valid_access
from errors import BadStatusError
import asyncio
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from loggers_control.loggers import db_logger

SITE_URL = 'https://guessit-space.herokuapp.com/'


async def make_screen(user_id, url, area, is_general_stat):
    token = await get_valid_access(user_id)

    options = webdriver.FirefoxOptions()
    db_logger.error(f'{options})
    options.add_argument("-headless")
    options.add_argument("-disable-gpu")
    options.add_argument("-no-sandbox")

    binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))
    db_logger.error(f'{binary}')

    binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))
    driver = webdriver.Firefox(
        firefox_binary=binary,
	executable_path=os.environ.get('GECKODRIVER_PATH'),
    )
    db_logger.error(f'{driver}')
    def interceptor(request):
        request.headers['Authorization'] = f'Bearer {token}'

    def wait_response():
        try:
            WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, 'preloader')))
        except TimeoutException:
            WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, 'preloader')))

    driver.request_interceptor = interceptor
    driver.get(SITE_URL + url)
    for request in driver.requests:
        if not request.response.status_code == 200:
            raise BadStatusError

    wait_response()

    await asyncio.sleep(2)
    if is_general_stat:
        png = driver.find_element(By.TAG_NAME, 'body').screenshot_as_png
    else:
        png = driver.get_screenshot_as_png()
    driver.quit()
    img = Image.open(io.BytesIO(png))
    output = io.BytesIO()
    img.crop(area).save(output, format='BMP')
    return output
