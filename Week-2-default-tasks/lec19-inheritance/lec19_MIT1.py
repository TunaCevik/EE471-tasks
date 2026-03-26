from lec19_MIT import Animal
###################### YOU TRY IT ####################
# Write a function that meets this spec.
# def make_animals(L1, L2):
#     """ L1 is a list if ints and L2 is a list of str
#         L1 and L2 have the same length
#     Creates a list of Animals the same length as L1 and L2.
#     An animal object at index i has the age and name
#     corresponding to the same index in L1 and L2, respectively. """
#     # your code here


L1 = [2,5,1]
L2 = ["blobfish", "crazyant", "parafox"]
# animals = make_animals(L1, L2)
# print(animals)     # note this prints a list of animal objects
# for i in animals:  # this prints the indivdual animals
#     print(i)

def make_animals(L1, L2):
    """ L1: yaş listesi (int), L2: isim listesi (str) """
    animals_list = []
    
    # İki listenin de aynı uzunlukta olduğunu biliyoruz
    for i in range(min(len(L1), len(L2))):
        # Her bir indeks için yeni bir Animal objesi oluştur [cite: 108]
        new_animal = Animal(L2[i], L1[i]) 
        # NOT: Senin sınıfında name başta None, o yüzden set_name kullanabilirsin
        new_animal.set_name(L2[i]) 
        animals_list.append(new_animal)
        
    return animals_list


def make_animals_zip(L1, L2):
    # zip(L1, L2) -> (2, "blobfish"), (5, "crazyant")... şeklinde çiftler oluşturur
    return [Animal(name, age) for age, name in zip(L1, L2)]


animals = make_animals(L1, L2)
print(type(animals))     # note this prints a list of animal objects


animals_zip = make_animals_zip(L1, L2)
print(type(animals_zip)) # note this also prints a list 

print(animals[0].get_name())
print(Animal.get_name(animals[0]))