# Preprocessing
Rows missing user, movie, or rating are dropped; duplicate user/movie pairs retain the latest row; rating values outside 0.5–5 are removed. User and movie identifiers are normalized, timestamp retained, and the rating matrix is a SciPy CSR sparse matrix. Evaluation splits rows before fitting similarities.
