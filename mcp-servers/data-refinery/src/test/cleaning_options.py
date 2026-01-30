import pytest
from pydantic import ValidationError
from data_refinery.domain.models.cleaning import CleaningOptions

def test_cleaning_options_invalid_strategy():
    """
    Test that providing an unknown strategy raises a ValidationError.
    """
    # We use 'with pytest.raises(...)' to catch the specific error
    with pytest.raises(ValidationError) as exc_info:
        CleaningOptions(
            normalize_headers=True,
            strategies={"age": "magic_wand"}  # "magic_wand" is not allowed!
        )

    # Now we inspect the error message to make sure it's the RIGHT error
    # We convert the error to a string and check for key phrases
    error_message = str(exc_info.value)
    
    assert "Input should be 'drop', 'zero', 'mean', 'mode' or 'unknown'" in error_message
    

def test_cleaning_options_valid_strategy():
    """
    Test that valid strategies are accepted and stored correctly.
    """
    # 1. Create the object with VALID data (e.g., age='mean', email='drop')
    options = CleaningOptions(
        normalize_headers=True,
        strategies={"age" : "mean", "email" : "unknown"} # <--- Fill this in!
    )

    # 2. Assertions: Check if the values are correct
    assert options.normalize_headers is True
    assert options.strategies["age"] == "mean"  # <--- What should this be?
    assert options.strategies["email"] == "unknown"