# SOCMINT (Social Media & People Intelligence) Features for qutebrowser

## Overview

This guide documents the SOCMINT features that have been integrated into qutebrowser, providing powerful tools for social media research, people intelligence gathering, and online investigation workflows.

## Features

### 1. Identifier Pivoting (`:pivot`)
Search for a username, email, or phone number across multiple platforms simultaneously.

**Usage:**
```
:pivot <identifier>
```

**Examples:**
- `:pivot johndoe` - Search for username across platforms
- `:pivot john.doe@email.com` - Search for email
- `:pivot 555-123-4567` - Search for phone number

The command automatically detects the identifier type and searches appropriate platforms:
- **Usernames**: Twitter, Instagram, GitHub, LinkedIn, Facebook, Reddit, YouTube, TikTok
- **Emails**: LinkedIn, Facebook, Twitter, GitHub, Instagram, Google
- **Phone numbers**: Truecaller, Whitepages, Facebook, LinkedIn

### 2. Platform-Internal Search (`:platform-search`)
Search within a specific social media platform using its native search functionality.

**Usage:**
```
:platform-search <platform> <query>
```

**Available Platforms:**
- Social Media: twitter, x, instagram, facebook, linkedin, github, reddit, youtube, tiktok, snapchat, telegram, discord, twitch, pinterest, vk, tumblr, medium, quora
- Professional: stackoverflow, behance, dribbble, deviantart
- Media: flickr, soundcloud, spotify, lastfm, goodreads
- E-commerce: yelp, tripadvisor, airbnb, etsy, ebay, amazon
- People Search: spokeo, pipl, truecaller, whitepages
- Search Engines: google, bing, duckduckgo, yandex, baidu

**Examples:**
- `:platform-search twitter "John Doe"`
- `:platform-search linkedin "software engineer Microsoft"`
- `:platform-search github "machine learning"`

### 3. Contextual Name Search (`:csearch`)
Combine a person's name with contextual information to narrow search results.

**Usage:**
```
:csearch <name> <context1> <context2> ...
```

**Examples:**
- `:csearch "John Doe" Microsoft Seattle` - Search for John Doe at Microsoft in Seattle
- `:csearch "Jane Smith" "Stanford University" "Computer Science"`
- `:csearch "Bob Johnson" "Tesla" "2020"`

This command:
- Opens searches in multiple search engines (Google, Bing, DuckDuckGo, Yandex)
- Creates site-specific searches for major social platforms
- Combines all context terms for precise results

### 4. Contact Syncing Emulation (`:syncprep`)
Prepares your browser for manual contact syncing workflows across platforms.

**Usage:**
```
:syncprep
```

Opens tabs for:
- Google Contacts
- Facebook Find Friends
- Instagram Discover People
- Twitter Contacts Import
- LinkedIn Connections
- Snapchat Add Friends
- Telegram Contacts
- WhatsApp Web
- Discord Friends
- Signal Contacts

**Workflow:**
1. Run `:syncprep` to open all contact pages
2. Add target phone numbers to your contacts
3. Use each platform's sync feature to find associated profiles

### 5. Reverse Phone Lookup (`:revphone`)
Search for information associated with a phone number.

**Usage:**
```
:revphone <phone>
```

**Supported Formats:**
- `5551234567`
- `555-123-4567`
- `(555) 123-4567`
- `+1-555-123-4567`

**Examples:**
- `:revphone 555-123-4567`
- `:revphone +442071234567`

Searches across:
- Reverse lookup services (Truecaller, Whitepages, Spokeo, BeenVerified)
- Social media platforms (Facebook, LinkedIn, Twitter, Instagram)
- Multiple phone number formats for better results

### 6. Reverse Email Lookup (`:revemail`)
Search for information associated with an email address.

**Usage:**
```
:revemail <email>
```

**Examples:**
- `:revemail john.doe@example.com`
- `:revemail contact@company.org`

Features:
- Searches the full email across search engines
- Extracts and searches the username portion separately
- Checks social media platforms
- Uses people search services

### 7. Social Connection Mapping (Userscript)
Extract social media profile links from the current page.

**Usage:**
Press `,x` while on a social media page listing followers/friends

**Features:**
- Automatically detects platform-specific profile patterns
- Extracts usernames and profile URLs
- Copies all URLs to clipboard
- Saves results to `~/Downloads/extracted_profiles.txt`
- Supports: Twitter/X, Instagram, Facebook, LinkedIn, GitHub, Reddit, YouTube, TikTok

### 8. SOCMINT Help (`:socmint-help`)
Display help information for all SOCMINT commands.

**Usage:**
```
:socmint-help
```

## Keyboard Shortcuts

The following keyboard shortcuts are configured for quick access:

| Shortcut | Action | Description |
|----------|--------|-------------|
| `,p` | `:pivot` | Start identifier pivoting |
| `,s` | `:platform-search` | Platform-specific search |
| `,c` | `:csearch` | Contextual name search |
| `,S` | `:syncprep` | Contact sync preparation |
| `,r` | `:revphone` | Reverse phone lookup |
| `,e` | `:revemail` | Reverse email lookup |
| `,x` | Extract profiles | Run profile extraction script |
| `,h` | `:socmint-help` | Show SOCMINT help |

## Search Engine Shortcuts

Quick search shortcuts (use with `:open` command):

| Shortcut | Platform | Example |
|----------|----------|---------|
| `tw` | Twitter | `:open tw john_doe` |
| `ig` | Instagram | `:open ig username` |
| `fb` | Facebook | `:open fb "John Doe"` |
| `li` | LinkedIn | `:open li "software engineer"` |
| `gh` | GitHub | `:open gh repository` |
| `reddit` | Reddit | `:open reddit topic` |
| `yt` | YouTube | `:open yt video_title` |

## Installation

### 1. Copy SOCMINT Module
```bash
cp qutebrowser/browser/socmint.py ~/Documents/qutebrowser/qutebrowser/browser/
```

### 2. Install Configuration Files
```bash
cp socmint_config.py ~/.config/qutebrowser/
cp config.py ~/.config/qutebrowser/
```

### 3. Install Userscript
```bash
mkdir -p ~/.config/qutebrowser/userscripts
cp extract_social_profiles.py ~/.config/qutebrowser/userscripts/
chmod +x ~/.config/qutebrowser/userscripts/extract_social_profiles.py
```

### 4. Restart qutebrowser
```bash
# Quit qutebrowser if running
# Start qutebrowser
python -m qutebrowser
```

## Testing

Run the test suite to verify installation:
```bash
python test_socmint.py
```

Expected output:
```
✓ All tests passed successfully!
```

## Use Cases

### 1. Username Investigation
```
:pivot johndoe123
```
Opens tabs searching for this username across all major platforms.

### 2. Email Investigation
```
:revemail suspicious@email.com
```
Searches for the email and associated username across platforms.

### 3. Phone Number Investigation
```
:revphone 555-867-5309
```
Performs reverse lookup and searches social media for the number.

### 4. Person Research
```
:csearch "John Smith" "Apple Inc" "Cupertino" "iOS developer"
```
Combines all context for targeted searches.

### 5. Social Network Analysis
1. Navigate to a user's followers page
2. Press `,x` to extract all profile links
3. Analyze the extracted data in `~/Downloads/extracted_profiles.txt`

## Privacy & Ethics

**Important Considerations:**
- Use these tools responsibly and ethically
- Respect privacy laws and regulations in your jurisdiction
- Only gather publicly available information
- Do not use for harassment, stalking, or illegal activities
- Consider the implications of your investigations
- Obtain proper authorization when conducting professional investigations

## Troubleshooting

### Commands Not Working
1. Check if the SOCMINT module is properly installed:
   ```bash
   ls -la ~/Documents/qutebrowser/qutebrowser/browser/socmint.py
   ```

2. Verify configuration is loaded:
   - Start qutebrowser
   - Check for "SOCMINT features loaded successfully!" message

3. Test a simple command:
   ```
   :socmint-help
   ```

### Userscript Not Working
1. Verify script is executable:
   ```bash
   chmod +x ~/.config/qutebrowser/userscripts/extract_social_profiles.py
   ```

2. Check Python shebang line is correct:
   ```bash
   head -1 ~/.config/qutebrowser/userscripts/extract_social_profiles.py
   ```

3. Test manually:
   ```bash
   python ~/.config/qutebrowser/userscripts/extract_social_profiles.py
   ```

### Performance Issues
- Limit the number of simultaneous tabs opened
- Close unnecessary tabs after investigation
- Use `:tab-only` to close all other tabs
- Consider increasing system resources

## Advanced Configuration

### Adding Custom Platforms
Edit `socmint.py` and add to `PLATFORM_SEARCH_URLS`:
```python
PLATFORM_SEARCH_URLS['custom_site'] = 'https://custom-site.com/search?q={}'
```

### Custom Keybindings
Edit `socmint_config.py`:
```python
config.bind('YOUR_KEY', 'COMMAND')
```

### Modifying Search Patterns
Edit the userscript `extract_social_profiles.py` to add platform-specific patterns:
```python
patterns['new_platform.com'] = [
    r'your_regex_pattern',
]
```

## Updates & Maintenance

To update the SOCMINT features:
1. Pull latest changes from repository
2. Re-run installation steps
3. Restart qutebrowser
4. Run tests to verify functionality

## Contributing

To contribute improvements:
1. Test your changes thoroughly
2. Update documentation
3. Add test cases for new features
4. Ensure backward compatibility

## License

GPL-3.0-or-later (same as qutebrowser)

## Support

For issues or questions:
- Check this documentation
- Review test output for errors
- Examine qutebrowser logs: `:messages`
- File issues on GitHub

---

**Note**: These features are designed for legitimate research, investigation, and security purposes. Always comply with applicable laws and ethical guidelines.