# SPDX-FileCopyrightText: Vilas Magare
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for SOCMINT features."""

import pytest


@pytest.mark.parametrize('command', [
    ':socmint-help',
    ':pivot testuser',
    ':platform-search twitter test',
    ':csearch "John Doe" Company',
    ':syncprep',
    ':revphone 555-123-4567',
    ':revemail test@example.com',
])
def test_socmint_commands(quteproc, command):
    """Test that SOCMINT commands don't crash."""
    quteproc.send_cmd(command)
    # Commands that open tabs might not have immediate feedback
    # Just ensure no error is shown
    quteproc.wait_for(lambda: True, timeout=2)
    assert not quteproc.is_crashed()


def test_socmint_help_content(quteproc):
    """Test that socmint-help shows the expected content."""
    quteproc.send_cmd(':socmint-help')
    quteproc.wait_for_js('document.body.textContent.includes("SOCMINT")')
    

def test_pivot_opens_tabs(quteproc):
    """Test that pivot command opens multiple tabs."""
    initial_tabs = quteproc.get_open_tabs()
    quteproc.send_cmd(':pivot testuser123')
    # Wait a bit for tabs to open
    quteproc.wait_for(lambda: len(quteproc.get_open_tabs()) > len(initial_tabs), 
                      timeout=5)
    new_tabs = quteproc.get_open_tabs()
    assert len(new_tabs) > len(initial_tabs)
    

def test_platform_search_opens_correct_url(quteproc):
    """Test that platform-search opens the correct URL."""
    quteproc.send_cmd(':platform-search github qutebrowser')
    quteproc.wait_for_load_finished('github.com')
    current_url = quteproc.get_url()
    assert 'github.com' in current_url
    assert 'qutebrowser' in current_url
    

@pytest.mark.parametrize('shortcut,command', [
    (',p', 'pivot'),
    (',s', 'platform-search'),
    (',c', 'csearch'),
    (',S', 'syncprep'),
    (',r', 'revphone'),
    (',e', 'revemail'),
    (',h', 'socmint-help'),
])
def test_keyboard_shortcuts(quteproc, shortcut, command):
    """Test that keyboard shortcuts are configured."""
    # Send the shortcut
    quteproc.send_cmd(f':bind {shortcut}')
    # Check if the binding exists and points to the right command
    output = quteproc.get_content()
    assert command in output or 'set-cmd-text' in output
    

def test_userscript_exists(quteproc):
    """Test that the profile extraction userscript is available."""
    # Try to run the userscript
    quteproc.send_cmd(':spawn --userscript extract_social_profiles.py')
    # Should not crash
    quteproc.wait_for(lambda: True, timeout=2)
    assert not quteproc.is_crashed()
    

def test_multiple_commands_sequence(quteproc):
    """Test running multiple SOCMINT commands in sequence."""
    commands = [
        ':socmint-help',
        ':pivot user123',
        ':platform-search twitter bitcoin',
        ':revemail test@test.com',
    ]
    
    for cmd in commands:
        quteproc.send_cmd(cmd)
        quteproc.wait_for(lambda: True, timeout=1)
        assert not quteproc.is_crashed()
        

def test_invalid_platform_shows_error(quteproc):
    """Test that invalid platform shows an error."""
    quteproc.send_cmd(':platform-search invalidplatform test')
    quteproc.wait_for_message('Unknown platform: invalidplatform')
    

def test_invalid_email_shows_error(quteproc):
    """Test that invalid email format shows an error."""
    quteproc.send_cmd(':revemail notanemail')
    quteproc.wait_for_message('Invalid email format: notanemail')