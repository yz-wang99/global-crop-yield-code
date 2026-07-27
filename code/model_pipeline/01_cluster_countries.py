"""Step 1: cluster countries by crop-growing-season phenology.

This script reproduces the clustering step described in the Methods. The
input CSV must have one row per country, ``adm0_name`` in the first column, and
the two phenology quantities used for clustering in columns 2 and 3. In the
analysed files these are ``MEAN`` and ``MEAN_12`` (planting and harvest
calendar positions). The code selects these fields by position, not name, so
do not insert a column before them.

All non-country columns are MinMax-scaled, but only those first two scaled
phenology columns enter the Ward dendrogram and agglomerative partition. The
output retains the input columns and adds/replaces ``class`` with an integer
phenology label.
"""

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN, KMeans
from sklearn.cluster import kmeans_plusplus
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import fcluster

# Select the crop identifier used in the local input and output filenames.
crop = 'wheat'    #rice, soybean, maize

# Replace the machine-specific path with the crop-calendar summary CSV.
df = pd.read_csv(fr'E:\D盘WYZ\SPAM2020\cluster\{crop}.csv')

scaler = MinMaxScaler()
numeric_cols = df.columns[df.columns != 'adm0_name']
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

country = list(df['adm0_name'])

plt.figure(figsize=(10, 7))
plt.title(f'{crop}', fontsize=20, fontweight='bold', loc='left')

# Ward linkage with Euclidean distance is applied to planting/harvest features.
Z = shc.linkage(df.iloc[:, 1:3], method='ward')
dend = shc.dendrogram(Z)
plt.axhline(y=0.8, color='r', linestyle='--')

plt.tight_layout()
plt.savefig(fr"E:\D盘WYZ\Process_country(Non_scale)\jpg\dendrogram{crop}.jpg", dpi=300, format="jpg", bbox_inches="tight")
plt.show()

# The cluster count must match the crop-specific downstream season windows.
# clusters = AgglomerativeClustering(n_clusters=4, metric='euclidean', linkage='ward')
max_d = 1.5  #Determine the threshold through a tree diagram
clusters = fcluster(Z, max_d, criterion='distance')
labels = clusters.fit_predict(df.iloc[:, 1:3])
df['class'] = labels
counts = pd.value_counts(labels,sort=True)
print(counts)
# Output schema: the country input table plus the downstream-required ``class`` field.
#df.to_csv(fr'E:\D盘WYZ\SPAM2020\cluster\{crop}_cluster_final.csv', index=False)
