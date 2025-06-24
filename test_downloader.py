#!/usr/bin/env python3
"""
Script de test pour le Téléchargeur de postulats VD
Teste l'accessibilité du site web et l'extraction des liens PDF.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import *
from downloader import TelechargeurPostulatsVD


def test_website_accessibility():
    """Teste l'accessibilité du site web cible."""
    print("🔍 Test d'accessibilité du site web...")
    
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        
        response = session.get(TARGET_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        print(f"✅ Site web accessible (Status: {response.status_code})")
        return response.text
    except requests.RequestException as e:
        print(f"❌ Erreur d'accès au site web : {e}")
        return None


def test_pdf_link_extraction(html_content):
    """Teste l'extraction des liens PDF."""
    print("🔍 Test d'extraction des liens PDF...")
    
    if not html_content:
        print("❌ Pas de contenu HTML à analyser")
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = f"{urlparse(TARGET_URL).scheme}://{urlparse(TARGET_URL).netloc}"
        
        # Find all links
        links = soup.find_all('a', href=True)
        pdf_links = []
        
        for link in links:
            href = link.get('href')
            if href:
                # Check if the link contains any of the search keywords
                href_upper = href.upper()
                if any(keyword.upper() in href_upper for keyword in SEARCH_KEYWORDS):
                    # Check if it's a PDF or has a PDF-like structure
                    if any(ext.lower() in href.lower() for ext in FILE_EXTENSIONS) or 'pdf' in href.lower():
                        full_url = urljoin(base_url, href)
                        pdf_links.append(full_url)
        
        print(f"✅ {len(pdf_links)} liens PDF trouvés contenant les mots-clés {SEARCH_KEYWORDS}")
        
        if pdf_links:
            print("📋 Liens trouvés :")
            for i, link in enumerate(pdf_links[:5], 1):  # Show first 5 links
                print(f"   {i}. {link}")
            if len(pdf_links) > 5:
                print(f"   ... et {len(pdf_links) - 5} autres")
        
        return pdf_links
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des liens : {e}")
        return []


def test_pdf_urls_accessibility(pdf_links):
    """Teste l'accessibilité des URLs PDF trouvées."""
    print("🔍 Test d'accessibilité des URLs PDF...")
    
    if not pdf_links:
        print("❌ Aucun lien PDF à tester")
        return
    
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    
    accessible_count = 0
    total_count = min(len(pdf_links), 3)  # Test only first 3 URLs
    
    for i, pdf_url in enumerate(pdf_links[:3], 1):
        try:
            print(f"   Test {i}/{total_count} : {pdf_url}")
            response = session.head(pdf_url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or pdf_url.lower().endswith('.pdf'):
                    print(f"   ✅ Accessible (Content-Type: {content_type})")
                    accessible_count += 1
                else:
                    print(f"   ⚠️  Accessible mais pas un PDF (Content-Type: {content_type})")
            else:
                print(f"   ❌ Non accessible (Status: {response.status_code})")
                
        except requests.RequestException as e:
            print(f"   ❌ Erreur d'accès : {e}")
    
    print(f"📊 Résumé : {accessible_count}/{total_count} URLs PDF accessibles")


def main():
    """Fonction principale du script de test."""
    print("🧪 Test du Téléchargeur de postulats VD")
    print("=" * 50)
    print(f"URL cible : {TARGET_URL}")
    print(f"Mots-clés de recherche : {SEARCH_KEYWORDS}")
    print(f"Extensions de fichiers : {FILE_EXTENSIONS}")
    print()
    
    # Test 1: Website accessibility
    html_content = test_website_accessibility()
    print()
    
    # Test 2: PDF link extraction
    pdf_links = test_pdf_link_extraction(html_content)
    print()
    
    # Test 3: PDF URLs accessibility
    test_pdf_urls_accessibility(pdf_links)
    print()
    
    # Summary
    print("=" * 50)
    if html_content and pdf_links:
        print("🎉 Tous les tests sont passés ! L'application devrait fonctionner correctement.")
        print("💡 Vous pouvez maintenant lancer : python downloader.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez votre connexion internet et l'URL cible.")
        print("💡 Consultez les messages d'erreur ci-dessus pour plus de détails.")


if __name__ == "__main__":
    main() 