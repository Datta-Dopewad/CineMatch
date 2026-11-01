from preprocessing.data_validation import validate
from preprocessing.duplicate_removal import remove_duplicates
from preprocessing.missing_values import handle_missing

def clean(ratings):
    ratings = handle_missing(ratings)
    ratings = remove_duplicates(ratings)
    return validate(ratings)
