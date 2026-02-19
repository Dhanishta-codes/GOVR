"""Email finder tools - Apollo.io and Hunter.io integration"""
import requests
import agent.infra.config as config
from typing import Optional, Dict, List


def find_email_apollo(first_name: str, last_name: str, company_domain: str) -> Optional[Dict]:
    """
    Find email using Apollo.io API
    
    Args:
        first_name: Person's first name
        last_name: Person's last name
        company_domain: Company domain (e.g., 'stripe.com')
        
    Returns:
        Dictionary with email and confidence, or None
    """
    if not config.APOLLO_API_KEY:
        return None
    
    url = "https://api.apollo.io/v1/people/match"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": config.APOLLO_API_KEY
    }
    
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "organization_name": company_domain.replace('.com', '').replace('.io', '')
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            person = result.get('person', {})
            
            email = person.get('email')
            if email:
                return {
                    "email": email,
                    "source": "apollo",
                    "confidence": "high",
                    "linkedin": person.get('linkedin_url'),
                    "title": person.get('title')
                }
        
        return None
        
    except Exception as e:
        print(f"Apollo API error: {str(e)}")
        return None


def find_email_hunter(first_name: str, last_name: str, company_domain: str) -> Optional[Dict]:
    """
    Find email using Hunter.io API
    
    Args:
        first_name: Person's first name
        last_name: Person's last name
        company_domain: Company domain (e.g., 'stripe.com')
        
    Returns:
        Dictionary with email and confidence, or None
    """
    if not config.HUNTER_API_KEY:
        return None
    
    url = "https://api.hunter.io/v2/email-finder"
    
    params = {
        "domain": company_domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": config.HUNTER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            email = data.get('email')
            if email:
                return {
                    "email": email,
                    "source": "hunter",
                    "confidence": data.get('confidence'),
                    "score": data.get('score')
                }
        
        return None
        
    except Exception as e:
        print(f"Hunter API error: {str(e)}")
        return None


def get_company_domain_from_name(company_name: str) -> Optional[str]:
    """
    Try to guess company domain from name
    Simple heuristic - in production, use Clearbit or similar
    
    Args:
        company_name: Company name (e.g., "Stripe")
        
    Returns:
        Likely domain (e.g., "stripe.com")
    """
    # Simple mapping for common companies
    common_domains = {
        "stripe": "stripe.com",
        "shopify": "shopify.com",
        "notion": "notion.so",
        "slack": "slack.com",
        "zoom": "zoom.us",
        "salesforce": "salesforce.com",
        "hubspot": "hubspot.com",
        "mailchimp": "mailchimp.com",
        "asana": "asana.com",
        "atlassian": "atlassian.com"
    }
    
    name_lower = company_name.lower().strip()
    
    # Check common mappings
    if name_lower in common_domains:
        return common_domains[name_lower]
    
    # Try basic heuristic
    # Remove common words
    name_clean = name_lower.replace('inc.', '').replace('llc', '').replace('ltd', '').strip()
    
    # Take first word if multiple
    first_word = name_clean.split()[0] if ' ' in name_clean else name_clean
    
    return f"{first_word}.com"


def find_contact_email(first_name: str, last_name: str, company_name: str) -> Optional[Dict]:
    """
    Find email using multiple sources
    Tries Apollo first, then Hunter
    
    Args:
        first_name: Person's first name
        last_name: Person's last name  
        company_name: Company name
        
    Returns:
        Best email result found, or None
    """
    # Get company domain
    domain = get_company_domain_from_name(company_name)
    
    print(f"🔍 Looking for email: {first_name} {last_name} @ {domain}")
    
    # Try Apollo first (better for B2B)
    apollo_result = find_email_apollo(first_name, last_name, domain)
    if apollo_result:
        print(f"✅ Found via Apollo: {apollo_result['email']}")
        return apollo_result
    
    # Try Hunter
    hunter_result = find_email_hunter(first_name, last_name, domain)
    if hunter_result:
        print(f"✅ Found via Hunter: {hunter_result['email']}")
        return hunter_result
    
    print(f"❌ No email found")
    return None


def search_people_at_company(company_name: str, titles: List[str] = None) -> List[Dict]:
    """
    Search for people at a company with specific titles using Apollo
    
    Args:
        company_name: Company name to search
        titles: List of job titles to search for
        
    Returns:
        List of people with contact info
    """
    if not config.APOLLO_API_KEY:
        return []
    
    if titles is None:
        titles = config.ICP_CRITERIA['decision_maker_titles']
    
    url = "https://api.apollo.io/v1/mixed_people/search"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": config.APOLLO_API_KEY
    }
    
    # Build title query
    title_query = " OR ".join([f'"{title}"' for title in titles[:3]])  # Limit to 3 titles
    
    data = {
        "q_organization_name": company_name,
        "person_titles": titles[:3],
        "page": 1,
        "per_page": 5  # Get top 5 matches
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            people = result.get('people', [])
            
            contacts = []
            for person in people:
                contacts.append({
                    "first_name": person.get('first_name'),
                    "last_name": person.get('last_name'),
                    "name": person.get('name'),
                    "title": person.get('title'),
                    "email": person.get('email'),
                    "linkedin": person.get('linkedin_url'),
                    "company": company_name
                })
            
            return contacts
        
        return []
        
    except Exception as e:
        print(f"Apollo search error: {str(e)}")
        return []
