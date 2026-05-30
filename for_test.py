names = ["Ali","Mohammad","Hosein"]
for name in names:
    print("Hi",name)
for i in range(6):
    s = 1
    s = s * i
   
    print(s)

    s = s * i
x =  0 


def end_number():
    print ("test")
end_number()
def hi(name):
    return(f"Hi to {name}")
print(hi("seyfollah"))
def check_name(name):
    if name == "MOhammad":
        return("yes")
    else:
        return("No")
    

print(check_name("aliboz"))
def avg(numbers):
    total = sum(numbers)
    return total/len(numbers)

print(avg([1,2,3]))