from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import os
import re

import html2text

def html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    markdown_content = h.handle(html_content)
    return markdown_content

def replace_newline(match):
    return match.group(1) + " " + match.group(3)

data = []

s=Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=s)

url = 'https://cyprus-faq.com/ru/north/'
driver.get(url)

elements = driver.find_elements(By.CLASS_NAME,'section-title')


driver.set_window_size(1500, 1000)

subdriver = webdriver.Chrome(service=s)
subdriver.set_window_size(1500, 1000)
subpage_driver = webdriver.Chrome(service=s)
subpage_driver.set_window_size(1500, 1000)
for element in elements:

    group_link = element.find_element(By.TAG_NAME, 'a')
    subdriver.get(group_link.get_property('href'))
    group_bodies = subdriver.find_elements(By.CLASS_NAME, 'section-body')
    output = ''
    for group_body in group_bodies:
        output += html_to_markdown(group_body.get_attribute('outerHTML'))
    output = output.replace('](/', '](https://cyprus-faq.com/')
    output = output.replace('https: /', 'https:/')
    output = output.replace('-\n', '-')
    output = re.sub(r"(\w)(\n)(\w)", replace_newline, output)

    dir_name = group_link.text
    if not os.path.exists('pages/'+dir_name):
        os.makedirs('pages/'+dir_name)
        

    subpages = []
    links = subdriver.find_elements(By.CSS_SELECTOR, '.section-body .list .link-short')
    for link in links:
        subpage_driver.get(link.get_property('href'))
        subpage_bodies = subpage_driver.find_elements(By.CSS_SELECTOR, 'article.flow>div')
        subpage_output = ''
        for subpage_body in subpage_bodies:
            
            if subpage_body.get_attribute('class') == 'section-body':
                subpage_output += html_to_markdown(subpage_body.get_attribute('outerHTML'))
            elif subpage_body.get_attribute('class') == 'section-copyright':
                break
            elif subpage_body.get_attribute('class') == 'section-header' or subpage_body.get_attribute('class') == 'section-description':
                continue
            else:
                print(subpage_body.get_attribute('class'))
                subpage_output += "\n *** ЧТО-ТО СТРАННОЕ *** \n"
        
        subpage_output = subpage_output.replace('](/', '](https://cyprus-faq.com/')
        subpage_output = subpage_output.replace('https: /', 'https:/')
        subpage_output = subpage_output.replace('-\n', '-')
        subpage_output = re.sub(r"(\w)(\n)(\w)", replace_newline, subpage_output)

        subpages.append(
            {
                'link': link.get_property('href'),
                'body': subpage_output,
            }
        )
        file_name = link.text + '.md'
        with open(os.path.join('pages/'+dir_name, file_name), 'w') as f:
            f.write(subpage_output)

    data.append({
        'link': group_link.get_property('href'),
        'body': output,
        'pages': subpages,
    })

with open('out.json', 'w') as file:
    file.write(json.dumps(data).encode().decode('unicode_escape'))    


driver.quit()

