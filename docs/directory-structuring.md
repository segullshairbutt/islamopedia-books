# Directory structuring and writing the book
To be consistent and ease of using the data we will try to develop a scalable directory structuring. If any breaking change is introduced in the data, it should be reflected on all the data that is already saved. 
Moreover, we use [markdown format](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github) to create the content of our pages. 

## Before writing a book
To start writing a book, a new directory/folder in the root should be created using following name format. 
**BOOK_NAME_WITHOUT_WHITESPACES_LANGUAGE_DATE_STARTED** e.g. A book named **Raheequl Makhtoom** in Arabic language is started on **04.02.2024** would be: **Raheeul_Makhtoom_ar_04-02-2024**. Use `-` in the date and for language codes visit: https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes. 

Inside this directory there should be a [JSON](https://en.wikipedia.org/wiki/JSON) file named `info.json` which will include all relevant information about that book (Normally available on the first page of the book). 

The writer should also upload the cover page, first page and last page of the book with minimum 300DPI. The directory structuring will be as follow:
1. **Raheeul_Makhtoom_ar_04-02-2024/first_page.png**
2. **Raheeul_Makhtoom_ar_04-02-2024/last_page.png**
2. **Raheeul_Makhtoom_ar_04-02-2024/cover_page.png**

If you think that there is any other important page to be uploaded. e.g. Disclaimer, Please consult with the team.

Each chapter will be segregated further with a separate directory/folder. e.g. full directory tree for Chapter 1 for the book one above will be: **Raheeul_Makhtoom_ar_04-02-2024/chapter_1/**

Now, create one `.md` file for each page. The name of the file will be the actual page number. e.g. full directory tree for Page 1 for Chapter 1 of the book mentioned above will be: **Raheeul_Makhtoom_ar_04-02-2024/chapter_1/01.md**. 

To upload the scanned image for each page use same directory structuring by just changing the extension of the file. e.g. Image for the file created above will be: **Raheeul_Makhtoom_ar_04-02-2024/chapter_1/01.png**

## Definition of Done for writing one page of a book
1. The design of the page should be consistent to the book. Because, in future in our tool we will provide the functionality to reference to the line numbers of the books. So, we need to make sure that we are even taking care of the line breaks. We can use `<br>` element for inline line break or 2 line breaks for that.
2. One should use the proper headings which will help us to keep the record and build the table of content programmatically. 
3. One should upload the scanned image of the page with minimum 300DPI.
