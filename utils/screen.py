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

SITE_URL = 'http://127.0.0.1:8000/'


async def make_screen(user_id, url, area, is_general_stat):
    token = await get_valid_access(user_id)
    driver = webdriver.Firefox()

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
