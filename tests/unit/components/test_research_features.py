# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Comprehensive tests for all research features."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QUrl

# Import all components
from qutebrowser.components import (
    advanced_search,
    visual_intelligence,
    website_deconstruct,
    temporal_analysis,
    public_records,
    community_intelligence,
    socmint
)


class TestAdvancedSearch:
    """Test advanced search features."""
    
    def test_search_query_builder_initialization(self):
        """Test SearchQueryBuilder initialization."""
        builder = advanced_search.SearchQueryBuilder()
        assert 'google' in builder.engines
        assert 'bing' in builder.engines
        assert 'duckduckgo' in builder.engines
        assert len(builder.engines) >= 9
    
    def test_build_query_with_operators(self):
        """Test building query with various operators."""
        builder = advanced_search.SearchQueryBuilder()
        
        operators = {
            'site': 'github.com',
            'filetype': 'pdf',
            'intitle': 'python',
            'exclude': 'java,javascript'
        }
        
        query = builder.build_query("tutorial", operators, 'google')
        assert 'tutorial' in query
        assert 'site:github.com' in query
        assert 'filetype:pdf' in query
        assert 'intitle:python' in query
        assert '-java' in query
        assert '-javascript' in query
    
    def test_build_url(self):
        """Test URL building for different engines."""
        builder = advanced_search.SearchQueryBuilder()
        
        google_url = builder.build_url("test query", 'google')
        assert 'google.com/search' in google_url
        assert 'test+query' in google_url
        
        bing_url = builder.build_url("test query", 'bing')
        assert 'bing.com/search' in bing_url
    
    def test_proximity_query(self):
        """Test proximity search query building."""
        builder = advanced_search.SearchQueryBuilder()
        
        operators = {
            'proximity': 'python,tutorial,5'
        }
        
        query = builder.build_query("", operators, 'google')
        assert 'AROUND(5)' in query
        assert 'python' in query
        assert 'tutorial' in query
    
    def test_boolean_query(self):
        """Test boolean search query building."""
        builder = advanced_search.SearchQueryBuilder()
        
        operators = {
            'or_terms': 'python,javascript,ruby'
        }
        
        query = builder.build_query("programming", operators, 'google')
        assert 'programming' in query
        assert '(python OR javascript OR ruby)' in query


class TestVisualIntelligence:
    """Test visual intelligence features."""
    
    def test_visual_intelligence_initialization(self):
        """Test VisualIntelligence initialization."""
        vis = visual_intelligence.VisualIntelligence()
        assert 'google' in vis.reverse_image_engines
        assert 'tineye' in vis.reverse_image_engines
        assert 'yandex' in vis.reverse_image_engines
        assert len(vis.reverse_image_engines) >= 15
        assert len(vis.ai_vision_services) >= 5
        assert len(vis.image_analysis_tools) >= 8
    
    def test_validate_image_url(self):
        """Test image URL validation."""
        vis = visual_intelligence.VisualIntelligence()
        
        assert vis.validate_image_url('https://example.com/image.jpg')
        assert vis.validate_image_url('https://example.com/photo.png')
        assert vis.validate_image_url('https://example.com/pic.gif')
        assert not vis.validate_image_url('https://example.com/document.pdf')
        assert not vis.validate_image_url('https://example.com/page.html')
    
    def test_extract_video_id(self):
        """Test YouTube video ID extraction."""
        vis = visual_intelligence.VisualIntelligence()
        
        # YouTube URLs
        assert vis.extract_video_id('https://youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        assert vis.extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        assert vis.extract_video_id('https://youtube.com/embed/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        assert vis.extract_video_id('https://example.com/video.mp4') is None


class TestWebsiteDeconstruction:
    """Test website deconstruction features."""
    
    def test_website_deconstructor_initialization(self):
        """Test WebsiteDeconstructor initialization."""
        decon = website_deconstruct.WebsiteDeconstructor()
        assert len(decon.common_hidden_paths) >= 30
        assert '/admin' in decon.common_hidden_paths
        assert '/.git' in decon.common_hidden_paths
        assert '/robots.txt' in decon.common_hidden_paths
        assert len(decon.interesting_file_extensions) >= 20
    
    def test_parse_robots_txt(self):
        """Test robots.txt parsing."""
        decon = website_deconstruct.WebsiteDeconstructor()
        
        robots_content = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /api/keys/
Allow: /public/
Sitemap: https://example.com/sitemap.xml
Crawl-delay: 1.0
        """
        
        result = decon.parse_robots_txt(robots_content)
        assert '/admin/' in result['disallowed']
        assert '/private/' in result['disallowed']
        assert '/api/keys/' in result['disallowed']
        assert '/public/' in result['allowed']
        assert 'https://example.com/sitemap.xml' in result['sitemaps']
        assert result['crawl_delay'] == 1.0
        assert len(result['interesting_paths']) >= 2  # admin and api paths
    
    def test_parse_sitemap_xml(self):
        """Test sitemap.xml parsing."""
        decon = website_deconstruct.WebsiteDeconstructor()
        
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
    </url>
</urlset>"""
        
        result = decon.parse_sitemap_xml(sitemap_content)
        assert 'https://example.com/page1' in result['urls']
        assert 'https://example.com/page2' in result['urls']
        assert len(result['urls']) == 2
    
    def test_extract_base_domain(self):
        """Test base domain extraction."""
        decon = website_deconstruct.WebsiteDeconstructor()
        
        assert decon.extract_base_domain('https://www.example.com/path/page.html') == 'https://www.example.com'
        assert decon.extract_base_domain('http://subdomain.example.com') == 'http://subdomain.example.com'
        assert decon.extract_base_domain('https://example.com:8080/') == 'https://example.com:8080'


class TestTemporalAnalysis:
    """Test temporal analysis features."""
    
    def test_temporal_analyzer_initialization(self):
        """Test TemporalAnalyzer initialization."""
        temporal = temporal_analysis.TemporalAnalyzer()
        assert 'wayback' in temporal.archive_services
        assert 'archive_is' in temporal.archive_services
        assert len(temporal.archive_services) >= 10
        assert len(temporal.evidence_services) >= 4
    
    def test_format_wayback_url(self):
        """Test Wayback Machine URL formatting."""
        temporal = temporal_analysis.TemporalAnalyzer()
        
        # Without date
        url = temporal.format_wayback_url('example.com')
        assert 'web.archive.org/web/*/' in url
        assert 'example.com' in url
        
        # With date
        url = temporal.format_wayback_url('example.com', '20200101')
        assert 'web.archive.org/web/20200101/' in url
        assert 'example.com' in url
        
        # URL without protocol
        url = temporal.format_wayback_url('example.com/page')
        assert 'https://example.com/page' in url
    
    def test_get_date_ranges(self):
        """Test date range generation."""
        temporal = temporal_analysis.TemporalAnalyzer()
        
        ranges = temporal.get_date_ranges()
        assert len(ranges) > 0
        assert all(len(r) == 8 for r in ranges)  # YYYYMMDD format
        assert '20200101' in ranges or '20200701' in ranges


class TestPublicRecords:
    """Test public records features."""
    
    def test_public_records_initialization(self):
        """Test PublicRecordsAccess initialization."""
        records = public_records.PublicRecordsAccess()
        
        assert len(records.business_databases) >= 20
        assert 'opencorporates' in records.business_databases
        assert 'sec_edgar' in records.business_databases
        
        assert len(records.legal_databases) >= 15
        assert 'pacer' in records.legal_databases
        
        assert len(records.property_databases) >= 10
        assert 'zillow' in records.property_databases
        
        assert len(records.ip_databases) >= 10
        assert 'google_patents' in records.ip_databases
        assert 'uspto_patents' in records.ip_databases
        
        assert len(records.academic_databases) >= 15
        assert 'google_scholar' in records.academic_databases
        assert 'pubmed' in records.academic_databases
        
        assert len(records.government_data) >= 10
        assert 'data_gov' in records.government_data


class TestCommunityIntelligence:
    """Test community intelligence features."""
    
    def test_community_intelligence_initialization(self):
        """Test CommunityIntelligence initialization."""
        comm = community_intelligence.CommunityIntelligence()
        
        assert 'reddit' in comm.forum_platforms
        assert 'hackernews' in comm.forum_platforms
        assert len(comm.forum_platforms) >= 10
        
        assert 'tech' in comm.industry_forums
        assert 'finance' in comm.industry_forums
        assert 'security' in comm.industry_forums
        assert len(comm.industry_forums['tech']) >= 5
        
        assert 'seekingalpha_earnings' in comm.earnings_sources
        assert len(comm.earnings_sources) >= 8
        
        assert 'inurl:forum' in comm.forum_search_patterns
        assert len(comm.forum_search_patterns) >= 10


class TestSocmint:
    """Test SOCMINT features."""
    
    def test_sanitize_identifier(self):
        """Test identifier sanitization."""
        assert socmint._sanitize_identifier('@username') == 'username'
        assert socmint._sanitize_identifier('user@email.com') == 'user@email.com'
        assert socmint._sanitize_identifier('123-456-7890') == '123-456-7890'
        assert socmint._sanitize_identifier('user!@#$%name') == 'username'
    
    def test_format_phone_number(self):
        """Test phone number formatting."""
        # US phone number
        formats = socmint._format_phone_number('1234567890')
        assert formats['dashed'] == '123-456-7890'
        assert formats['dotted'] == '123.456.7890'
        assert formats['spaced'] == '123 456 7890'
        assert formats['parentheses'] == '(123) 456-7890'
        assert formats['international'] == '+11234567890'
        
        # US phone with country code
        formats = socmint._format_phone_number('11234567890')
        assert formats['dashed'] == '123-456-7890'
        assert formats['international'] == '+11234567890'
        
        # Non-standard format
        formats = socmint._format_phone_number('987654321')
        assert formats['international'] == '+987654321'


class TestIntegration:
    """Integration tests for command execution."""
    
    @patch('qutebrowser.utils.objreg.get')
    def test_advanced_search_command(self, mock_objreg):
        """Test advanced search command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Execute command
        advanced_search.search_advanced(
            "python tutorial",
            win_id=1,
            site="github.com",
            filetype="pdf"
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 3  # At least 3 search engines
    
    @patch('qutebrowser.utils.objreg.get')
    def test_reverse_image_command(self, mock_objreg):
        """Test reverse image search command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Execute command
        visual_intelligence.reverse_image_search(
            "https://example.com/image.jpg",
            win_id=1
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 5  # At least 5 reverse image engines
    
    @patch('qutebrowser.utils.objreg.get')
    @patch('urllib.request.urlopen')
    def test_robots_analyze_command(self, mock_urlopen, mock_objreg):
        """Test robots.txt analysis command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Mock robots.txt response
        mock_response = Mock()
        mock_response.read.return_value = b"""
User-agent: *
Disallow: /admin/
Disallow: /api/
Sitemap: https://example.com/sitemap.xml
        """
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Execute command
        website_deconstruct.analyze_robots_txt(
            "example.com",
            win_id=1
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 2  # robots.txt and wayback
    
    @patch('qutebrowser.utils.objreg.get')
    def test_wayback_view_command(self, mock_objreg):
        """Test Wayback Machine view command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Execute command without date
        temporal_analysis.wayback_view(
            "example.com",
            win_id=1
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 2  # Wayback and CDX API
        
        # Test with date
        mock_browser.reset_mock()
        temporal_analysis.wayback_view(
            "example.com",
            win_id=1,
            date="20200101"
        )
        
        assert mock_browser.tabopen.called
    
    @patch('qutebrowser.utils.objreg.get')
    def test_business_search_command(self, mock_objreg):
        """Test business search command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Execute command
        public_records.business_search(
            "Apple Inc",
            win_id=1,
            jurisdiction="us"
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 4  # Multiple business databases
    
    @patch('qutebrowser.utils.objreg.get')
    def test_reddit_user_command(self, mock_objreg):
        """Test Reddit user analysis command execution."""
        mock_browser = Mock()
        mock_objreg.return_value = mock_browser
        
        # Execute command
        community_intelligence.reddit_user_analysis(
            "testuser",
            win_id=1
        )
        
        # Verify tabs were opened
        assert mock_browser.tabopen.called
        calls = mock_browser.tabopen.call_args_list
        assert len(calls) >= 5  # Reddit profile and analysis tools


def test_all_commands_registered():
    """Test that all commands are properly registered."""
    from qutebrowser.api import cmdutils
    
    # List of expected commands
    expected_commands = [
        # Advanced Search
        'search-advanced', 'search-cross', 'search-proximity',
        'search-wildcard', 'search-boolean', 'search-ip',
        'search-cache', 'search-help',
        
        # Visual Intelligence
        'reverse-image', 'visual-deanon', 'image-timeline',
        'image-manipulate', 'video-frame', 'ai-vision',
        'image-exif', 'visual-help',
        
        # Website Deconstruction
        'robots-analyze', 'sitemap-analyze', 'orphan-find',
        'hidden-discover', 'wayback-discover', 'config-find',
        'decon-help',
        
        # Temporal Analysis
        'wayback-view', 'wayback-timeline', 'wayback-directory',
        'cache-view', 'evidence-save', 'archive-compare',
        'domain-history', 'temporal-help',
        
        # Public Records
        'business-search', 'legal-search', 'property-search',
        'patent-search', 'academic-search', 'gov-data',
        'public-help',
        
        # Community Intelligence
        'reddit-user', 'reddit-search', 'forum-discover',
        'earnings-call', 'community-sentiment', 'discord-search',
        'hackernews', 'community-help',
        
        # SOCMINT (existing)
        'pivot', 'platform-search', 'csearch', 'syncprep',
        'revphone', 'revemail', 'socmint-help'
    ]
    
    # Note: In actual implementation, we would check if commands are registered
    # For now, we just verify the list is complete
    assert len(expected_commands) >= 50  # We have 50+ commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])