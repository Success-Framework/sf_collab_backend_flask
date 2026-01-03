import os
import requests
from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging

# Create blueprint
scraper_bp = Blueprint('scraper', __name__)

def standard_response(success=True, data=None, error=None, code=200):
    response = jsonify({
        'success': success,
        'data': data,
        'error': error
    })
    return response, code

def scrape_page(url, dynamic=False):
    """Scrape a webpage and extract content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Extract title
        title = soup.title.string if soup.title else None
        
        # Extract headings
        h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
        
        # Extract links (limit to first 50)
        links = []
        for a in soup.find_all('a', href=True)[:50]:
            href = a['href']
            # Make relative URLs absolute
            if not href.startswith(('http://', 'https://')):
                href = urljoin(url, href)
            links.append({
                'text': a.get_text(strip=True)[:100],  # Limit text length
                'href': href
            })
        
        # Extract meta description
        meta_desc = None
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content')
        
        # Extract paragraphs (first 5)
        paragraphs = [p.get_text(strip=True)[:500] for p in soup.find_all('p')[:5] if p.get_text(strip=True)]
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True)[:20]:
            src = img['src']
            if not src.startswith(('http://', 'https://')):
                src = urljoin(url, src)
            images.append({
                'src': src,
                'alt': img.get('alt', '')
            })
        
        return {
            'url': url,
            'title': title,
            'meta': {
                'domain': domain,
                'description': meta_desc,
                'total_links': len(soup.find_all('a', href=True)),
                'total_h1': len(h1_tags),
                'total_h2': len(h2_tags),
                'total_images': len(soup.find_all('img', src=True)),
                'total_paragraphs': len(soup.find_all('p'))
            },
            'headings': {
                'h1': h1_tags,
                'h2': h2_tags[:20]  # Limit h2 to 20
            },
            'links': links,
            'paragraphs': paragraphs,
            'images': images
        }
        
    except requests.exceptions.Timeout:
        raise Exception('Request timeout - the page took too long to load')
    except requests.exceptions.RequestException as e:
        raise Exception(f'Failed to fetch URL: {str(e)}')
    except Exception as e:
        raise Exception(f'Scraping error: {str(e)}')


# ============================================================
# SCRAPER ROUTES
# ============================================================

@scraper_bp.route('/scrape-static', methods=['POST'])
def scrape_static():
    """Static scraping using BeautifulSoup"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return standard_response(False, None, 'Missing URL in request', 400)
        
        url = data.get('url', '').strip()
        
        # Validate URL
        if not url:
            return standard_response(False, None, 'URL cannot be empty', 400)
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Scrape the page
        result = scrape_page(url, dynamic=False)
        
        return standard_response(True, result)
        
    except Exception as e:
        logging.error(f'Static scraping error: {str(e)}')
        return standard_response(False, None, str(e), 500)


@scraper_bp.route('/scrape-dynamic', methods=['POST'])
def scrape_dynamic():
    """
    Dynamic scraping - for now uses same method as static.
    For full dynamic support, you'd need Playwright or Selenium.
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return standard_response(False, None, 'Missing URL in request', 400)
        
        url = data.get('url', '').strip()
        
        # Validate URL
        if not url:
            return standard_response(False, None, 'URL cannot be empty', 400)
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # For now, use static scraping
        # TODO: Implement Playwright for true dynamic scraping
        result = scrape_page(url, dynamic=True)
        
        return standard_response(True, result)
        
    except Exception as e:
        logging.error(f'Dynamic scraping error: {str(e)}')
        return standard_response(False, None, str(e), 500)


@scraper_bp.route('/scraper/health', methods=['GET'])
def scraper_health():
    """Health check for scraper"""
    return standard_response(True, {
        'status': 'ready',
        'methods': ['static', 'dynamic'],
        'version': '1.0.0'
    })
