numbers = [10, 20, 30, 40,50]
names = ["ali", "mahdi" , "Reza"]
print(numbers[0])
print(numbers[-1])
print(numbers[1])
numbers[2] = 999
numbers.append(60)
numbers.insert(1 , 15)
numbers.remove(40)
del numbers[0]

print(numbers)
print(len(numbers))
print(max(names))
print(max(numbers))
print(sum(numbers))


print(type(names))