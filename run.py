from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pickle
import os

URLS = [
  'https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/detail/44665',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/detail/44666',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/detail/44667',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/detail/44668',
]

URLS2 = [
  'https://www.vaccine.mrso.jp/sdftokyo/CustomReserves/input/44665/894',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomReserves/input/44666/894',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomReserves/input/44667/894',
  'https://www.vaccine.mrso.jp/sdftokyo/CustomReserves/input/44668/894',
]

def login(driver, config):
  driver.get('https://www.vaccine.mrso.jp/sdftokyo/VisitNumbers/visitnoAuth/')
  print(driver.title)
  assert(driver.title == '自衛隊東京 | 予約システム')

  element = driver.find_element_by_name("data[VisitnoAuth][name]")
  element.send_keys(config['CODE'])
  element = driver.find_element_by_name("data[VisitnoAuth][visitno]")
  element.send_keys(config['NUMBER'])
  element =Select( driver.find_element_by_name("data[VisitnoAuth][year]"))
  element.select_by_value(config['BIRTH_YEAR'])
  element = Select(driver.find_element_by_name("data[VisitnoAuth][month]"))
  element.select_by_value(config['BIRTH_MONTH'])
  element = Select(driver.find_element_by_name("data[VisitnoAuth][day]"))
  element.select_by_value(config['BIRTH_DAY'])

  element = driver.find_element_by_css_selector("button[type='submit'].btn.btn-warning.auth-btn.center-block")
  element.click()

  print(driver.title)
  assert(driver.title == '接種者情報確認 |自衛隊東京')
  element = driver.find_element_by_css_selector("button[type='submit'].btn.btn-warning.btn-next.center-block")
  element.click()

  print(driver.title)
  assert(driver.title == '接種会場一覧 | 自衛隊東京')

def search(driver, repeat=True):
  URL = 'https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/visit'
  if driver.current_url != URL:
    driver.get(URL)

  element = driver.find_element_by_name("data[res_from]")
  element.send_keys('2021-06-24')

  element = driver.find_element_by_name("data[res_to]")
  element.send_keys('2021-06-30')

  while True:
    element = driver.find_element_by_css_selector("input[type='submit'].btn.btn-info.search-btn")
    element.click()

    print(driver.title)
    assert(driver.title == '接種会場一覧 | 自衛隊東京')

    elements = driver.find_elements_by_css_selector("div.alert.alert-warning.err-msg")
    if len(elements) == 0:
      print('ok')
      break

    if repeat:
      time.sleep(1)
    else:
      break

  # btn btn-lg btn-next btn-warning covid19_move_plan_detail" role="button"
  element = driver.find_element_by_css_selector("a[role='button'].btn.btn-lg.btn-next.btn-warning.covid19_move_plan_detail")
  element.click()

  reserve(driver)

def search2(driver):
  while True:
    for url in URLS:
      driver.get(url)
      assert(driver.title == '会場詳細 | 自衛隊東京')
      ret = reserve(driver)

      if ret:
        return
      time.sleep(1)

def search3(driver):
  while True:
    for url in URLS2:
      driver.get(url)
      assert(driver.title == '予約内容入力 | 自衛隊東京')
      ret = reserve2(driver)

      if ret:
        return
      time.sleep(1)

def reserve(driver):
  #print(driver.title)
  assert(driver.title == '会場詳細 | 自衛隊東京')
  element = driver.find_element_by_css_selector("h2")
  print(element.text)

  elements = driver.find_elements_by_partial_link_text("△")
  if len(elements) == 0:
    return False

  elements[0].click()
  return reserve2(driver)

def reserve2(driver):
  print(driver.title)
  print(driver.current_url)
  assert(driver.title == '予約内容入力 | 自衛隊東京')

  elements = driver.find_elements_by_css_selector("div.panel-heading.text-center")
  for element in elements:
    if element.text == '選択された日付の予約は既に埋まっております。':
      print('ng')
      return False

  elements = driver.find_elements_by_partial_link_text("(残り")
  assert(len(elements) != 0)
  elements[0].click()

  print(driver.title)
  print(driver.current_url)

  elements = driver.find_elements_by_css_selector("td.planDate")
  if len(elements) != 0:
    print(elements[0].text)

  elements = driver.find_elements_by_css_selector("div.panel-heading.text-center")
  for element in elements:
    if element.text == '選択された日付の予約は既に埋まっております。':
      print('ng')
      return False

  element = driver.find_element_by_css_selector("button.btn.btn-lg.btn-warning.center-block.btn-next")
  #  <button type="submit" class="btn btn-lg btn-warning center-block btn-next">予約内容確認</button>
  element.click()

  print(driver.title)
  print(driver.current_url)

  # <button type="submit" class="btn btn-lg btn-warning btn-block center-block btn-next">
  element = driver.find_element_by_css_selector("button[type='submit'].btn.btn-lg.btn-warning.btn-block.center-block.btn-next")
  element.click()

  driver.save_screenshot('screen_shot.png')
  with open('soure.txt', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

  return True

def main(driver):
  json_file = open('config.json', 'r')
  config = json.load(json_file)

  driver.get('https://www.vaccine.mrso.jp/sdftokyo/CustomPlans/visit')
  print(driver.title)
  if driver.title != '接種会場一覧 | 自衛隊東京':
    login(driver, config)

  search2(driver)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--user-data-dir=chrome-data")
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1024, 1024)

main(driver)
driver.quit()
