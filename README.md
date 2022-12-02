# BotsUpV3

This is a project I made to send automatic bulk messages on whatsapp for marketing purposes.
I made the entire UI with TKinter (I am a bad designer).
In order for the software to start, you need to login with your creds which are stored in an SQL database.

(For TechSoc, Username : TechSoc ; Password : 1234)

After logging in, you need to select a txt file containing the message you want to send.
After that you need to select the excel sheet containing the phone numbers of people you want to send the message to.
After that you can select attachments to send, if you want.
Clicking the send button will take you to whatsApp web portal where you need to scan your with your smartphone.
After that BotsUp will automatically send the message and attachment to all the phone numbers in the excel sheet.

You might notice some bugs due to change to Win11 (i guess)

Download standalone exe : https://drive.google.com/file/d/1him3YZ--638YllOlFM0VqwSYAunelcEM/view?usp=sharing
NOTE: After extracting the above file, please change the config.json file to the one in the repository, as the old database is closed.
