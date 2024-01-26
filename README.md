<h1>iogram plugin for easier telegram bot development.</h1>

<p>It implemets the class <b>Menu</b>, which is a message, that can be changed in time. Also, this class detects the high activity, and bans user if it is continuous.</p>
<p>The plugin features:</p>
<ul>
  <li>Message menu - a class, that implements a menue in the chat, that can change in time, and disappear if there is no usage of it</li>
  <li>User menu management - every user has customizable menues.</li>
  <li>Button - basic button with a callback function, that takes "user" as an argument</li>
  <li>InputButton - button, that can handle user inputs. Photo or text for this moment.</li>
  <li>TelePhoto - The class, that allows to save dynamic memory of a server, by implementing a reference to image, instead of opening it or keeping in memory the copies of it</li>
  <li>User ban - if user acts really fast, the module will notice that and add him to ban list</li>
</ul>

<p>The plugin requires a <b>bot_token.txt</b>, whic acts as a configurational file. There, sould be inputted a token. After the first launch, the bot creates a database, with:</p>
<ul>
  <li>user_data - a table, for storing the user ids, personal data and a json of user data, collected during the execution.</li>
  <li>banned_users - a table, for storing the banned user ids</li>
</ul>

<p>Also, this class have a signal mechanics implementation. This is when a particular event happens, the desired function is being executed. For now, the module has:</p>
<ul>
  <li>_on_user_created(user : User) -> None - a function, the value of which needs to be defined, called when a new user is added to dynamic memory.</li>
  <li>_on_user_data_saving(data : dict) -> None - a function, the value of which needs to be defined, called, when the user data is being stored. Should be assigned as a parser, that parses the user_data dictionary for storing the data (when, for example, the dictionary has Object, and those have their own parsers, not strings)</li>
  <li>_on_user_data_loading(data : str) -> dict - a function, the value of which needs to be defined, called, when the user data is being loaded. Should be assigned as a parser, that parses the user_data string for the data (when, for example, the dictionary has a string, that needs to be recreated as an object, and those have their own parsers) </li>
</ul>
