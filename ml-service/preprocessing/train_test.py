from sklearn.model_selection import train_test_split
def split(ratings, test_size=0.2, seed=42):
    train, test = train_test_split(ratings, test_size=test_size, random_state=seed)
    return train.copy(), test.copy()
