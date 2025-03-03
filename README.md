# islamopedia-books
This is a helper repository of [Islamopedia](https://github.com/segullshairbutt/islamopedia/) to keep the backup of the books in text format. This will allow us to keep the books in a version control system and allow us to collaborate on the books easily.

## Static pages of the books
- [Demo Book](./books/template_book/_build/html/index.html)

## How to start writing a new book
1. Clone the repository
2. [Setup the development environment](./docs/local-setup.md)
3. Follow the [directory structuring](./docs/directory-structuring.md) to create a new book

## Definition of Done
1. The design of the page should be consistent to the book. Because, in future in our tool we will provide the functionality to reference to the line numbers of the books. So, we need to make sure that we are even taking care of the line breaks.
2. The writer should use the proper headings which will help us to keep the record and build the table of content programmatically. 

## Contribution workflow
A new PR should be created against the work's small unit (as much as possible). It can be one page of the book, a book chapter, or a group of chapters. But the smaller the PR, the easier to review.

1. [Writing a book in Jupyter book](./docs/directory-structuring.md): 
    We use Juptyer book to write the books. This is a guide on how to write a book in Jupyter book.

2. A list of books which are on the track coming ahead
    1. Books of Fiqh
        1. Ahl-e-Sunah Fiqhs
            1. Fiqha Hanfi
            2. Fiqha Maliki
            3. Fiqha Shafie
            4. Fiqa Hambali 
        2. Ahl-e-Tasheeh Fiqh
            1. Fiqha Jafferia
    2. Biographies
        1. Ahl-e-Bait S.A
        2. Ummahat-ul-Momineen R.A
        3. Sahaba and Sahabiat R.A
        4. All popular Fiqhi Imams (Imam Abu Hanifa, Imam Malik, Imam Shafie, Imam Ahmad, Imam Jaffar) R
        5. All popular Ahl-e-Sunnah Imams (Writers of Sihah Sitah) R
        6. Khulafa-e-Rashideen (Hazrat Abu Bakar, Hazrat Umar, Hanzrat Usman and Hazrat Ali) R.A
        7. Prophet PBUH (The reason to keep it last on the list is that we already have a lot of content online, but for the above points we have almost nothing)
