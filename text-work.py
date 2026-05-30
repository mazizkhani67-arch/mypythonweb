
# -*- coding: utf-8
a = "Mohammad"
b= "Family"
c = a + "**" + b
print(c)
print("-" * 30)
print(c.upper())
print(c.lower())
d = "      Python Fun      "
print(d.strip())
print(d.rstrip())
print(d.lstrip())
print("*" * 10)
e = c.replace("Family", "Azizkhani")
print(e)
print("!" * 10)
with open("Meli.txt","r") as file:
   lines = file.readlines()
for line in lines:
   print("@" * 10)
   words = line.split(" ")
   fff = line.find("Parsa")
   if fff == 0:
     print("jigar")
   else: 
      print("bacheho")
   print("#" * 10)
   print(line)
   print("$" * 10)
   print(words)
   print("% " * 10)
   seperator = "^^"
   newword = seperator.join(words)
   print(newword)