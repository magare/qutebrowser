# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Social Media & People Intelligence (SOCMINT) features for qutebrowser.

This module is loaded automatically as a component.
"""

import re
import urllib.parse
from typing import Optional, List, Dict

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


# Platform search URL templates
PLATFORM_SEARCH_URLS = {
    'twitter': 'https://twitter.com/search?q={}',
    'x': 'https://x.com/search?q={}',
    'instagram': 'https://www.instagram.com/{}/',
    'facebook': 'https://www.facebook.com/search/top/?q={}',
    'linkedin': 'https://www.linkedin.com/search/results/all/?keywords={}',
    'github': 'https://github.com/search?q={}',
    'reddit': 'https://www.reddit.com/search/?q={}',
    'youtube': 'https://www.youtube.com/results?search_query={}',
    'tiktok': 'https://www.tiktok.com/search?q={}',
    'snapchat': 'https://www.snapchat.com/add/{}',
    'telegram': 'https://t.me/{}',
    'discord': 'https://discord.com/users/{}',
    'twitch': 'https://www.twitch.tv/search?term={}',
    'pinterest': 'https://www.pinterest.com/search/users/?q={}',
    'vk': 'https://vk.com/search?c%5Bq%5D={}',
    'tumblr': 'https://www.tumblr.com/search/{}',
    'medium': 'https://medium.com/search?q={}',
    'quora': 'https://www.quora.com/search?q={}',
    'stackoverflow': 'https://stackoverflow.com/users?tab=users&filter=all&search={}',
    'behance': 'https://www.behance.net/search/users?search={}',
    'dribbble': 'https://dribbble.com/search/{}',
    'deviantart': 'https://www.deviantart.com/search?q={}',
    'flickr': 'https://www.flickr.com/search/people/?q={}',
    'soundcloud': 'https://soundcloud.com/search/people?q={}',
    'spotify': 'https://open.spotify.com/search/{}',
    'lastfm': 'https://www.last.fm/search?q={}',
    'goodreads': 'https://www.goodreads.com/search?q={}',
    'yelp': 'https://www.yelp.com/search?find_desc={}',
    'tripadvisor': 'https://www.tripadvisor.com/Search?q={}',
    'airbnb': 'https://www.airbnb.com/s/homes?query={}',
    'etsy': 'https://www.etsy.com/search?q={}',
    'ebay': 'https://www.ebay.com/sch/i.html?_nkw={}',
    'amazon': 'https://www.amazon.com/s?k={}',
    'alibaba': 'https://www.alibaba.com/trade/search?SearchText={}',
    'taobao': 'https://s.taobao.com/search?q={}',
    'weibo': 'https://s.weibo.com/user?q={}',
    'wechat': 'https://weixin.sogou.com/weixin?type=2&query={}',
    'douyin': 'https://www.douyin.com/search/{}',
    'bilibili': 'https://search.bilibili.com/all?keyword={}',
    'zhihu': 'https://www.zhihu.com/search?q={}',
    'baidu': 'https://www.baidu.com/s?wd={}',
    'yandex': 'https://yandex.com/search/?text={}',
    'duckduckgo': 'https://duckduckgo.com/?q={}',
    'bing': 'https://www.bing.com/search?q={}',
    'google': 'https://www.google.com/search?q={}',
}

# Reverse lookup service URLs
REVERSE_LOOKUP_URLS = {
    'truecaller': 'https://www.truecaller.com/search/{}',
    'whitepages': 'https://www.whitepages.com/phone/{}',
    'whocalld': 'https://whocalld.com/{}',
    'reverse-phone-lookup': 'https://www.reversephonelookup.com/number/{}',
    'spydialer': 'https://www.spydialer.com/results.aspx?stype=CellPhone&s1={}',
    'zlookup': 'https://www.zlookup.com/{}',
    'thatsthem': 'https://thatsthem.com/phone/{}',
    'beenverified': 'https://www.beenverified.com/phone/{}',
    'spokeo': 'https://www.spokeo.com/search?q={}',
    'pipl': 'https://pipl.com/search/?q={}',
    'peoplesearch': 'https://www.peoplesearch.com/phone-lookup/{}',
    'intelius': 'https://www.intelius.com/phone-lookup/{}',
    'instantcheckmate': 'https://www.instantcheckmate.com/phone-lookup/{}',
    'peoplewhiz': 'https://www.peoplewhiz.com/phone/{}',
    'usphonebook': 'https://www.usphonebook.com/{}',
    'fastpeoplesearch': 'https://www.fastpeoplesearch.com/phone/{}',
    'peoplebyname': 'https://www.peoplebyname.com/phone/{}',
    'peoplelooker': 'https://www.peoplelooker.com/phone-lookup/{}',
    'truthfinder': 'https://www.truthfinder.com/reverse-phone-lookup/{}',
    'publicrecords': 'https://www.publicrecords.com/phone/{}',
}

# Social media contact sync URLs (for manual sync preparation)
SYNC_PREP_URLS = {
    'google_contacts': 'https://contacts.google.com/',
    'facebook_find': 'https://www.facebook.com/friends/requests/mobile/',
    'instagram_discover': 'https://www.instagram.com/explore/people/',
    'twitter_contacts': 'https://twitter.com/i/contacts',
    'linkedin_connections': 'https://www.linkedin.com/mynetwork/import-contacts/',
    'snapchat_add': 'https://accounts.snapchat.com/accounts/friends',
    'telegram_contacts': 'https://web.telegram.org/#/im?p=@contacts',
    'whatsapp_web': 'https://web.whatsapp.com/',
    'discord_friends': 'https://discord.com/channels/@me',
    'signal_contacts': 'https://signal.org/download/',
}

def _sanitize_identifier(identifier: str) -> str:
    """Sanitize an identifier for use in URLs."""
    # Remove @ symbols commonly used in social media handles
    identifier = identifier.lstrip('@')
    # Remove common phone number formatting  
    identifier = re.sub(r'[^\w\s@.\-]', '', identifier)
    return identifier.strip()

def _format_phone_number(phone: str) -> Dict[str, str]:
    """Format phone number in various formats for different services."""
    # Remove all non-numeric characters
    digits = re.sub(r'\D', '', phone)
    
    formats = {
        'digits': digits,
        'dashed': '',
        'dotted': '',
        'spaced': '',
        'international': '',
        'parentheses': ''
    }
    
    # US phone number formatting (10 digits)
    if len(digits) == 10:
        formats['dashed'] = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        formats['dotted'] = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        formats['spaced'] = f"{digits[:3]} {digits[3:6]} {digits[6:]}"
        formats['parentheses'] = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        formats['international'] = f"+1{digits}"
    elif len(digits) == 11 and digits[0] == '1':
        # US number with country code
        digits = digits[1:]
        formats['dashed'] = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        formats['dotted'] = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        formats['spaced'] = f"{digits[:3]} {digits[3:6]} {digits[6:]}"
        formats['parentheses'] = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        formats['international'] = f"+1{digits}"
    else:
        # International or non-standard format
        formats['international'] = f"+{digits}" if not digits.startswith('+') else digits
    
    return formats


@cmdutils.register()
@cmdutils.argument('identifier')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def pivot(identifier: str, win_id: int) -> None:
    """Perform identifier pivoting across multiple platforms.
    
    Opens multiple tabs searching for the given identifier (username, email, 
    phone number) across various social media and online platforms.
    
    Args:
        identifier: The identifier to search for (username, email, phone, etc.)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    identifier = _sanitize_identifier(identifier)
    
    message.info(f"Pivoting on identifier: {identifier}")
    
    # Determine identifier type
    is_email = '@' in identifier and '.' in identifier
    is_phone = identifier.replace('+', '').replace('-', '').replace(' ', '').isdigit()
    
    # Select appropriate platforms based on identifier type
    if is_email:
        # Email searches work better on professional platforms
        priority_platforms = ['linkedin', 'facebook', 'twitter', 'github', 
                            'instagram', 'google']
    elif is_phone:
        # Phone searches work on specific platforms
        priority_platforms = ['truecaller', 'whitepages', 'facebook', 
                            'linkedin', 'whatsapp_web']
    else:
        # Username searches on all major platforms
        priority_platforms = ['twitter', 'instagram', 'github', 'linkedin',
                            'facebook', 'reddit', 'youtube', 'tiktok']
    
    # Open search in new tabs
    for platform in priority_platforms:
        if platform in PLATFORM_SEARCH_URLS:
            url = PLATFORM_SEARCH_URLS[platform].format(
                urllib.parse.quote_plus(identifier))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Opened {len(priority_platforms)} tabs for identifier pivoting")


@cmdutils.register()
@cmdutils.argument('platform', choices=sorted(PLATFORM_SEARCH_URLS.keys()))
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def platform_search(platform: str, query: str, win_id: int) -> None:
    """Search within a specific social media platform.
    
    Performs a platform-internal search using the platform's native search
    functionality.
    
    Args:
        platform: The platform to search on (twitter, instagram, github, etc.)
        query: The search query (username, email, phone, keywords)
    """
    if platform not in PLATFORM_SEARCH_URLS:
        message.error(f"Unknown platform: {platform}")
        return
    
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    query = _sanitize_identifier(query)
    
    url = PLATFORM_SEARCH_URLS[platform].format(urllib.parse.quote_plus(query))
    tabbed_browser.tabopen(QUrl(url))
    
    message.info(f"Searching {platform} for: {query}")


@cmdutils.register()
@cmdutils.argument('name')
@cmdutils.argument('context')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def csearch(name: str, win_id: int, *context: str) -> None:
    """Perform contextual name search combining name with context.
    
    Combines a person's name with contextual information like employer,
    school, location, etc. to narrow search results.
    
    Args:
        name: The person's name to search for
        context: Additional context (employer, school, location, etc.)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Build the search query
    search_parts = [name] + list(context)
    search_query = ' '.join(search_parts)
    
    # Use multiple search engines for comprehensive results
    search_engines = {
        'google': 'https://www.google.com/search?q={}',
        'bing': 'https://www.bing.com/search?q={}',
        'duckduckgo': 'https://duckduckgo.com/?q={}',
        'yandex': 'https://yandex.com/search/?text={}',
    }
    
    # Also search on social platforms
    social_searches = {
        'linkedin': f'site:linkedin.com {search_query}',
        'facebook': f'site:facebook.com {search_query}',
        'twitter': f'site:twitter.com OR site:x.com {search_query}',
        'instagram': f'site:instagram.com {search_query}',
    }
    
    # Open general search engines
    for engine_name, url_template in search_engines.items():
        url = url_template.format(urllib.parse.quote_plus(search_query))
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Open social media specific searches
    google_url = search_engines['google']
    for platform, platform_query in social_searches.items():
        url = google_url.format(urllib.parse.quote_plus(platform_query))
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Contextual search for '{name}' with context: {', '.join(context)}")


@cmdutils.register()
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def syncprep(win_id: int) -> None:
    """Prepare browser for contact syncing workflow.
    
    Opens relevant contact management and social media "Find Friends" pages
    to facilitate manual contact syncing across platforms.
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Open all sync preparation URLs
    for service, url in SYNC_PREP_URLS.items():
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Opened {len(SYNC_PREP_URLS)} tabs for contact sync preparation")
    message.info("Add target phone numbers to your contacts, then use platform sync features")


@cmdutils.register()
@cmdutils.argument('phone')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def revphone(phone: str, win_id: int) -> None:
    """Perform reverse phone lookup across multiple services.
    
    Searches for information associated with a phone number using various
    reverse lookup and people search services.
    
    Args:
        phone: The phone number to look up
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Format phone number in various ways
    phone_formats = _format_phone_number(phone)
    
    # Priority services for phone lookups
    priority_services = [
        'truecaller', 'whitepages', 'spokeo', 'beenverified',
        'thatsthem', 'fastpeoplesearch', 'usphonebook'
    ]
    
    # Open lookups with the most appropriate format for each service
    for service in priority_services:
        if service in REVERSE_LOOKUP_URLS:
            # Use digits format for most services
            phone_to_use = phone_formats['digits']
            if service in ['whitepages', 'spokeo']:
                # Some services prefer dashed format
                phone_to_use = phone_formats['dashed'] or phone_formats['digits']
            
            url = REVERSE_LOOKUP_URLS[service].format(
                urllib.parse.quote_plus(phone_to_use))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Also search the phone number on social platforms
    social_platforms = ['facebook', 'linkedin', 'twitter', 'instagram']
    for platform in social_platforms:
        if platform in PLATFORM_SEARCH_URLS:
            # Try different phone formats
            for format_name, formatted_phone in phone_formats.items():
                if formatted_phone:
                    url = PLATFORM_SEARCH_URLS[platform].format(
                        urllib.parse.quote_plus(formatted_phone))
                    tabbed_browser.tabopen(QUrl(url), background=True)
                    break  # Only use one format per platform
    
    total_tabs = len(priority_services) + len(social_platforms)
    message.info(f"Opened {total_tabs} tabs for reverse phone lookup: {phone}")


@cmdutils.register()
@cmdutils.argument('email')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def revemail(email: str, win_id: int) -> None:
    """Perform reverse email lookup across multiple services.
    
    Searches for information associated with an email address using various
    search engines and people search services.
    
    Args:
        email: The email address to look up
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Validate email format
    if '@' not in email or '.' not in email:
        message.error(f"Invalid email format: {email}")
        return
    
    # Extract username from email for additional searches
    username = email.split('@')[0]
    
    # Search engines with email
    search_queries = {
        'google': f'"{email}"',
        'bing': f'"{email}"',
        'duckduckgo': f'"{email}"',
        'yandex': f'"{email}"',
    }
    
    # Open search engine queries
    for engine, query in search_queries.items():
        if engine in PLATFORM_SEARCH_URLS:
            url = PLATFORM_SEARCH_URLS[engine].format(
                urllib.parse.quote_plus(query))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    # People search services
    people_services = ['spokeo', 'pipl', 'beenverified', 'truthfinder']
    for service in people_services:
        if service in REVERSE_LOOKUP_URLS:
            url = REVERSE_LOOKUP_URLS[service].format(
                urllib.parse.quote_plus(email))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Social media searches with email
    social_platforms = ['facebook', 'linkedin', 'twitter', 'instagram', 'github']
    for platform in social_platforms:
        if platform in PLATFORM_SEARCH_URLS:
            url = PLATFORM_SEARCH_URLS[platform].format(
                urllib.parse.quote_plus(email))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Also search for the username part
    pivot(username, win_id)
    
    message.info(f"Reverse email lookup initiated for: {email}")


@cmdutils.register(name='socmint-help')
def socmint_help() -> None:
    """Display help information for SOCMINT commands."""
    help_text = """
SOCMINT (Social Media & People Intelligence) Commands:

1. :pivot <identifier>
   - Search for username, email, or phone across multiple platforms
   - Automatically detects identifier type and searches appropriate platforms
   - Example: :pivot john.doe@email.com

2. :platform-search <platform> <query>
   - Search within a specific platform
   - Platforms: twitter, instagram, facebook, linkedin, github, etc.
   - Example: :platform-search twitter "John Doe"

3. :csearch <name> <context1> <context2> ...
   - Contextual search combining name with employer, location, etc.
   - Example: :csearch "John Doe" "Microsoft" "Seattle"

4. :syncprep
   - Opens contact sync pages for multiple platforms
   - Use to prepare for manual contact syncing workflow

5. :revphone <phone>
   - Reverse phone lookup across multiple services
   - Accepts various phone formats
   - Example: :revphone 555-123-4567

6. :revemail <email>
   - Reverse email lookup across multiple services
   - Also searches for the username part separately
   - Example: :revemail john.doe@email.com

Tips:
- All commands open results in background tabs
- Use Tab key for command completion
- Combine commands for comprehensive investigations
    """
    message.info(help_text)