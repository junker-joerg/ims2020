import statsmodels.api as sm
import pandas as pd
data = sm.datasets.longley.load_pandas()
df = pd.DataFrame(data.data)

data.data.head(5)
