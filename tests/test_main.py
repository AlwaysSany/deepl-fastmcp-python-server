import pytest
from unittest.mock import patch, MagicMock
import main

@pytest.fixture(autouse=True)
def patch_deepl_translator():
    with patch.object(main.server, 'translator') as mock_translator:
        yield mock_translator

def test_translate_text_basic(patch_deepl_translator):
    mock_result = MagicMock()
    mock_result.text = 'Hallo Welt'
    mock_result.detected_source_lang = 'EN'
    patch_deepl_translator.translate_text.return_value = mock_result

    response = main.translate_text(
        text='Hello world',
        target_language='DE'
    )
    assert response['success'] is True
    assert response['translated_text'] == 'Hallo Welt'
    assert response['detected_source_language'] == 'EN'
    assert response['target_language'] == 'DE'


def test_get_source_languages(patch_deepl_translator):
    mock_lang = MagicMock()
    mock_lang.code = 'EN'
    mock_lang.name = 'English'
    patch_deepl_translator.get_source_languages.return_value = [mock_lang]

    response = main.get_source_languages()
    assert response['success'] is True
    assert response['source_languages'][0]['code'] == 'EN'
    assert response['source_languages'][0]['name'] == 'English'


def test_get_target_languages(patch_deepl_translator):
    mock_lang = MagicMock()
    mock_lang.code = 'DE'
    mock_lang.name = 'German'
    patch_deepl_translator.get_target_languages.return_value = [mock_lang]

    response = main.get_target_languages()
    assert response['success'] is True
    assert response['target_languages'][0]['code'] == 'DE'
    assert response['target_languages'][0]['name'] == 'German'
