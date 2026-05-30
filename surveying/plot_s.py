
import matplotlib.pyplot as plt

x = [1,2,3,4,5,6,7,8]
y = [1,4,9,16,25,36,49,64]

plt.scatter(x,y, color='blue',marker='o',label='points')
plt.grid(True)


plt.show()

import seaborn as sns
import pandas as pd
data = {
    'height':[160,170,180,155,165,175,185,150,160,170],
    'weight':[60,70,85,50,58,75,90,45,55,65],
    'gender':['f','m','f','m','f','m','f','m','f','m']
}
df = pd.DataFrame(data)

sns.scatterplot(data=df,x='height',y='weight',hue='gender',style='gender',s=100)

plt.title('رابطه ')
plt.grid(True)

plt.show()