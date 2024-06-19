# Directory structuring and writing the book
To be consistent and ease of using the data we will try to develop a scalable directory structuring. If any breaking change is introduced in the data, it should be reflected on all the data that is already saved. Moreover, we use [HTML](https://www.w3schools.com/html) to create the content. 

## Before writing a book
To start writing a book, a new directory/folder in the root should be created using following name format. 
**BOOK_NAME_WITHOUT_WHITESPACES_LANGUAGE_DATE_STARTED** e.g. A book named **Raheequl Makhtoom** in Arabic language is started on **04.02.2024** would be: **Raheeul_Makhtoom_ar_04-02-2024**. Use `-` in the date and for language codes visit: https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes. 

Inside this directory there should be a [JSON](https://en.wikipedia.org/wiki/JSON) file named **info.json** which will include all relevant information about that book (Normally available on the first page of the book). e.g. **info.json** file for **Raheeul_Makhtoom_ar_04-02-2024** book will look something like this:
**Raheeul_Makhtoom_ar_04-02-2024/info.json**

The writer should upload the image of each page with minimum 200DPI. A new directory per page is created as follow:
1. **Raheeul_Makhtoom_ar_04-02-2024/1/page.png**
2. **Raheeul_Makhtoom_ar_04-02-2024/1/page.html**
3. **Raheeul_Makhtoom_ar_04-02-2024/1/ANY_OTHER_RESOURCE**
The cover page, last page or any other pages outside of the content are uploaded using following directory structure.
1. **Raheeul_Makhtoom_ar_04-02-2024/cover/page.png**
2. **Raheeul_Makhtoom_ar_04-02-2024/cover/page.html**
3. **Raheeul_Makhtoom_ar_04-02-2024/SPECIAL_PAGE/page.png**
4. **Raheeul_Makhtoom_ar_04-02-2024/SPECIAL_PAGE/page.html**

If you think that there is any other important page to be uploaded. Please consult with the team.

## Standard to write the book
We decided to follow a standard class names to distinguish between various components of our books. It will help us to style our books using simple **CSS**. This standard should be maintained and updated according to the needs.

We will use `span` elements to avoid any predefined styling and use the class names to identify the content what has been written over there. In future, when we will work on showing this content. We can transform this content in whatever way we want.

Following are some class names which are used inside the **span** elements.
1. **chapter**: indicates the name of the chapter
2. **h1…h6**: indicates that the H1…H6 headings (their links will be generated, so make sure that they are the actual headings)
3. **row**: indicates the row of the page (we are keeping this low level detail because we want to build a tool for cross-referencing to the rows of a book.
4. **ADDITIONAL_CLASS_NAME**: Feel free to update this list, this should be maintained and revisited to make sure that the dependent tools do not break.

## Definition of Done for writing one page of a book
1. The design of the page should be consistent to the book. Because, in future in our tool we will provide the functionality to reference to the line numbers of the books. So, we need to make sure that we are even taking care of the line breaks.
2. The writer should use the proper headings which will help us to keep the record and build the table of content programmatically. 
3. The writer should upload the scanned image of the page with minimum 200DPI.
