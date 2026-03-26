
# We will learn about inherince we will use inheritance object instead of generic python object
# class definition | name | class parent
class Animal(object):
    def __init__(self, name, age): # self i the variable to refer an instance of the class
        self.age = age
        self.name = None # name is a data attribute even thoug an isntace is not initialized with it as a param
    def __str__(self):
        return "Animal: " + str(self.name) + " is " + str(self.age) + " years old" 
    
    def get_age(self):
        return self.age
    def set_age(self, new_age):
        self.age = new_age

    def get_name(self):
        return self.name
    def set_name(self, new_name):
        self.name = new_name


### EXAMPLE: using Animal objects in code
def animal_dict(L):
    """ L is a list
    Returns a dict, d, mappping an int to an Animal object. 
    A key in d is all non-negative ints, n, in L. A value 
    corresponding to a key is an Animal object with n as its age. """
    d = {}
    for n in L:
        if type(n) == int and n >= 0:
            d[n] = Animal("", n)
    return d

if __name__ == "__main__":
    a = Animal(None, 3)
    print(a)
    print(a.age) # getting the internal data attribute
    print(type(a.get_name()))

    a.set_name("Fido")
    print(type(a.get_name()))

    L = [2,5,'a',-5,0]
    animals = animal_dict(L)
    
    for n,a in animals.items():   
        print(f'key {n} with val {a}')
    # loop above prints animal:None:2 
    #                   animal:None:5 
    #                   animal:None:0


    print(animals)
    # above prints {2: <__main__.Animal object at 0x00000199AFF350A0>, 
    #               5: <__main__.Animal object at 0x00000199AFF35A30>, 
    #               0: <__main__.Animal object at 0x00000199AFF35D00>}
