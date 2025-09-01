# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Community & Forum Intelligence for qutebrowser.

Implements Reddit analysis, forum discovery, and earnings call analysis.
"""

import urllib.parse
import re
from typing import List, Dict, Optional

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg


class CommunityIntelligence:
    """Handle community and forum intelligence operations."""
    
    def __init__(self):
        # Major forum platforms
        self.forum_platforms = {
            'reddit': 'https://www.reddit.com',
            'hackernews': 'https://news.ycombinator.com',
            'stackoverflow': 'https://stackoverflow.com',
            'quora': 'https://www.quora.com',
            'discourse': 'https://www.discourse.org',
            'discord': 'https://discord.com',
            'slack': 'https://slack.com',
            'telegram': 'https://telegram.org',
            'gitter': 'https://gitter.im',
            'spectrum': 'https://spectrum.chat',
            'dev_to': 'https://dev.to',
            'hashnode': 'https://hashnode.com',
            'medium': 'https://medium.com',
            'producthunt': 'https://www.producthunt.com',
            'indiehackers': 'https://www.indiehackers.com'
        }
        
        # Industry-specific forums
        self.industry_forums = {
            'tech': [
                'https://slashdot.org',
                'https://www.techpowerup.com/forums/',
                'https://arstechnica.com/civis/',
                'https://forums.anandtech.com',
                'https://www.overclock.net',
                'https://linustechtips.com/forum/',
                'https://forum.xda-developers.com'
            ],
            'finance': [
                'https://www.wallstreetoasis.com',
                'https://www.elitetrader.com',
                'https://www.trade2win.com',
                'https://www.bogleheads.org',
                'https://seekingalpha.com',
                'https://stocktwits.com'
            ],
            'security': [
                'https://www.bleepingcomputer.com/forums/',
                'https://www.wilderssecurity.com',
                'https://malwaretips.com',
                'https://0x00sec.org',
                'https://www.hackthebox.eu/forum',
                'https://forum.bugcrowd.com'
            ],
            'crypto': [
                'https://bitcointalk.org',
                'https://forum.bitcoin.com',
                'https://www.altcoinstalks.com',
                'https://cryptocurrencytalk.com',
                'https://forum.ethereum.org'
            ],
            'gaming': [
                'https://www.resetera.com',
                'https://www.neogaf.com',
                'https://gamefaqs.gamespot.com',
                'https://forums.mmorpg.com',
                'https://www.rpg.net/forums/'
            ]
        }
        
        # Earnings call and investor relations
        self.earnings_sources = {
            'seekingalpha_earnings': 'https://seekingalpha.com/earnings/earnings-call-transcripts',
            'motley_fool': 'https://www.fool.com/earnings-call-transcripts/',
            'nasdaq_earnings': 'https://www.nasdaq.com/market-activity/earnings',
            'yahoo_finance': 'https://finance.yahoo.com/calendar/earnings',
            'zacks': 'https://www.zacks.com/stock/research/',
            'morningstar': 'https://www.morningstar.com/earnings',
            'investor_relations': 'https://www.google.com/search?q=',
            'sec_earnings': 'https://www.sec.gov/edgar/search/',
            'conference_call': 'https://www.google.com/search?q='
        }
        
        # Search operators for forums
        self.forum_search_patterns = [
            'inurl:forum',
            'inurl:community',
            'inurl:discussion',
            'inurl:board',
            'inurl:threads',
            'inurl:topic',
            'inurl:viewtopic',
            'inurl:showthread',
            'intitle:forum',
            'intitle:discussion',
            'intitle:community'
        ]


@cmdutils.register(name='reddit-user')
@cmdutils.argument('username')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def reddit_user_analysis(username: str, win_id: int) -> None:
    """Analyze Reddit user activity and history.
    
    Search for all posts, comments, and activity by a Reddit user.
    
    Args:
        username: Reddit username (without u/ prefix)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    # Clean username
    username = username.replace('u/', '').replace('/u/', '').strip()
    
    # Reddit user profile
    reddit_profile = f"https://www.reddit.com/user/{username}"
    tabbed_browser.tabopen(QUrl(reddit_profile))
    
    # Reddit search for user's content
    reddit_searches = [
        f"https://www.reddit.com/search/?q=author:{username}",
        f"https://www.reddit.com/user/{username}/posts/",
        f"https://www.reddit.com/user/{username}/comments/",
        f"https://www.reddit.com/user/{username}/submitted/",
        f"https://www.reddit.com/user/{username}/gilded/"
    ]
    
    for url in reddit_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # External Reddit analysis tools
    analysis_tools = [
        f"https://redditmetis.com/user/{username}",
        f"https://www.redective.com/?r=e&a=search&s=user&t=redective&q={username}",
        f"https://redditsearch.io/?term=&dataviz=false&aggs=false&subreddits=&searchtype=posts,comments&search=true&start=0&end=0&size=100&author={username}",
        f"https://camas.unddit.com/#{{'author':'{username}'}}",
        f"https://www.google.com/search?q=site:reddit.com+\"{username}\""
    ]
    
    for tool_url in analysis_tools:
        tabbed_browser.tabopen(QUrl(tool_url), background=True)
    
    message.info(f"Reddit user analysis: u/{username}")


@cmdutils.register(name='reddit-search')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def reddit_search(query: str, win_id: int, subreddit: str = None, time: str = 'all') -> None:
    """Search Reddit with advanced filters.
    
    Search across Reddit or within specific subreddits.
    
    Args:
        query: Search query
        subreddit: Optional subreddit to search within
        time: Time range (hour, day, week, month, year, all)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # Reddit internal search
    if subreddit:
        subreddit = subreddit.replace('r/', '').replace('/r/', '').strip()
        reddit_url = f"https://www.reddit.com/r/{subreddit}/search/?q={encoded_query}&restrict_sr=1&t={time}"
    else:
        reddit_url = f"https://www.reddit.com/search/?q={encoded_query}&t={time}"
    
    tabbed_browser.tabopen(QUrl(reddit_url))
    
    # Reddit search tools
    search_tools = [
        f"https://redditsearch.io/?term={encoded_query}&dataviz=false&aggs=false&subreddits=&searchtype=posts,comments&search=true&start=0&end=0&size=100",
        f"https://camas.unddit.com/#{{'searchFor':1,'query':'{query}'}}",
        f"https://www.google.com/search?q=site:reddit.com+\"{query}\"",
        f"https://www.bing.com/search?q=site:reddit.com+\"{query}\""
    ]
    
    for tool_url in search_tools:
        tabbed_browser.tabopen(QUrl(tool_url), background=True)
    
    # Also search for related subreddits
    subreddit_search = f"https://www.reddit.com/subreddits/search?q={encoded_query}"
    tabbed_browser.tabopen(QUrl(subreddit_search), background=True)
    
    message.info(f"Reddit search: {query}")
    if subreddit:
        message.info(f"Limited to r/{subreddit}")


@cmdutils.register(name='forum-discover')
@cmdutils.argument('topic')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def forum_discovery(topic: str, win_id: int, industry: str = None) -> None:
    """Discover niche forums on a specific topic.
    
    Find specialized discussion boards and forums related to a topic.
    
    Args:
        topic: Topic to search for forums about
        industry: Optional industry filter (tech, finance, security, crypto, gaming)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    comm = CommunityIntelligence()
    
    encoded_topic = urllib.parse.quote_plus(topic)
    
    # Search for forums using patterns
    forum_searches = []
    for pattern in comm.forum_search_patterns[:5]:
        search_query = f'"{topic}" {pattern}'
        google_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_query)}"
        forum_searches.append(google_url)
    
    for url in forum_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Industry-specific forums
    if industry and industry.lower() in comm.industry_forums:
        for forum_url in comm.industry_forums[industry.lower()][:3]:
            tabbed_browser.tabopen(QUrl(forum_url), background=True)
    
    # General forum searches
    general_searches = [
        f"https://www.google.com/search?q=\"{encoded_topic}\"+forum+OR+discussion+OR+community",
        f"https://www.bing.com/search?q=\"{encoded_topic}\"+inurl:forum",
        f"https://duckduckgo.com/?q=\"{encoded_topic}\"+forum",
        f"https://boardreader.com/s/{encoded_topic}.html"
    ]
    
    for url in general_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Check major platforms
    platform_searches = [
        f"https://www.reddit.com/search/?q={encoded_topic}",
        f"https://stackoverflow.com/search?q={encoded_topic}",
        f"https://www.quora.com/search?q={encoded_topic}",
        f"https://news.ycombinator.com/item?id=site:{encoded_topic}"
    ]
    
    for url in platform_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Forum discovery: {topic}")
    if industry:
        message.info(f"Industry focus: {industry}")


@cmdutils.register(name='earnings-call')
@cmdutils.argument('company')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def earnings_call_analysis(company: str, win_id: int, ticker: str = None) -> None:
    """Search for earnings call transcripts and analysis.
    
    Find quarterly earnings calls, investor presentations, and financial analysis.
    
    Args:
        company: Company name
        ticker: Optional stock ticker symbol
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    comm = CommunityIntelligence()
    
    encoded_company = urllib.parse.quote_plus(company)
    
    # If ticker provided, use it in searches
    if ticker:
        ticker = ticker.upper()
        search_term = f"{company} {ticker}"
        encoded_search = urllib.parse.quote_plus(search_term)
    else:
        search_term = company
        encoded_search = encoded_company
    
    # Earnings transcript sources
    earnings_searches = [
        f"{comm.earnings_sources['seekingalpha_earnings']}?search={encoded_search}",
        f"{comm.earnings_sources['motley_fool']}?search={encoded_search}",
        f"{comm.earnings_sources['yahoo_finance']}?search={encoded_search}",
        f"{comm.earnings_sources['sec_earnings']}#/entitySearch/{encoded_company}"
    ]
    
    for url in earnings_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Google searches for earnings calls
    google_searches = [
        f"https://www.google.com/search?q=\"{search_term}\"+\"earnings+call+transcript\"",
        f"https://www.google.com/search?q=\"{search_term}\"+\"investor+presentation\"+filetype:pdf",
        f"https://www.google.com/search?q=\"{search_term}\"+\"quarterly+results\"",
        f"https://www.google.com/search?q=\"{search_term}\"+site:seekingalpha.com",
        f"https://www.google.com/search?q=\"{search_term}\"+\"conference+call\"+\"Q1+OR+Q2+OR+Q3+OR+Q4\""
    ]
    
    for url in google_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Investor relations page
    ir_search = f"https://www.google.com/search?q=\"{company}\"+\"investor+relations\""
    tabbed_browser.tabopen(QUrl(ir_search), background=True)
    
    # Financial news and analysis
    if ticker:
        finance_urls = [
            f"https://finance.yahoo.com/quote/{ticker}",
            f"https://www.marketwatch.com/investing/stock/{ticker}",
            f"https://www.bloomberg.com/quote/{ticker}:US"
        ]
        for url in finance_urls:
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Earnings call analysis: {company}")
    if ticker:
        message.info(f"Ticker: {ticker}")


@cmdutils.register(name='community-sentiment')
@cmdutils.argument('topic')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def community_sentiment(topic: str, win_id: int) -> None:
    """Analyze community sentiment on a topic across platforms.
    
    Search multiple community platforms to gauge sentiment and discussions.
    
    Args:
        topic: Topic to analyze sentiment for
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    encoded_topic = urllib.parse.quote_plus(topic)
    
    # Social and community platforms
    sentiment_searches = [
        # Reddit
        f"https://www.reddit.com/search/?q={encoded_topic}&sort=top",
        f"https://www.reddit.com/search/?q={encoded_topic}&sort=hot",
        
        # Twitter/X
        f"https://twitter.com/search?q={encoded_topic}&f=top",
        f"https://twitter.com/search?q={encoded_topic}&f=live",
        
        # Hacker News
        f"https://hn.algolia.com/?q={encoded_topic}",
        
        # Stack Overflow
        f"https://stackoverflow.com/search?q={encoded_topic}&tab=votes",
        
        # Quora
        f"https://www.quora.com/search?q={encoded_topic}",
        
        # YouTube comments
        f"https://www.youtube.com/results?search_query={encoded_topic}&sp=CAM%253D",
        
        # Product Hunt
        f"https://www.producthunt.com/search?q={encoded_topic}",
        
        # Dev.to
        f"https://dev.to/search?q={encoded_topic}",
        
        # Medium
        f"https://medium.com/search?q={encoded_topic}"
    ]
    
    for url in sentiment_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Google Trends for popularity analysis
    trends_url = f"https://trends.google.com/trends/explore?q={encoded_topic}"
    tabbed_browser.tabopen(QUrl(trends_url), background=True)
    
    message.info(f"Community sentiment analysis: {topic}")


@cmdutils.register(name='discord-search')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def discord_search(query: str, win_id: int) -> None:
    """Search for Discord servers and discussions.
    
    Find Discord servers related to a topic or search for discussions.
    
    Args:
        query: Search query for Discord servers or topics
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # Discord directory sites
    discord_searches = [
        f"https://disboard.org/servers/tag/{encoded_query}",
        f"https://discord.me/servers?q={encoded_query}",
        f"https://discordservers.com/search/{encoded_query}",
        f"https://top.gg/search?q={encoded_query}",
        f"https://discord.com/invite/{query}",  # Try direct invite
        f"https://www.google.com/search?q=\"{query}\"+discord+server+invite",
        f"https://www.google.com/search?q=site:discord.gg+\"{query}\"",
        f"https://www.reddit.com/search/?q={encoded_query}+discord"
    ]
    
    for url in discord_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Discord search: {query}")


@cmdutils.register(name='hackernews')
@cmdutils.argument('query')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def hackernews_search(query: str, win_id: int, sort: str = 'relevance') -> None:
    """Search Hacker News discussions and submissions.
    
    Search HN for discussions, links, and comments.
    
    Args:
        query: Search query
        sort: Sort order (relevance, points, date)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    
    encoded_query = urllib.parse.quote_plus(query)
    
    # Algolia HN Search (official)
    if sort == 'points':
        hn_url = f"https://hn.algolia.com/?q={encoded_query}&sort=byPopularity"
    elif sort == 'date':
        hn_url = f"https://hn.algolia.com/?q={encoded_query}&sort=byDate"
    else:
        hn_url = f"https://hn.algolia.com/?q={encoded_query}"
    
    tabbed_browser.tabopen(QUrl(hn_url))
    
    # Additional HN searches
    hn_searches = [
        f"https://news.ycombinator.com/item?id=site:{encoded_query}",
        f"https://www.google.com/search?q=site:news.ycombinator.com+\"{query}\"",
        f"https://hn.algolia.com/?q={encoded_query}&type=comment",
        f"https://hn.algolia.com/?q={encoded_query}&type=story"
    ]
    
    for url in hn_searches:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info(f"Hacker News search: {query}")


@cmdutils.register(name='community-help')
def community_intelligence_help() -> None:
    """Display help for community intelligence commands."""
    help_text = """
Community Intelligence Commands:

1. :reddit-user <username>
   - Analyze Reddit user history
   - Posts, comments, activity
   - Example: :reddit-user spez

2. :reddit-search <query> [subreddit] [time]
   - Search Reddit with filters
   - Time: hour, day, week, month, year, all
   - Example: :reddit-search "python tips" learnpython week

3. :forum-discover <topic> [industry]
   - Find niche forums on topic
   - Industries: tech, finance, security, crypto, gaming
   - Example: :forum-discover "machine learning" tech

4. :earnings-call <company> [ticker]
   - Find earnings transcripts
   - Investor presentations
   - Example: :earnings-call "Apple" AAPL

5. :community-sentiment <topic>
   - Analyze sentiment across platforms
   - Reddit, Twitter, HN, etc.
   - Example: :community-sentiment "chatgpt"

6. :discord-search <query>
   - Find Discord servers
   - Search for invites
   - Example: :discord-search "python programming"

7. :hackernews <query> [sort]
   - Search Hacker News
   - Sort: relevance, points, date
   - Example: :hackernews "rust lang" points

Tips:
- Use quotes for exact phrases
- Check multiple time periods
- Look for deleted/archived content
- Cross-reference platforms
    """
    message.info(help_text)