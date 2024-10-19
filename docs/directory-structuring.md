# Directory structuring and writing the book
To be consistent and ease of using the data we will try to develop a scalable directory structuring. If any breaking change is introduced in the data, it should be reflected on all the data that is already saved. Moreover, we use [CommonMark Markdown](https://commonmark.org/) to create the content. 

## Getting started with writing a book
You should understand the basic concepts of [Jupyter book](https://jupyterbook.org/en/stable/) and how you can write the book in Jupyter book. 

Following are some basic steps to get started with writing a book in Jupyter book.

### Create a new book
Copy the `template_book` directory and rename it to the name of the book. You can use the following command to create a new book.

``` bash
cp books/template_book books/BOOK_NAME_WITHOUT_WHITESPACES_LANGUAGE_DATE_STARTED
```
Or you can simply copy the `template_book` directory and rename it to the name of the book. The template book is a simple book with two pages, you can modify it according to your needs. For more information, visit the [Jupyter book documentation](https://jupyterbook.org/en/stable/basics/create.html).

**BOOK_NAME_WITHOUT_WHITESPACES_LANGUAGE_DATE_STARTED** e.g. A book named **Raheequl Makhtoom** in Arabic language is started on **04.02.2024** would be: **Raheeul_Makhtoom_ar_04-02-2024**. Use `-` in the date and for language codes visit: https://www.w3schools.com/tags/ref_language_codes.asp. 

### Write the book
You can write the book in the markdown files. The markdown files should be saved in the `content` directory of the book. You can use the markdown files to write the content of the book. For more information, visit the [Jupyter book documentation](https://jupyterbook.org/en/stable/basics/organize.html).

A new `.md` file is created for each chapter of the book. The name of the file should be the number of the chapter e.g. `chap_1`. 

If any chapter has sub-chapters, the sub-chapters should be saved in the same file. The sub-chapters should be saved in the same file with the name of the sub-chapter e.g. `chap_1_1`.

If any book has the graphics, the graphics should be saved in the `images` directory of the book. The graphics should be saved in the `images` directory of the book with comprehensive and self explanatory names.
