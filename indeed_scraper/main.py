from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time
from pandasgui import show

# Base URL for job search
base_url = "https://www.indeed.com/jobs?q=python+developer&start="

# Initialize WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


def get_element_text(locator, backup_locator=None, multiple=False):
    """
    Helper function to get the text of an element or multiple elements.
    """
    try:
        if multiple:
            elements = driver.find_elements(*locator)
            return [el.text for el in elements if el.text]
        element = driver.find_element(*locator)
        return element.text
    except Exception:
        if backup_locator is not None:
            get_element_text(backup_locator, None, multiple)
        return None


def scrape_page(job_url):
    """
    Scrapes detailed information from a single job posting page.
    """
    driver.get(job_url)

    try:
        # Wait for the job page to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@data-testid='simpler-jobTitle']")))

        # Extract job details
        title = get_element_text((By.XPATH, "//h2[@data-testid='simpler-jobTitle']"))
        company = get_element_text((By.XPATH, "//span[@class='jobsearch-JobInfoHeader-companyNameSimple']"),
                                   (By.XPATH, "//h2[@class='jobsearch-CompanyReview--heading']"))
        location = get_element_text((By.XPATH, "//div[@data-testid='jobsearch-JobInfoHeader-companyLocation']//div"),
                                    (By.XPATH, "//div[@data-testid='jobsearch-JobInfoHeader-companyLocation']//span"))
        salary = get_element_text((By.XPATH, "//span[@class='js-match-insights-provider-4pmm6z']"))

        # Return job details, with missing fields replaced by empty strings or NaN
        return {
            "Title": title if title else "",
            "Company": company if company else "",
            "Location": location if location else "",
            "Salary": salary if salary else "",
        }
    except Exception as ex:
        print(f"Error scraping job page: {ex}")
        return None


def get_list_of_jobs(url):
    """
    Fetches the list of job postings from a search result page.
    """
    driver.get(url)

    # Wait for job listings to appear
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='job_seen_beacon']")))

    # Find all job links with 'data-jk' attribute
    vjk_elements = driver.find_elements(By.XPATH, "//div[@class='job_seen_beacon']//a[@data-jk]")
    vjk_list = [vjk.get_attribute('data-jk') for vjk in vjk_elements]
    return vjk_list


def get_jobs_detailed():
    """
    Main function to scrape multiple pages of job postings.
    """
    all_jobs_detailed = []

    for page in range(0, 10, 10):
        print(f"Scraping page {page}")
        page_url = f"{base_url}{page}"

        # Get the list of job links (vjk)
        vjk_list = get_list_of_jobs(page_url)

        if vjk_list:
            for vjk in vjk_list:
                job_url = f"https://www.indeed.com/viewjob?jk={vjk}"
                print(f"Scraping job URL: {job_url}")

                # Scrape details for each job
                job_details = scrape_page(job_url)
                if job_details:
                    all_jobs_detailed.append(job_details)

        time.sleep(2)  # Delay between requests

    # Close the WebDriver
    driver.quit()
    return all_jobs_detailed


def scrape():
    # Scrape job data and store it in a DataFrame
    job_data = get_jobs_detailed()

    # Ensure the job_data is a valid list of dictionaries
    if job_data:
        df = pd.DataFrame(job_data)
        # Save to CSV file
        df.to_csv("jobs.csv", index=False)
    else:
        print("No job data scraped.")

print(scrape_page("https://www.indeed.com/viewjob?jk=8f93f49c653ed7b8"))