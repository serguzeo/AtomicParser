import csv
import os

from selenium import webdriver
import time
from bs4 import BeautifulSoup
from initLoad import initial_load


class AtomicParser:

    def __init__(self, domain: str = ""):
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.options)
        self.domain = domain if domain else "https://pris.iaea.org"

    def get_page(self, suffix: str) -> str:
        self.driver.get(self.domain + suffix)
        time.sleep(1)

        return self.driver.page_source

    def get_countries(self) -> list:
        soup = self.get_soup(
            self.get_page("/PRIS/CountryStatistics/CountryStatisticsLandingPage.aspx")
        )
        countries = soup.find_all('a', id=lambda x: x and 'MainContent_rptSideNavigation_hypNavigation' in x)

        return [[country.text, country['href']] for country in countries]

    def get_country_reactors(self, country_name, country_prefix) -> list:
        js_reactors = []

        self.driver.get(self.domain + country_prefix)
        time.sleep(1)

        soup = self.get_soup(self.driver.page_source)

        reactor_table = soup.find('table', class_='tablesorter')
        if reactor_table:
            rows = reactor_table.find_all('tr')

            for row in rows[1:]:
                cells = row.find_all('td')
                status = cells[2].get_text(strip=True)

                if status in {'Operational', 'Permanent Shutdown', 'Suspended Operation'}:
                    reactor_link = cells[0].find('a')['href']

                    js_reactors.append(reactor_link)

        for js_link in js_reactors:
            self.driver.execute_script(js_link)  # open reactor's page

            soup = self.get_soup(self.driver.page_source)

            table_rows = soup.select("table.layout tbody tr")

            fgc = soup.find("span", id="MainContent_MainContent_lblGridConnectionDate").text.strip()
            sd = soup.find("span", id="MainContent_MainContent_lblLongTermShutdownDate").text.strip()
            psd = soup.find("span", id="MainContent_MainContent_lblPermanentShutdownDate").text.strip()
            reactor = {
                "country": country_name,
                "name": soup.find("span", id="MainContent_MainContent_lblReactorName").text.strip(),
                "type": soup.find("span", id="MainContent_MainContent_lblType").text.strip(),
                "owner": table_rows[1].find_all("td")[-2].text.strip().split(',')[0],
                "operator": table_rows[1].find_all("td")[-1].text.strip(),
                "status": soup.find("span", id="MainContent_MainContent_lblReactorStatus").text.strip(),
                "thermalCapacity": soup.find("span", id="MainContent_MainContent_lblThermalCapacity").text.strip(),
                "firstGridConnection": fgc.split()[-1] if fgc else fgc,
                "suspendedDate": sd.split()[-1] if sd else sd,
                "permanentShutdownDate": psd.split()[-1] if psd else psd,
                "loadFactor": {str(year): 0 for year in range(2014, 2024 + 1)}
            }

            table = soup.find('table', class_='active')
            self.set_load_factor(reactor, table)

            self.write_reactor(reactor, filename="../out/reactors.csv")
            self.write_load_factor(reactor["name"], reactor["loadFactor"], filename="../out/loadFactors.csv")
            self.driver.back()

        return js_reactors

    @staticmethod
    def get_soup(page: str) -> BeautifulSoup:
        soup = BeautifulSoup(page, 'html.parser')

        return soup

    @staticmethod
    def set_load_factor(reactor, table) -> None:
        table_rows = table.find_all('tr')

        fgc = reactor["firstGridConnection"]
        sd = reactor["suspendedDate"]
        psd = reactor["permanentShutdownDate"]

        for row in table_rows:
            cells = row.find_all('td')

            if len(cells) > 1:
                year = cells[0].get_text().strip()

                if sd and year > sd or psd and year > psd:
                    break

                load_factor_value = float(cells[-2].get_text().strip()) if cells[-2].get_text().strip() else 0

                if year in reactor["loadFactor"]:
                    reactor["loadFactor"][year] = load_factor_value

        if 2014 <= int(fgc) <= 2024:
            reactor["loadFactor"][fgc] = initial_load[reactor["type"]]

    @staticmethod
    def write_reactor(reactor, filename) -> None:
        out_folder = os.path.dirname(filename)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([
                reactor["country"],
                reactor["name"],
                reactor["type"],
                reactor["owner"],
                reactor["operator"],
                reactor["status"],
                reactor["thermalCapacity"],
                reactor["firstGridConnection"],
                reactor["suspendedDate"],
                reactor["permanentShutdownDate"]
            ])

    @staticmethod
    def write_load_factor(reactor_name, load_factor, filename) -> None:
        out_folder = os.path.dirname(filename)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            for year, factor in load_factor.items():
                writer.writerow([reactor_name, year, factor])


if __name__ == "__main__":
    parser = AtomicParser()
    countries = parser.get_countries()

    for country in countries:
        parser.get_country_reactors(*country)
