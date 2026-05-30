class dog:
    def __init__(self,name,breed,age):
        self.name = name
        self.breed = breed
        self.age = age
    def bark(self):
        print(f"{self.name} say hop hop")
    def description(self):
        return (f"{self.name} is {self.breed} and is {self.age}")
    def birthday(self):
        self.age +=1
        print(f"happy birthday {self.name}!!!")

my_dog = dog("boby","german",3)
your_dog = dog("loucy","podel",1)
print(my_dog.name)
print(your_dog.breed)

my_dog.bark()
(your_dog.description())
your_dog.birthday()


class GuideDog(dog):
    def __init__(self, name, breed, age,owner_name):
        super().__init__(name, breed, age)
        self.owner_name = owner_name
    def lead(self):
        print(f"{self.name} is leading {self.owner_name}")
    def bark(self):
        print(f"{self.name} quitly hop hop")
my_guide_dog = GuideDog("jessy","ghdrejoon",5,"sefollah")
print(my_guide_dog.description())
my_guide_dog.lead()
my_guide_dog.bark()