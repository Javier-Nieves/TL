# Trilingua
#### Video Demo:  https://youtu.be/O4jEjIU36aY
## Description:
Trilingua is a Flask web application which can be used to get translations of a word to two different languages at the same time. Hence it could be used as a three languages dictionary, teaching platform or an instrument for testing one’s languages skills.
App consists of 6 routes and 5 html pages: 
- Login 
- Register  
- Index 
- Trilingua 
- Test

Each html file extends the *layout.html* template with the help of Jinja2 to avoid repetitions.
Trilingua uses SQLite3 database to work. Users.db file contains *Users* table with all registered users names and password hashes, *Words* table with each user’s history of translations and several tables of bilingual dictionaries. These tables include not just *word* and *translation* columns, but also *type* column, which is used in **Test** route.

## Register route
This simple page consists of three basic fields for Username, Password and its Confirmation. All forms shouldn't be empty and there are rules for password complexity, it's checked at frontend. Backend logic is used to check if password is equal to confirmation and to hash password in that case. In other case warning message appears. It's implemented using JS className change. Here as in all of the app's code CSS is separated in styles.css and no inline styling is used. 
In case of successfull registration user is redirected to *login* page and Success allert is displayed there. Sessions module is used to transfer data between routes.

## Login route
This page is similar to register in the sence of checks - frontend for input fields and backend for database username/hash match. JS allert will also appear in case of a mismatch. On login user is redirected to the Index page (logout link is always present in any page alongside the username).

## Index route
Here user should choose three different languages to work with. At this moment only 4 language options are available, but it's easily scalable. If user chooses one language several times he wouldn't be able to proceed further. Instead the page will be reloaded and it's heading will be changed to "different languages". After choosing three different languages to work with user will choose to go to **Trilingua** dictionary or straight to **Test** page. Chosen languages will be remembered in *Sessions* variables.

## Trilingua 
This page is a three-language dictionary with a personal history table. User can input a word to any of three text fields on the page. As well as the word exists in database dictionary user will see 2 translations to languages, chosen on Index page. In case of an empty input or when word isn't in the DB JS will show an according allert message. Translated words will appear at the top of the personal history table, which can be cleared by *Clear History* button or used in **Test**.

## Test
Here user can test his language skills or learn new words. There are 3 methods to practice:
- Random
- Personal
- Category

User can choose how many words at once he will receive on the page and which method will he use. In any method user will see words from left column and should recall two translations for every word. Correct translations appear on hover, focus of when *Reveal* button is pushed. Second push will hide the translations back. This is achived with *classList.Toggle* method in JS. Also *refresh* button will give user another set of words in chosen method.
So, **Random** method will provide user with random words from first language, **Personal** method will be useful to train specific words from user's personal history. When **Category** method is chosen Category selector becomes active and user can now choose words by groups (allert will appear if Category isn't chosen).
