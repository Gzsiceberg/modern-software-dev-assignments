import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_llm_bullet_list():
    text = """
    Meeting notes:
    - Review the pull request
    - Fix the authentication bug
    - Update the documentation
    """
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert all(isinstance(item, str) for item in items)


def test_extract_llm_keyword_prefixes():
    text = """
    Todo: Implement the user profile feature
    Action: Schedule team meeting for tomorrow
    Next: Review the design mockups
    """
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert all(isinstance(item, str) for item in items)


def test_extract_llm_empty_input():
    text = ""
    items = extract_action_items_llm(text)
    assert items == []

    text_whitespace = "   \n\n  \t  "
    items_whitespace = extract_action_items_llm(text_whitespace)
    assert items_whitespace == []


def test_extract_llm_mixed_content():
    text = """
    Today we had a productive meeting.
    
    Action items:
    - Complete the API integration
    - Write unit tests for the new module
    - Update the user interface
    
    We also discussed the roadmap for Q1.
    """
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert all(isinstance(item, str) for item in items)
