import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# flatten function
class point:
    def __init__(self,easting,northing,height,description):
        self.Easting= easting
        self.northing = northing
        self.height = height
        self.description = description
    
def flattens(points):
    for point in points:
        points[2] = 0
        
    return points
    if __name__ == "__main__":
       points = input("enter one Point to flatten : ")
       flatten(points)

def scatterp(file_path):
    with open(file_path,"r") as file:
        lines = file.readlines()

    Cop = len(lines) # Count Of Points
    print(Cop)
    X = []
    Y = []
    H = []
    D = [] 
    x = 1
    for line in lines:
        if x ==1 :
          x+=1
        else:   
             Coordinate = line.split(",")
             X.append(int(Coordinate[1]))
             Y.append(int(Coordinate[2]))
             H.append(int(Coordinate[3]))
             D.append(Coordinate[4])
             x +=1


    #plt.scatter(X,Y, color='blue',marker='o',label='points')
    #plt.grid(True)

    #plt.show()

    data = {
        "Easting":X,
        "Northing":Y,
        "Height":H,
        "Code":D
    }
    df = pd.DataFrame(data)

    sns.scatterplot(data=df,x='Easting',y='Northing',hue='Code',style='Code', s=100)

    plt.title('Points view')
    plt.grid(True)

    plt.show()

    if __name__ == "__main__":
       points = input("Enter File Points(txt) : ")
       scatterp(file_path)