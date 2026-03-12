class MediaItem(object):
    def __init__(self, title, author, is_avaible=True):
        self.title = title
        self.author = author
        self.is_avaible = is_avaible
    def __str__(self) -> str:
        status = "Available" if self.is_avaible else "Checked Out"
        return f"Title by Author [{status}]"
    def checkout(self) -> str:
        if self.is_avaible:
            self.is_avaible = False
            return "Checked out successfully."
        else:
            return "Already out."
    def return_item(self):
        self.is_avaible = True
        
if __name__ == "__main__":
    book1 = MediaItem("Cin Ali", "Mahmut Ekrem")
    movie1= MediaItem("No Country for Old Mens", "Joel Coen")

    print(book1)
    print(book1.checkout())
    print(book1.checkout())

    print(movie1)
    print(movie1.checkout())
    print(movie1.checkout())
    print(movie1.return_item())
    print(movie1.checkout())
