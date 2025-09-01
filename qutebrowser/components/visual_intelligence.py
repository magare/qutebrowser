# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Visual Intelligence (Image & Video) features for qutebrowser.

Implements reverse image search, visual analysis, and image tracking capabilities.
"""

import re
import urllib.parse
import base64
import mimetypes
from typing import Optional, List, Dict
from pathlib import Path

from PyQt6.QtCore import QUrl

from qutebrowser.api import cmdutils
from qutebrowser.utils import message, objreg, utils


class VisualIntelligence:
    """Handle visual intelligence operations."""
    
    def __init__(self):
        self.reverse_image_engines = {
            'google': 'https://lens.google.com/uploadbyurl?url={}',
            'google_images': 'https://www.google.com/searchbyimage?image_url={}',
            'tineye': 'https://tineye.com/search?url={}',
            'yandex': 'https://yandex.com/images/search?source=collections&rpt=imageview&url={}',
            'bing': 'https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIVSP&sbisrc=UrlPaste&q=imgurl:{}',
            'baidu': 'https://graph.baidu.com/pcpage/similar?tpl_from=pc&image={}',
            'sogou': 'https://pic.sogou.com/ris?query={}',
            'imgops': 'https://imgops.com/{}',
            'karma_decay': 'https://karmadecay.com/search?q={}',
            'iqdb': 'https://iqdb.org/?url={}',
            'saucenao': 'https://saucenao.com/search.php?url={}',
            'trace_moe': 'https://trace.moe/?url={}',
            'ascii2d': 'https://ascii2d.net/search/url/{}',
            'reverse_image_search': 'https://www.reverseimagesearch.com/uploadbyurl?url={}',
            'pixsy': 'https://www.pixsy.com/reverse-image-search?url={}',
            'berify': 'https://berify.com/reverse-image-search/?url={}',
            'prepostseo': 'https://www.prepostseo.com/reverse-image-search?url={}',
            'duplichecker': 'https://www.duplichecker.com/reverse-image-search.php?url={}',
            'labnol': 'https://www.labnol.org/reverse/?url={}',
            'camsoda': 'https://www.camfind.com/search?image_url={}'
        }
        
        self.ai_vision_services = {
            'gemini': 'https://gemini.google.com/',
            'chatgpt': 'https://chat.openai.com/',
            'claude': 'https://claude.ai/',
            'bing_chat': 'https://www.bing.com/chat',
            'bard': 'https://bard.google.com/',
            'huggingface': 'https://huggingface.co/spaces',
            'replicate': 'https://replicate.com/explore'
        }
        
        self.image_analysis_tools = {
            'exif_viewer': 'https://exifdata.com/url.php?url={}',
            'jeffrey_exif': 'https://exif.regex.info/exif.cgi?imgurl={}',
            'metapicz': 'https://metapicz.com/#landing?url={}',
            'pic2map': 'https://www.pic2map.com/?url={}',
            'forensically': 'https://29a.ch/photo-forensics/#url={}',
            'fotoforensics': 'https://fotoforensics.com/upload-url.php?url={}',
            'imageedited': 'https://imageedited.com/?url={}',
            'imageforensics': 'https://www.imageforensics.io/upload-url?url={}',
            'izitru': 'https://www.izitru.com/upload?url={}',
            'reveal': 'https://reveal-mklab.iti.gr/reveal/index.html?url={}'
        }
        
        self.video_analysis_tools = {
            'invid': 'https://www.invid-project.eu/tools-and-services/invid-verification-plugin/',
            'amnesty_youtube': 'https://citizenevidence.amnestyusa.org/',
            'youtube_metadata': 'https://mattw.io/youtube-metadata/',
            'youtube_geofind': 'https://mattw.io/youtube-geofind/',
            'deturl': 'https://deturl.com/download-video.html?v={}',
            'frame_by_frame': 'https://www.watchframebyframe.com/?v={}',
            'youtube_thumbnail': 'https://www.youtubescreenshot.com/?url={}'
        }
    
    def validate_image_url(self, url: str) -> bool:
        """Check if URL likely points to an image."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
                          '.svg', '.ico', '.tiff', '.tif']
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube/video URLs."""
        # YouTube patterns
        youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*&v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


@cmdutils.register(name='reverse-image')
@cmdutils.argument('image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def reverse_image_search(image_url: str, win_id: int, engines: str = None) -> None:
    """Multi-engine reverse image search.
    
    Search for an image across multiple reverse image search engines to find
    its source, modified versions, and similar images.
    
    Args:
        image_url: URL of the image to search
        engines: Comma-separated list of engines to use (default: all major ones)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Clean and validate URL
    image_url = image_url.strip()
    if not image_url.startswith(('http://', 'https://')):
        image_url = 'https://' + image_url
    
    # Select engines to use
    if engines:
        selected_engines = [e.strip() for e in engines.split(',')]
    else:
        # Default to major engines
        selected_engines = ['google', 'tineye', 'yandex', 'bing', 'baidu', 
                          'imgops', 'saucenao']
    
    # Open reverse image searches
    opened = 0
    for engine in selected_engines:
        if engine in vis.reverse_image_engines:
            url = vis.reverse_image_engines[engine].format(
                urllib.parse.quote_plus(image_url))
            tabbed_browser.tabopen(QUrl(url), background=True)
            opened += 1
    
    message.info(f"Reverse image search: {opened} engines searching for image")


@cmdutils.register(name='visual-deanon')
@cmdutils.argument('profile_image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def visual_deanonymization(profile_image_url: str, win_id: int) -> None:
    """Visual de-anonymization using profile picture.
    
    Search for other accounts using the same profile picture across platforms.
    
    Args:
        profile_image_url: URL of the profile picture
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Clean URL
    profile_image_url = profile_image_url.strip()
    if not profile_image_url.startswith(('http://', 'https://')):
        profile_image_url = 'https://' + profile_image_url
    
    # Use specific engines good for finding profile pictures
    engines_for_profiles = ['google', 'tineye', 'yandex', 'bing', 'karma_decay']
    
    for engine in engines_for_profiles:
        if engine in vis.reverse_image_engines:
            url = vis.reverse_image_engines[engine].format(
                urllib.parse.quote_plus(profile_image_url))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    # Also search for face matches
    face_search_urls = [
        f'https://pimeyes.com/en',  # Manual upload required
        f'https://search4faces.com/',  # Russian social media face search
        f'https://findclone.me/',  # VK face search
    ]
    
    for url in face_search_urls:
        tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info("Visual de-anonymization search initiated")
    message.info("Some services require manual image upload")


@cmdutils.register(name='image-timeline')
@cmdutils.argument('image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def image_timeline_tracking(image_url: str, win_id: int) -> None:
    """Track chronological appearance of an image online.
    
    Find when an image first appeared online and track its spread over time.
    
    Args:
        image_url: URL of the image to track
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Clean URL
    image_url = image_url.strip()
    if not image_url.startswith(('http://', 'https://')):
        image_url = 'https://' + image_url
    
    # TinEye with sort by oldest
    tineye_url = f'https://tineye.com/search?url={urllib.parse.quote_plus(image_url)}&sort=crawl_date&order=asc'
    
    # Google with time tools
    google_url = vis.reverse_image_engines['google'].format(
        urllib.parse.quote_plus(image_url))
    
    # Karma Decay for Reddit timeline
    karma_url = vis.reverse_image_engines['karma_decay'].format(
        urllib.parse.quote_plus(image_url))
    
    # Open timeline searches
    tabbed_browser.tabopen(QUrl(tineye_url))
    tabbed_browser.tabopen(QUrl(google_url), background=True)
    tabbed_browser.tabopen(QUrl(karma_url), background=True)
    
    message.info("Image timeline tracking initiated")
    message.info("Sort TinEye results by date to see first appearance")


@cmdutils.register(name='image-manipulate')
@cmdutils.argument('image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def image_manipulation_detection(image_url: str, win_id: int) -> None:
    """Detect image manipulation and editing.
    
    Analyze an image for signs of manipulation, editing, or forgery.
    
    Args:
        image_url: URL of the image to analyze
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Clean URL
    image_url = image_url.strip()
    if not image_url.startswith(('http://', 'https://')):
        image_url = 'https://' + image_url
    
    # Open forensic analysis tools
    for tool_name, tool_url in vis.image_analysis_tools.items():
        if tool_name in ['forensically', 'fotoforensics', 'imageedited', 
                         'imageforensics', 'izitru']:
            url = tool_url.format(urllib.parse.quote_plus(image_url))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info("Image manipulation detection initiated")
    message.info("Check Error Level Analysis, metadata, and clone detection")


@cmdutils.register(name='video-frame')
@cmdutils.argument('video_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def video_frame_analysis(video_url: str, win_id: int) -> None:
    """Analyze video frames for reverse image search.
    
    Extract frames from a video for analysis and reverse image searching.
    
    Args:
        video_url: URL of the video (YouTube or direct video URL)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Extract video ID if YouTube
    video_id = vis.extract_video_id(video_url)
    
    if video_id:
        # YouTube-specific tools
        tools = {
            'frame_by_frame': vis.video_analysis_tools['frame_by_frame'].format(video_id),
            'youtube_thumbnail': vis.video_analysis_tools['youtube_thumbnail'].format(video_url),
            'youtube_metadata': f'https://mattw.io/youtube-metadata/?url={video_url}',
            'amnesty': 'https://citizenevidence.amnestyusa.org/'
        }
    else:
        # Generic video tools
        tools = {
            'invid': vis.video_analysis_tools['invid'],
            'amnesty': 'https://citizenevidence.amnestyusa.org/'
        }
    
    for tool_url in tools.values():
        tabbed_browser.tabopen(QUrl(tool_url), background=True)
    
    message.info("Video frame analysis tools opened")
    message.info("Extract key frames and perform reverse image search on them")


@cmdutils.register(name='ai-vision')
@cmdutils.argument('image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def ai_vision_analysis(image_url: str, win_id: int, service: str = None) -> None:
    """AI-powered image analysis.
    
    Open AI vision services to analyze image content, identify objects,
    landmarks, text, and context.
    
    Args:
        image_url: URL of the image to analyze
        service: Specific AI service to use (gemini, chatgpt, claude, etc.)
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Prepare image URL for clipboard
    import pyperclip
    try:
        pyperclip.copy(image_url)
        message.info(f"Image URL copied to clipboard: {image_url}")
    except:
        pass
    
    # Open AI services
    if service and service in vis.ai_vision_services:
        services_to_open = [service]
    else:
        services_to_open = ['gemini', 'chatgpt', 'claude']
    
    for service_name in services_to_open:
        if service_name in vis.ai_vision_services:
            url = vis.ai_vision_services[service_name]
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info("AI vision services opened")
    message.info("Paste the image URL or upload the image to analyze")


@cmdutils.register(name='image-exif')
@cmdutils.argument('image_url')
@cmdutils.argument('win_id', value=cmdutils.Value.win_id)
def image_exif_analysis(image_url: str, win_id: int) -> None:
    """Extract and analyze EXIF metadata from image.
    
    View EXIF data including camera info, GPS location, timestamps, etc.
    
    Args:
        image_url: URL of the image to analyze
    """
    tabbed_browser = objreg.get('tabbed-browser', scope='window', window=win_id)
    vis = VisualIntelligence()
    
    # Clean URL
    image_url = image_url.strip()
    if not image_url.startswith(('http://', 'https://')):
        image_url = 'https://' + image_url
    
    # Open EXIF viewers
    exif_tools = ['exif_viewer', 'jeffrey_exif', 'metapicz', 'pic2map']
    
    for tool in exif_tools:
        if tool in vis.image_analysis_tools:
            url = vis.image_analysis_tools[tool].format(
                urllib.parse.quote_plus(image_url))
            tabbed_browser.tabopen(QUrl(url), background=True)
    
    message.info("EXIF analysis initiated")
    message.info("Check for GPS coordinates, camera model, timestamps")


@cmdutils.register(name='visual-help')
def visual_intelligence_help() -> None:
    """Display help for visual intelligence commands."""
    help_text = """
Visual Intelligence Commands:

1. :reverse-image <image_url> [engines]
   - Multi-engine reverse image search
   - Engines: google, tineye, yandex, bing, baidu, etc.
   - Example: :reverse-image https://example.com/image.jpg

2. :visual-deanon <profile_image_url>
   - Find other accounts using the same profile picture
   - Includes face search services
   - Example: :visual-deanon https://example.com/avatar.png

3. :image-timeline <image_url>
   - Track when image first appeared online
   - Chronological spread analysis
   - Example: :image-timeline https://example.com/photo.jpg

4. :image-manipulate <image_url>
   - Detect image editing and manipulation
   - Error level analysis, clone detection
   - Example: :image-manipulate https://example.com/suspect.jpg

5. :video-frame <video_url>
   - Extract and analyze video frames
   - Works with YouTube and direct video URLs
   - Example: :video-frame https://youtube.com/watch?v=xxx

6. :ai-vision <image_url> [service]
   - AI-powered image analysis
   - Services: gemini, chatgpt, claude
   - Example: :ai-vision https://example.com/landmark.jpg

7. :image-exif <image_url>
   - Extract EXIF metadata
   - GPS location, camera info, timestamps
   - Example: :image-exif https://example.com/photo.jpg

Tips:
- Most commands open multiple tabs for comprehensive analysis
- Some services require manual image upload
- EXIF data may contain GPS coordinates
    """
    message.info(help_text)