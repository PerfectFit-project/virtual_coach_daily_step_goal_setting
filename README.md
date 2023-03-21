# rasa_example_project
Example for setting up a conversational agent based on Rasa Open Source on a Google Compute Engine instance. The conversational agent in this example interacts with people in 5 conversational sessions.

Based on this Github repository (https://github.com/AmirStudy/Rasa_Deployment) as well as the work by Tom Jacobs (https://github.com/TomJ-EU/rasa/tree/dev).


## Components

This virtual coach consists of a backend based on Rasa Open Source (backend), a custom action server (actions), a frontend (frontend), a database (db), and an SQLTrackerStore.


## Setup on Google Compute Engine

To run this project on a Google Compute Engine, I followed these steps:

   - Create a Google Compute Engine instance:
	  - Use Ubuntu 20.04.
	  - Make sure that the location is in Europe.
	  - Enable http and https traffic.
	  - Choose a small instance for the start, since you have to pay more for larger instances. I started with an e2-medium machine type and 100GB for the boot disk.
	  - The first 3 months you have some free credit.
      - Follow the instructions from [here](https://github.com/AmirStudy/Rasa_Deployment) in the sense that you “allow full access to all cloud APIs” on the Google Compute Engine instance. This is shown in this video: https://www.youtube.com/watch?v=qOHszxJsuGs&ab_channel=JiteshGaikwad. Also see this screenshot:
   
      <img src = "Readme_images/allow_full_access.PNG" width = "500" title="Allowing full access to all cloud APIs.">
   
   - Open port 5005 for tcp on the Compute Engine instance:
	
   <img src = "Readme_images/firewall_rule.PNG" width = "500" title="Creating a firewall rule.">
	
   <img src = "Readme_images/firewall_rule_0.PNG" width = "250" title="Creating a firewall rule 0.">
	
   <img src = "Readme_images/firewall_rule_1.PNG" width = "500" title="Creating a firewall rule 1.">
	
   <img src = "Readme_images/firewall_rule_2.PNG" width = "250" title="Creating a firewall rule 2.">
   
   <img src = "Readme_images/firewall_rule_3.PNG" width = "250" title="Creating a firewall rule 3.">
	
   - Do the same with port 3000.
   - Follow the instructions from [here](https://github.com/AmirStudy/Rasa_Deployment) for installing Docker on the Google Compute Engine instance. You can do this via the command line that opens after you click on "SSH":
   
   <img src = "Readme_images/ssh.PNG" width = "250" title="Connect via SSH.">
	
   - Install docker-compose on the instance:
	  - I followed the steps described [here](https://levelup.gitconnected.com/the-easiest-docker-docker-compose-setup-on-compute-engine-ec171c09a29a):
	     - `curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
	     - `chmod +x /usr/local/bin/docker-compose`
	     - You might need to add `sudo` in front of the commands to make them work.
   - I suggest getting a static IP address for your Google Compute Engine instance:
      - Follow the instructions here: https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address.
	  - You have to pay for every month, but it is rather cheap.
   - Make sure you turn off your instance whenever you do not need it, as you are charged for the time that it is up.
   - Create your own branch/fork from this project.
   - In your branch, set the IP address of your Google Compute Engine instance in the function `send(message)` in the file frontend/static/js/script.js: `url: "http://<your_instance_IP>:5005/webhooks/rest/webhook"`. This is why it helps to have a static IP address.
      - When you run the project locally, use `url: "http://localhost:5005/webhooks/rest/webhook"`.
   - Clone your project from Github on the Google Compute Engine instance.
   - Navigate to your project folder on the Compute Engine instance and start your project with `docker-compose up`.
   - Check if all your containers are running on your Google Compute Engine instance via `docker container ls`.
   - You can access the frontend from your browser via `http://<your_instance_IP>:3000/?userid=<some_user_id>&n=1`. `n` determines which session is started (1-5). Earlier sessions need to be completed by a user to be able to access later ones.
   - Open the chat here:
   
      <img src = "Readme_images/open_chat.PNG" width = "250" title="Open chat.">
   
      - The button can be very small on your phone.
   
   - The chat should look something like this:
   
   <img src = "Readme_images/chat.PNG" width = "250" title="Chat.">
   
   - Right now I have set the code in frontend/static/js/script.js such that the chat is always opened in fullscreen. See this code:
     
	 ```js
	 if ($('.widget').width() == 350) {
		$('.widget').css("width" , "98%");
		$('.widget').css("height" , "100%");
	 } else {
		$('.widget').css("width" , "350px");
		$('.widget').css("height" , "100%");
	 }
	 ```
      - The code by Tom Jacobs (https://github.com/TomJ-EU/rasa/tree/dev) instead adds a "fullscreen"-option to the drop-down used in the code by Jitesh Gaikwad (https://github.com/AmirStudy/Rasa_Deployment). For example, like this in script.js:
   
		```js
		//fullscreen function to toggle fullscreen.
		$("#fullscreen").click(function () {
		   if ($('.widget').width() == 350) {
		      $('.widget').css("width" , "98%");
			  $('.widget').css("height" , "100%");
		   } else {
			  $('.widget').css("width" , "350px");
			  $('.widget').css("height" , "500px");
		   }
		});
		```
      - But then you also need to make sure to add the drop-down to the file index.html:
	  
	    ```html
		<div class="chat_header">

           <!--Add the name of the bot here -->
		   <span class="chat_header_title">Virtual Coach Mel</span>
		   <span class="dropdown-trigger" href='#' data-target='dropdown1'>
			  <i class="material-icons">
				 more_vert
			  </i>
		   </span>
        </div>
		```
		
		```html
		<!-- Dropdown menu-->
        <ul id='dropdown1' class='dropdown-content'>
           <li><a href="#" id="fullscreen">Fullscreen</a></li>
        </ul>
		```
		
	  - And further adapt script.js by adding code to `(document).ready(function ()`:
	  
	    ```js
		//drop down menu
	    $('.dropdown-trigger').dropdown();
	    ```

This project uses an SQLTrackerStore (https://rasa.com/docs/rasa/tracker-stores/) to store the conversation history in a database:
   - A nice way to see the contents of this database is using the program DBeaver.
      - First also open port 5432 on your Google Compute Engine instance for tcp. There is no need to restart the instance after opening the port.
      - To configure DBeaver, add a new database connection:
   
      <img src = "Readme_images/dbeaver_1.PNG" width = "250" title="DBeaver 1.">
   
      - Select a "PostgresSQL" connection.
      - Enter your instance's IP address as the "Host", keep the "Port" set to 5432, enter the username and password used in docker-compose.yml, and set the "Database" to "rasa".
      - After connecting, you can inspect the database content by clicking on the "events" table:
   
      <img src = "Readme_images/dbeaver_2.PNG" width = "500" title="DBeaver 2.">
   
      - After clicking on "Data," you can see the table content. The "sender_id" is the "<some_user_id>" you used when accessing your frontend:
   
      <img src = "Readme_images/dbeaver_3.PNG" width = "500" title="DBeaver 3.">
   
      - To refresh the view, you can click on File > Refresh in DBeaver.
	  - You can also export the data in the database:
	  
	  <img src = "Readme_images/dbeaver_4.PNG" width = "500" title="DBeaver 4.">

   - The database is persistent because of the "volumes" we specified in docker-compose.yml for postgres. Read more about this here: https://medium.com/codex/how-to-persist-and-backup-data-of-a-postgresql-docker-container-9fe269ff4334.
      - So you can run `docker-compose down --volumes` and `docker-compose up --build` and the database content is still there. Check for yourself using DBeaver.


The project further uses an mysql database to store specific data from the conversations:
   - The database is also persistent. The folder "data_mysql" is used for this, as set up in docker-compose.yml.
   - To inspect the database content content with DBeaver, first open port 3306 on your instance for tcp. Again, there is no need to restart your instance after opening this port.
   - When setting up the connection, use "db" for "Database", "root" for "Username", and the password specified in docker-compose.yml. Keep "Port" to 3306. The "Server Host" is the IP address of your instance.
      - You might have to set "allowPublicKeyRetrieval" to "true" in "Driver properties." 


Some errors I got during the setup:
   - "Couldn't connect to Docker daemon at http+docker://localhost - is it running? If it's at a non-standard location, specify the URL with the DOCKER_HOST environment variable“ when running `docker-compose up –-build`.
      - I followed the steps suggested here: https://forums.docker.com/t/couldnt-connect-to-docker-daemon-at-http-docker-localhost-is-it-running/87257/2.
	  - These 2 steps fixed the issue for me:
	     
		 <img src = "Readme_images/error_build.PNG" width = "500" title="docker-compose up --build error.">
		 
		 - Run `sudo docker-compose up –-build`. 
		 
   - When running the project locally on Windows, I got an error for the SQLTrackerStore when running `docker-compose up –-build`. Just removing the information on `volumes` in docker-compose.yml helped. This removes the persistence though.
	
		 
## Frontend Styling

Check the file frontend/static/css/style.css to adapt the styling of the frontend:
   - .chats defines the chat area within the window in fullscreen mode. I tuned the height and width of this.
   - .chat_header_title defines the chat header title. I set the color to #f7f7f7 so that the title is not visible in fullscreen mode. Change the margin-left to align the title to the center. Right now I have fully removed the title though. If you want to add the title again, your file frontend/index.html should contain `chat_header_title`:
   
     ```html
	 <!--chatbot widget -->
	 <div class="widget">
		 <div class="chat_header">

		    <!--Add the name of the bot here -->
		    <span class="chat_header_title">Your Bot Name</span>
		   
		 </div>
		   
	     <!--Chatbot contents goes here -->
	     <div class="chats" id="chats">
		    <div class="clearfix"></div>
	     </div>

	     <!--keypad for user to type the message -->
	     <div class="keypad">
		    <textarea id="userInput" placeholder="Type a message..." class="usrInput"></textarea>
		    <div id="sendButton"><i class="fa fa-paper-plane" aria-hidden="true"></i></div>
	     </div>

	 </div>
     ```
	
   - If you want to change the way that buttons are displayed, adapt `.menu` and `.menuChips` in the file style.css.
      - For example, you may want to display the buttons like this:
	   
	     <img src = "Readme_images/buttons_wrapped.PNG" width = "500" title="Wrapped buttons.">
		  
	  - This can be done with this code:

	    ```css
	    .menu {
			padding: 5px;
			display: flex;
			flex-wrap: wrap;
		}

		.menuChips {
			display: inline-block;
			background: #2c53af;
			color: #fff;
			padding: 5px;
			margin-bottom: 5px;
			cursor: pointer;
			border-radius: 15px;
			font-size: 14px;
		}
	    ```

      - Important is that `display: flex` and `flex-wrap: wrap` in `.menu`.
	  - To further remove the background of the buttons and add a shadow to the individual buttons instead, set `box-shadow: 2px 5px 5px 1px #dbdade` for `.menuChips` and use this code for `.suggestions` in the file style.css:
	  
	    ```css
		.suggestions {
			padding: 5px;
			width: 80%;
			border-radius: 10px;
			background: #f7f7f7;
		}
		```

	  - Then buttons are displayed like this:
	  
	     <img src = "Readme_images/buttons_wrapped_noback.PNG" width = "500" title="Wrapped buttons no background.">
		
	  - See [this post](https://stackoverflow.com/questions/73533611/how-to-put-two-chips-divs-next-to-each-other) for some other ideas for displaying buttons next to each other.
	  - Note that by default, buttons are displayed like this:
		
	     <img src = "Readme_images/buttons_below.PNG" width = "500" title="Buttons below each other.">
		
	  - The corresponding code in the file style.css looks like this:
		
		```css
		.menu {
			padding: 5px;
		}

		.menuChips {
			display: block;
			background: #2c53af;
			color: #fff;
			text-align: center;
			padding: 5px;
			margin-bottom: 5px;
			cursor: pointer;
			border-radius: 15px;
			font-size: 14px;
			word-wrap: break-word;
		}
		```

The files in frontend/static/img are used to display the chatbot and the user inside the chat, as well as to display the chatbot when the chat is still closed at the start.

You can use "\n" in your utterances in domain.yml to display a single utterance as two (or more) separate messages. The resulting messages are not treated as separate messages when it comes to displaying the typing symbol though.


## Other Notes
- The frontend is not fully cleaned up yet (i.e., still contains quite some components that are not used by this project).
- The repository by Jitesh Gaikwad (https://github.com/AmirStudy/Rasa_Deployment) also contains code for displaying charts, drop-downs, and images in frontend/static/js/script.js (see the function `setBotResponse` for displaying responses from the rasa bot). I have removed this code in this example project, but if you need to send such kinds of messages, take a look.
- `"--debug"` in backend/Dockerfile prints a lot of debugging statements (e.g., for the action prediction). This is handy while you are still developing your agent, but can be removed.
- The Developer tools in Google Chrome show the logs from script.js (i.e., the result of `console.log()`)if you access the frontend via Google Chrome.

## License

Copyright (C) 2023 Delft University of Technology.

Licensed under the Apache License, version 2.0. See LICENSE for details.
