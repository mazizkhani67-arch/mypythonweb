file = open ("data.txt","r",encoding= "utf-8")
# content = file.read()
# print(content)
lines = file.readlines()
print(lines)
x = 1 
for line in lines:

    print( x ,":", line)
    x += 1
file.close()
file2 = open("data2.txt","w")
file2.write("new line added \n")
file2.close()
with open("data.txt","a") as file3:
   file3.write("\n class in dictionary")