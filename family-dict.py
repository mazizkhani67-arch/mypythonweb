family = {
    "lastName":{"f1":"Azizkhani","f2":"azdanshenas"},
    "Home": {"H1":"Seydan","H2":"anaytebad"},
    "age": {"a1":"200","a2":"100"}
}
print(family["Home"] ["H1"])
family["Power"] = "GOD"
print(family)
for key in family:
    print(key)

for key, value in family.items():
    print(key, ":" ,value)