from extension import scatterp
from tkinter import Tk,simpledialog
from tkinter.filedialog import asksaveasfilename

root = Tk()
root.withdraw()

file_path = asksaveasfilename(
    title="ذخیره فایل",
    defaultextension=".csv",
    filetypes=[("CSV File","*.csv"),("Text Files", "*.txt"), ("All Files", "*.*")]
)
fpn = simpledialog.askstring("شماره اول", "شماره اولین نقطه را وارد کنید:")
print(f"File path and Name is {file_path} ")
#file_name = input("Input File Name : ")
# tpoint = input("Input 1 for 'ENHD' or 2 for 'ENH': ")
#fpn = input("Input first point number (press enter for 1)   :")
print("_" * 30)
if fpn == None:
    point_number = 1
else :
    point_number = int(fpn)


# file_path = f"{file_name}.csv"#file name
with open(file_path,'w') as f:
    pass
Lable = ["PointNO","Easting","Northing","Height","Desc"] #
e = True
coor = [None]*5


while e == True:
    print("-"*30) 
    for i  in range(5):
        if i == 0 :
            print(f"NO = {point_number}")
            value = point_number
        else:    
            input_title = f"{Lable[i]} = "
            value = input(input_title)

            if value== "" :
                if Lable[i] == "Easting" or Lable[i] == "Northing":
                    e = False
                    print("Error")
                    break
                elif Lable[i] == "Height":
                    value = "0"
            if value == "end" :
                e = False
                break
        coor[i]=value   
     
    if e:          
        coordinate = f"{point_number},{coor[0]},{coor[1]},{coor[2]},{coor[3]},\n"
        with open(file_path,'a') as file:
            file.write(coordinate)
        point_number += 1 


if e:
    scatterp(file_path)
