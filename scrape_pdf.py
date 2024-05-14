import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

# Extrahiere PDF-Links
def scrape_pdf_links_from_html(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_links = []
    for area_tag in soup.find_all('area', href=True):
        href = area_tag['href']
        if href.endswith('.pdf'):
            pdf_links.append(href)
        else:
            abs_url = urljoin(url, href)
            abs_url_parsed = urlparse(abs_url)
            if abs_url_parsed.path.endswith('.pdf'):
                pdf_links.append(abs_url)
    return pdf_links


# Lade Dateien herunter
def download_pdf(url, folder):
    try:
        if not url.startswith("https://www.euforbih.org/"):
            url = "https://www.euforbih.org" + url  # Vor PDF-Link setzen
        filename = os.path.join(folder, url.split("/")[-1])
        response = requests.get(url, timeout=120)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"PDF heruntergeladen: {filename}")
    except Exception as e:
        print(f"Fehler beim Herunterladen der PDF von {url}: {e}")


# Scrapen der PDFs und Herunterladen
def scrape_pdfs_from_website(website_url, download_folder):
    try:
        response = requests.get(website_url, timeout=120)
        pdf_links = scrape_pdf_links_from_html(response.content, website_url)
        
        # Ausgabe Liste aller PDF-Dokumente
        print("Liste aller PDF-Dokumente:")
        for pdf_link in pdf_links:
            print(pdf_link)
        
        # Herunterladen 
        for pdf_link in pdf_links:
            download_pdf(pdf_link, download_folder)
    except Exception as e:
        print(f"Fehler beim Abrufen der Website {website_url}: {e}")

# Aufruf
website_url = "https://www.euforbih.org/index.php/bih-minefield-maps"
download_folder = "pdfDateien"
scrape_pdfs_from_website(website_url, download_folder)