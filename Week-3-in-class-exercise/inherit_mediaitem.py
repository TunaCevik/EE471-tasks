from custom_classes import MediaItem

class Book(MediaItem):
    def __init__(self, title, author, page_count, is_avaible=True):
        super().__init__(title, author, is_avaible)
        self.page_count = page_count
    def __str__(self) -> str:
        status = "Available" if self.is_avaible else "Not Available"
        return f"📖 Book: {self.title} | Author: {self.author} | Pages: {self.page_count} [{status}]"
    

class DVD(MediaItem):
    def __init__(self, title, author, duration, is_avaible=True):
        super().__init__(title, author, is_avaible)
        self.duration = duration

    def __str__(self) -> str:
        status = "Available" if self.is_avaible else "Not Available"
        return f"🎬 DVD: {self.title} | Director: {self.author} | Duration: {self.duration} mins [{status}]"
    
    def checkout(self) -> str:
        mesaj = super().checkout()  # Run that original checkout method to update availability
        if mesaj == "Checked out successfully.":
            return "Handle with care: Do not scratch the disc."
        else:
            return "DVD is already checked out."


# Discussion Point: What is the use of super() here? What happens if we change the logic in MediaItem.checkout() later?
# If we change the logic in MediaItem.checkout(), the DVD classes if else block will not be working as expected.





