# Can create instances of a Coordinate object
# (3,4) (1,1)
# Decide what data elements constitute an object in a 2D plane
# A coordinate is defined by x and y value

# Decide what to do with coordinates
# Tell us how far away the coordinate is on the x or y axes
# Measure the distance between two coordinates, Pythagoras

#class definition name/type class parent
class Coordinate(object):
    #define attributes of the class here
    def __init__(self, xval, yval): # self is a first parameter of a method, a function that only works with an object of this class of this type
        # this is a function that only works with an object of this class, and it is called when we create an instance of the class
        # self: parameter to refer to an instance oth xlass without having created one yet, xval and yval: what data initializes an Coordinate object
        # x=xval, y=yval as soon as __init__ function terminates, this regular variables will be gone. But self.x and self.y will be part of the object, and they will be initialized to xval and yval, and they will be available as long as the object  (28. dk güzel cümle),
        #But in order to have these variables, x and y, persist throughout the lifetime of my object, I' ve defined them using self.x and self.y
        self.x = xval
        self.y = yval
    def distance(self, other):
        x_diff_sq = (self.x - other.x)**2
        y_diff_sq = (self.y - other.y)**2
        return (x_diff_sq + y_diff_sq)**0.5

# There is a object named c, and it is an instance of the Coordinate class, and it has attributes x and y, and they are initialized to 3 and 4 respectively
c = Coordinate(3,4) # create an instance of the Coordinate class, c is an object of type Coordinate, c is an instance of the Coordinate class, c is a Coordinate object
origin = Coordinate(0,0)
print(c.x)
print(origin.x)
print(c.distance(origin))
print(origin.x)