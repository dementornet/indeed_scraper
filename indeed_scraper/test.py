import pandas as pd
import pandasgui

df = pd.DataFrame(pd.read_csv("jobs.csv"))
pandasgui.show(df)