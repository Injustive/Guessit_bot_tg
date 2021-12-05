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
import os
from loggers_control.loggers import db_logger

SITE_URL = 'https://guessit-space.herokuapp.com/'


async def make_screen(user_id, url, area, is_general_stat):
    token = await get_valid_access(user_id)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    def interceptor(request):
        request.headers['Authorization'] = f'Bearer {token}'

    def wait_response():
        try:
            WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, 'preloader')))
        except TimeoutException:
            WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, 'preloader')))

    driver.request_interceptor = interceptor
    
    try:
        driver.get(SITE_URL + url)
    except Exception as e:
        db_logger.error(f'Ошибка -- {e}')
    for request in driver.requests:
        if not request.response.status_code == 200:
            raise BadStatusError
    
    try:    
        wait_response()
    except Exception as e:
        db_logger.error(f'Ошибка -- {e}')

    await asyncio.sleep(2)
    
    try:
        png = driver.get_screenshot_as_png()
    except Exception as e:
        db_logger.error(f'Ошибка -- {e}')
    db_logger.error(f'Ошибка -- {png}')
    driver.quit()
    #     img = Image.open(io.BytesIO(png))
    #     output = io.BytesIO()
    #     img.crop(area).save(output, format='BMP')
    return png
