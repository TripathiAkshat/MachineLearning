from bs4 import BeautifulSoup
import requests
html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=ft&searchTextText=&txtKeywords=python&cboWorkExp1=0&txtLocation=')
data = html_text.text
soup = BeautifulSoup(data, 'lxml')
jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

for job in jobs:
    job_title = job.find('h2', class_='heading-trun').text
    print("Job Title: ", job_title.strip())
    company_name = job.find('h3', class_='joblist-comp-name').text
    print("Company Name: ", company_name.strip())
    skills = job.find('div', class_='more-skills-sections').text
    print("Skills: ", skills.strip().split())
    location = job.find('li', class_='srp-zindex location-tru').text
    print("Location: ", location.strip().split())
    print()
