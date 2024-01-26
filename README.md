<h1>iogram plugin for easier telegram bot development.</h1>

<p>It implemets the class <b>Menu</b>, which is a message, that can be changed in time. Also, this class detects the high activity, and bans user if it is continuous.</p>
<p>The plugin features:</p>
<ul>
  <li>Message menu - a class, that implements a menue in the chat, that can change in time, and disappear if there is no usage of it</li>
  <li>User menu management - every user has customizable menues.</li>
  <li>Button - basic button with a callback function, that takes "user" as an argument</li>
  <li>InputButton - button, that can handle user inputs. Photo or text for this moment.</li>
  <li>TelePhoto - The class, that allows to save dynamic memory, by implementing a reference to image, instead of opening it or keeping in memory the copies of it</li>
  <li>User ban - if user acts really fast, the module will notice that and add him to ban list</li>
</ul>

<p>The plugin requires a <b>bot_token.txt</b>, whic acts as a configurational file. There, sould be inputted a token. After the first launch, the bot creates a database, with:</p>
<ul>
  <li>user_data - a table, for storing the user ids, personal data and a json of user data, collected during the execution.</li>
  <li>banned_users - a table, for storing the banned user ids</li>
</ul>
