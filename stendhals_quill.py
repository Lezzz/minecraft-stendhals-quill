import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import re
import os
import math
from PyPDF2 import PdfReader
import unicodedata
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='book_processor_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_front_page(title, author, book_type, library_name, book_number=None, total_books=None):
    """
    Create the front page of a Minecraft book.
    
    Args:
    - title (str): The title of the book
    - author (str): The author of the book
    - book_type (str): The type of the book
    - library_name (str): The name of the library
    - book_number (int, optional): The number of this book in a series
    - total_books (int, optional): The total number of books in the series
    
    Returns:
    - str: Formatted front page content
    """
    subtitle = f"§4§lBook {book_number} of {total_books}" if book_number is not None else ""
    return f"""§4§l§o{title}
§7by {author}

{subtitle}
§c✧ §7§o{book_type} §c✧






§4§o{library_name} §r"""

def create_second_page():
    """
    Create the second page of a Minecraft book (approval seal).
    
    Returns:
    - str: Formatted second page content
    """
    return """

    

       §b✧ §6W§bX§6Y§bZ §b✧
          §6SEAL
           §bOF
       §6APPROVAL
"""

def create_end_page(title, author, brought_by, library_name, book_number, total_books):
    """
    Create the end page of a Minecraft book.
    
    Args:
    - title (str): The title of the book
    - author (str): The author of the book
    - brought_by (str): Who brought the book in-game
    - library_name (str): The name of the library
    - book_number (int): The number of this book in a series
    - total_books (int): The total number of books in the series
    
    Returns:
    - str: Formatted end page content
    """
    return f"""§4§l§oEnd of ✦ {title} ✦
Book {book_number} of {total_books}
§7by {author}



§7Brought in-game by:
§b✧ §6{brought_by}§b ✧

  
§4{library_name}"""

def split_into_pages(text, max_chars=220):
    """
    Split the input text into pages based on a maximum character limit.
    
    Args:
    - text (str): The input text to be split
    - max_chars (int): Maximum number of characters per page
    
    Returns:
    - list: List of pages (strings)
    """
    pages = []
    current_page = ""
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        if paragraph.startswith('§'):  # Check if the paragraph starts with a formatting code
            pages.append(paragraph)  # Add the formatted paragraph as a whole page
            continue

        words = paragraph.split()
        for word in words:
            if len(current_page) + len(word) + 1 <= max_chars:
                current_page += word + " "
            else:
                pages.append(current_page.strip())
                current_page = word + " "
        
        if current_page:
            pages.append(current_page.strip())
            current_page = ""

    if current_page:
        pages.append(current_page.strip())

    return pages

def remove_links(text):
    """
    Remove various forms of links from the text.
    
    Args:
    - text (str): Input text
    
    Returns:
    - str: Text with links removed
    """
    text = re.sub(r'https?:?/?/?(?:\s?/?\s?)+\S+', '', text)
    text = re.sub(r'www\.?\s?\S+', '', text)
    text = re.sub(r'(\w+\.)+\w{2,}', '', text)
    return text

def filter_sensitive_words(text):
    """
    Filter out sensitive words from the text.
    
    Args:
    - text (str): Input text
    
    Returns:
    - str: Text with sensitive words replaced by [redacted]
    """
    sensitive_words = ['bad word']  # Add more words as needed

    def normalize_caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())

    normalized_text = normalize_caseless(text)

    for word in sensitive_words:
        normalized_word = normalize_caseless(word)
        pattern = re.compile(re.escape(normalized_word), re.IGNORECASE)
        text = re.sub(pattern, '[redacted]', text)
    
    return text

def process_text(text):
    """
    Process the input text by removing links and filtering sensitive words.
    
    Args:
    - text (str): Input text
    
    Returns:
    - str: Processed text
    """
    text = remove_links(text)
    text = filter_sensitive_words(text)
    return text

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
    - pdf_path (str): Path to the PDF file
    
    Returns:
    - str: Extracted and processed text from the PDF
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        return process_text(text)
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

class BookProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Stendhal's Quill - Bringing real-life books into Minecraft")
        master.geometry("1200x800")  # Increased width for better wide screen support

        self.input_file = ""
        self.output_folder = "default_path_here"
        self.title = ""
        self.author = ""
        self.book_type = ""
        self.brought_by = ""
        self.library_name = "Library of [your_name_here]"  # Default library name
        self.books = []
        self.current_book = 0
        self.current_page = 0

        self.create_widgets()

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Create left and right frames for better layout
        left_frame = tk.Frame(self.master)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(self.master)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Left frame widgets
        tk.Button(left_frame, text="Select Input File (PDF or TXT)", command=self.select_input_file).pack(pady=5, fill=tk.X)
        self.input_label = tk.Label(left_frame, text="No file selected")
        self.input_label.pack(fill=tk.X)

        tk.Button(left_frame, text="Select Output Folder (Optional)", command=self.select_output_folder).pack(pady=5, fill=tk.X)
        self.output_label = tk.Label(left_frame, text="Using default folder")
        self.output_label.pack(fill=tk.X)

        tk.Label(left_frame, text="Book Title:").pack(pady=5)
        self.title_entry = tk.Entry(left_frame, width=50)
        self.title_entry.pack(fill=tk.X)

        tk.Label(left_frame, text="Author:").pack(pady=5)
        self.author_entry = tk.Entry(left_frame, width=50)
        self.author_entry.pack(fill=tk.X)

        tk.Label(left_frame, text="Book Type:").pack(pady=5)
        self.book_type_entry = tk.Entry(left_frame, width=50)
        self.book_type_entry.pack(fill=tk.X)

        tk.Label(left_frame, text="Brought in-game by (leave blank for default):").pack(pady=5)
        self.brought_by_entry = tk.Entry(left_frame, width=50)
        self.brought_by_entry.pack(fill=tk.X)

        tk.Label(left_frame, text="Library Name:").pack(pady=5)
        self.library_name_entry = tk.Entry(left_frame, width=50)
        self.library_name_entry.insert(0, self.library_name)
        self.library_name_entry.pack(fill=tk.X)

        tk.Button(left_frame, text="Process Book", command=self.process_book).pack(pady=10, fill=tk.X)

        # Right frame widgets
        self.book_nav = ttk.Combobox(right_frame, state="readonly")
        self.book_nav.pack(pady=5, fill=tk.X)
        self.book_nav.bind("<<ComboboxSelected>>", self.show_selected_book)

        self.page_viewer = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=60, height=15)
        self.page_viewer.pack(pady=10, fill=tk.BOTH, expand=True)

        self.page_matrix_frame = tk.Frame(right_frame)
        self.page_matrix_frame.pack(pady=10, fill=tk.X)

        tk.Button(right_frame, text="Copy Current Page", command=self.copy_page).pack(fill=tk.X)

    def select_input_file(self):
        """Open a file dialog to select the input file (PDF or TXT)."""
        self.input_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
        self.input_label.config(text=self.input_file)

    def select_output_folder(self):
        """Open a folder dialog to select the output folder."""
        self.output_folder = filedialog.askdirectory()
        if not self.output_folder:
            self.output_folder = os.path.join(os.path.expanduser("~"), "minecraft_books")
            self.output_label.config(text="Using default folder")
        else:
            self.output_label.config(text=self.output_folder)

    def process_book(self):
        """Process the input file and create Minecraft books."""
        logging.info("Starting book processing")
        if not self.input_file or not self.title_entry.get() or not self.author_entry.get() or not self.book_type_entry.get():
            messagebox.showerror("Error", "Please fill in all required fields.")
            logging.error("Missing required fields")
            return

        if not self.output_folder:
            self.output_folder = os.path.join(os.path.expanduser("~"), "minecraft_books")

        self.title = self.title_entry.get()
        self.author = self.author_entry.get()
        self.book_type = self.book_type_entry.get()
        self.brought_by = self.brought_by_entry.get() or "Anonymous"
        self.library_name = self.library_name_entry.get()

        logging.info(f"Processing book: {self.title} by {self.author}")

        try:
            # Extract and process text from the input file
            if self.input_file.lower().endswith('.pdf'):
                content = extract_text_from_pdf(self.input_file)
            else:
                with open(self.input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = process_text(content)

            # Split the content into pages
            all_pages = split_into_pages(content)
            logging.info(f"Split content into {len(all_pages)} pages")

            # Organize pages into books
            self.books = []
            current_book = []
            total_pages = len(all_pages)
            max_pages_per_book = 97  # Maximum pages per book, leaving room for front, second, and end pages

            for i, page in enumerate(all_pages):
                current_book.append(page)
                
                # Check if we've reached the max pages for this book or if it's the last page
                if len(current_book) == max_pages_per_book or i == total_pages - 1:
                    self.books.append(current_book)
                    current_book = []

            logging.info(f"Created {len(self.books)} books")

            # Add front, second, and end pages to each book
            for i, book in enumerate(self.books):
                front_page = create_front_page(self.title, self.author, self.book_type, self.library_name, i+1, len(self.books))
                book.insert(0, front_page)
                book.insert(1, create_second_page())
                end_page = create_end_page(self.title, self.author, self.brought_by, self.library_name, i+1, len(self.books))
                book.append(end_page)

            # Write the books to files
            self.write_stendhal_files()
            self.update_book_viewer()
        except Exception as e:
            logging.exception("An error occurred while processing the book")
            messagebox.showerror("Error", f"An error occurred while processing the book: {str(e)}")

    def write_stendhal_files(self):
        """Write processed books to Stendhal-compatible files."""
        logging.info("Starting to write Stendhal files")
        for i, book in enumerate(self.books):
            filename = f"{self.title.replace(' ', '_')}_Book_{i+1}.stendhal"
            filepath = os.path.join(self.output_folder, filename)
            logging.info(f"Writing file: {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"title: {self.title} - Book {i+1}\n")
                f.write(f"author: {self.author}\n")
                f.write("pages:\n")
                for page_num, page in enumerate(book):
                    logging.debug(f"Writing page {page_num+1} of Book {i+1}")
                    f.write("#- \n")
                    f.write(page + "\n")
            logging.info(f"Finished writing file: {filepath}")
        messagebox.showinfo("Success", f"Created {len(self.books)} Stendhal file(s) in {self.output_folder}")
        logging.info(f"Successfully created {len(self.books)} Stendhal file(s)")

    def update_book_viewer(self):
        """Update the book viewer with processed books."""
        if not self.books:
            messagebox.showinfo("Info", "No books were created. Please check your input file.")
            return
        self.book_nav['values'] = [f"Book {i+1}" for i in range(len(self.books))]
        self.book_nav.current(0)
        self.show_selected_book()

    def show_selected_book(self, event=None):
        """Display the selected book in the page viewer."""
        if not self.books:
            return
        self.current_book = self.book_nav.current()
        self.master.after(100, self.create_page_matrix)  # Delay to ensure widget sizes are updated
        self.show_page(0)

    def create_page_matrix(self):
        """Create a matrix of buttons for page navigation."""
        for widget in self.page_matrix_frame.winfo_children():
            widget.destroy()

        total_pages = len(self.books[self.current_book])
        columns = 10  # Fixed number of columns
        rows = math.ceil(total_pages / columns)

        # Calculate button width based on the page viewer width
        button_width = self.page_viewer.winfo_width() // (columns * 10)  # Adjust the divisor as needed

        for i in range(rows):
            for j in range(columns):
                page_num = i * columns + j
                if page_num < total_pages:
                    btn = tk.Button(self.page_matrix_frame, text=str(page_num + 1), 
                                    width=button_width, height=1,
                                    command=lambda p=page_num: self.show_page(p))
                    btn.grid(row=i, column=j, padx=1, pady=1, sticky='nsew')

        # Configure grid to expand buttons
        for i in range(columns):
            self.page_matrix_frame.columnconfigure(i, weight=1)

    def show_page(self, page_num):
        """Display the selected page in the page viewer."""
        self.current_page = page_num
        self.page_viewer.delete('1.0', tk.END)
        self.page_viewer.insert(tk.END, self.books[self.current_book][self.current_page])

    def copy_page(self):
        """Copy the current page content to clipboard."""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.page_viewer.get('1.0', tk.END))
        messagebox.showinfo("Copied", "Current page content copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookProcessorGUI(root)
    root.mainloop()