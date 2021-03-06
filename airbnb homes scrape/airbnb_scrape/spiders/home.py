# -*- coding: utf-8 -*-
import scrapy
import re
import sys
from time import sleep
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from airbnb_scrape.items import AirbnbScrapeItem
from selenium.webdriver.support import expected_conditions as EC

WAIT_FOR_PAGE_LOADING_TIME = 1.5 ## After selenium gets a request, it is reliable to wait for a while until the page is fully loaded 

class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['www.airbnb.ca']
    start_urls = ['http://www.airbnb.ca']

    def get_home_type(self, home_selector):
        home_type = home_selector.xpath('.//div[@class="_1j3840rv"]/text()').get()
        if home_type is not None:
            return home_type
        home_type = home_selector.xpath('.//div[@class="_1q6rrz5"]/text()').get()
        if home_type is not None:
            return home_type
        home_type = home_selector.xpath('.//div[@class="_dr3g77n"]/text()').get()
        if home_type is not None:
            return home_type
        home_type = home_selector.xpath('.//div[@class="_15w8m6q"]/text()').get()
        if home_type is not None:
            return home_type
        return None

    def get_rating(self, home_selector):
        rating = home_selector.xpath('.//div[@class="_tghtxy2"]/text()').get()
        if rating is not None:
            return float(rating)
        rating = home_selector.xpath('.//span[@class="_rs3rozr"]/@aria-label').get()
        if rating is not None:
            return float(rating.split()[1])
        rating = home_selector.xpath('.//span[@class="_60hvkx2"]/span[@class="_ky9opu0"]/text()').get()
        if rating is not None:
            return float(rating)
        rating = home_selector.xpath('.//span[@class="_3zgr580"]/text()').get()
        if rating is not None:
            return float(rating)
        return None

    def get_review_count(self, home_selector):
        review_count = home_selector.xpath('.//div[@class="_10qgzd5i"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        review_count = home_selector.xpath('.//div[@class="_1lqf9qr0"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        review_count = home_selector.xpath('.//span[@class="_q27mtmr"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        review_count = home_selector.xpath('.//span[@class="_ky9opu0"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        review_count = home_selector.xpath('.//span[@class="_3zgr580"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        return None

    def get_price(self, home_selector):
        price_text = home_selector.xpath('.//span[@class="_1p7iugi"]/span[@class="_krjbj"]/following-sibling::text()').get()
        if price_text is not None:
            return re.search(r'\d+', price_text).group()
        else:
            return None

    def get_image(self, home_selector):
        style_text = home_selector.xpath('.//div[@class="_1i2fr3fi"]/@style').get()
        if style_text is not None:
            background_image_text = re.search(r'background-image.*?url\(.*?\)', style_text).group()
            begin = background_image_text.find('(') + 2
            end = background_image_text.find(')') - 2
            image_url = background_image_text[begin: end + 1]
            return image_url
        else:
            return None
    
##    This method scrapes all the images of a home. However, the time consumption is intolerable. Therefore it can only fetch the only image in the original html
##    def get_images(self, index):
##        def get_current_image():
##            self.scrapy_selector = Selector(text = self.driver.page_source)
##            style_text = self.scrapy_selector.xpath('//div[@class="_1i2fr3fi"]/@style')[index].get()
##            background_image_text = re.search(r'background-image.*?url\(.*?\)', style_text).group()
##            begin = background_image_text.find('(') + 2
##            end = background_image_text.find(')') - 2
##            image_url = background_image_text[begin: end + 1]
##            return image_url
##        
##        def scroll_and_move_to_next_button():
##            home_element = self.driver.find_elements_by_xpath('//div[@class="_8ssblpx"]')[index]
##            self.driver.execute_script('window.scroll(arguments[0], arguments[1])', home_element.location['x'], home_element.location['y'] - home_element.size['height'] / 2)
##            next_button = self.driver.find_elements_by_xpath('//div[@class="_tk908t"]/button[2]')[index]
##            ActionChains(self.driver).move_to_element(next_button).perform()
##            return next_button
##
##        images = []
##        images.append(get_current_image())
##        next_button = scroll_and_move_to_next_button()
##        wait = WebDriverWait(self.driver, 10)
##        wait.until(EC.presence_of_element_located((By.XPATH, '(//div[@class="_8ssblpx"])['+ str(index + 1) + ']//button[@class="_1rftspj9"]')))
##        while True:
##            next_button.click()
##            wait.until(EC.invisibility_of_element_located((By.XPATH, '(//div[@class="_8ssblpx"])['+ str(index + 1) + ']//div[@class="_1na7kj9b"][2]')))
##            image_url = get_current_image()
##            if image_url == images[0]:
##                break
##            else:
##                images.append(image_url)
##        return images


    def close_driver(self):
        self.driver.close()
        self.logger.info('webdriver closed')


    def close_cookie_notice(self):
        try:
            self.driver.find_element_by_xpath('//button[@title="OK"]').click()
        except Exception as e:
            self.logger.error('close cookie notice error' + str(e))


    def get_chrome_driver_path(self):
        if sys.platform.startswith('darwin'):
            return './chromedriver_mac'
        elif sys.platform.startswith('linux'):
            return './chromedriver_linux'
        else:
            sys.exit('Chrome driver dos not support this OS.')

    def start_request_with_selenium(self):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument(" --disable-gpu")
        options.add_argument(" --disable-infobars")
        options.add_argument(" -–disable-web-security")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        caps = options.to_capabilities()
        self.driver = webdriver.Chrome(self.get_chrome_driver_path(), desired_capabilities=caps)
        self.driver.get(self.url)
        self.logger.info('started request to %s', self.url)
        sleep(WAIT_FOR_PAGE_LOADING_TIME)
        

    def parse(self, response):
        page_number = 1
        self.start_request_with_selenium()
        self.close_cookie_notice()
        
        while True:
            ## Load all home selectors
            self.logger.info('start scraping page ' + str(page_number))
            self.scrapy_selector = Selector(text = self.driver.page_source)
            home_selectors = self.scrapy_selector.xpath('//div[@class="_fhph4u"]/div[@class="_8ssblpx"]')
            self.logger.info('home_selectors lengh is ' + str(len(home_selectors)))

            ## Scrape all home items in the current page
            for index, home_selector in enumerate(home_selectors):
                home_type = self.get_home_type(home_selector)
                description = home_selector.xpath('.//div[@class="_1jbo9b6h"]/text()').get()
                room = u'\u00B7'.join(home_selector.xpath('(.//div[@class="_6kiyebe"]/div[@class="_1ulsev2"])[1]/text()').getall())
                amenity = u'\u00B7'.join(home_selector.xpath('(.//div[@class="_6kiyebe"]/div[@class="_1ulsev2"])[2]/text()').getall())
                rating = self.get_rating(home_selector)
                review_count = self.get_review_count(home_selector)
                price = self.get_price(home_selector)
                is_new = True if home_selector.xpath('.//span[@class="_1p2weln"][contains(., "NEW")]').get() is not None else False
                is_superhost = True if home_selector.xpath('.//span[@class="_1a31dx8f"][contains(., "SUPERHOST")]').get() is not None else False
                image = self.get_image(home_selector)
                detail_page = self.driver.find_element_by_xpath('(//div[@class="_8ssblpx"])[' + str(index + 1) +']//a').get_attribute('href')
                home_item = AirbnbScrapeItem(home_type = home_type, description = description, room = room, amenity = amenity, rating = rating, review_count = review_count,\
                                             price = price, is_new = is_new, is_superhost = is_superhost, image = image, detail_page = detail_page)
                self.logger.debug('scrape a home item ' + str(home_item))
                yield home_item
            self.logger.info('finish scraping page ' + str(page_number))

            ## if reach max page stop scraping
            if hasattr(self, 'max_page_number') and page_number == int(self.max_page_number):
                break

            ## navigate to next apge
            try:
                self.driver.get(self.driver.find_element_by_xpath('//li[not(@data-id)][@class="_i66xk8d"]/a').get_attribute('href'))
                self.logger.info('navigated to next page')
                sleep(WAIT_FOR_PAGE_LOADING_TIME)
                page_number += 1
            except Exception as e:
##                self.logger.debug('check next button')
##                sel = Selector(text=self.driver.page_source)
##                self.logger.debug(sel.xpath('//ul[@class="_11hau3k"]/li[last()]').get())
                self.logger.error('navigate to next page fail ' + str(e))
                break
    	
        self.close_driver()

	
