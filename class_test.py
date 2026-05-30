class home:
    def __init__(self,name,structure,face):
        self.name = name
        self.structure = structure
        self.face =  face
    def earthquake(self) :
        print("ooops")

my_home = home("morvarid","brick","brick")
print(my_home.name)
my_home.earthquake()
class royal_home(home):
    def __init__(self, name, structure, face,age):
        super().__init__(name, structure, face)
        self.age = age
    def earthquake(self):
        print("badbakht shodim")
    def sage(self):
        print(f"its age{self.age}")

myroyal = royal_home("morvarid","brick","brick","300")
print(myroyal.age)
myroyal.earthquake()
myroyal.sage()