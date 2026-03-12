from custom_classes import MediaItem
from inherit_mediaitem import Book, DVD 

class LibraryCollection:
    def __init__(self):
        self.collection: list[MediaItem] = []

    def add_item(self, item: MediaItem) -> None:
        self.collection.append(item)
        print(f"Kütüphaneye eklendi: '{item.title}'")

    def list_available(self) -> None:
        print("\n--- (Available) ---")
        
        is_avaliable = False
        
        for item in self.collection:
            if item.is_avaible: 
                print(f"- {item.title}")
                is_avaliable = True
                
        if not is_avaliable:
            print("Şu an kütüphanede mevcut eser bulunmuyor.")


if __name__ == "__main__":
    my_library = LibraryCollection()

    book1 = Book("Cin Ali", "Mahmut Ekrem", 50)
    dvd1 = DVD("No Country for Old Men", "Joel Coen", 122)
    breakpoint()
    book2 = Book("Nutuk", "Mustafa Kemal Atatürk", 600)

    my_library.add_item(book1)
    my_library.add_item(dvd1)
    my_library.add_item(book2)

    my_library.list_available()

    print("\n[İşlem]: Cin Ali ödünç alınıyor...")
    book1.checkout()

    my_library.list_available()