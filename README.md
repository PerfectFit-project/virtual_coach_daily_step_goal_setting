# Using Reinforcement Learning to Personalize Daily Step Goals for a Collaborative Dialogue with a Virtual Coach

This github repository contains the code for the chatbot Steph that is created for the thesis project: Using Reinforcement Learning to Personalize Daily Step Goals for a Collaborative Dialogue with a Virtual Coach. Steph was used to gather data dring an observational study. Please refer to our [OSF pre-registration](https://doi.org/10.17605/OSF.IO/6JQPK) for more details on our observational study. For our code for the reinforcement learning model based on the collected data during the conversation sessions, please refer to our [published data and code](https://doi.org/10.4121/6f8e6750-7494-4226-b6f9-299a9edbb077).

## Dialogue flow

During the observational study, participants were aksed to interact with our chatbot Steph for at most five consequetive days. The figure below visualizes the flow of the dialogue with Steph during the different days of the observational study.

<img src = "Readme_images/High-level dialogue flow.png" title="Dialogue flow.">

## System architecture

### Frontend

The frontend is a html-page. Accessing the page via localhost requires to provide a user id and session number in the URL. For example, `localhost/?userid=42&n=1` opens the session 1 for the user with id 42.

Files:
- static/css/style.css contains the stylesheet for the html-page.
- static/js/script.js contains the functions for the interaction between the user and the chatbot and for the communication between front- and backend.
- index.html contains the code for the frontend html-page.
- server.js contains the code to start the server and initialize the correct session.

### Backend

The backend is a combination of files that split the logic of what the chatbot should say, what internal actions should be taken and which variables to keep during the session.

Files:
- data/rules.yml contains the rules of the chatbot, stating what to do when something is triggered by the user or chatbot itself.
- models contains the trained models for the chatbot to use with all the rules, actions and other information.
- domain.yml contains the actual phrases of the chatbot and the variables that need to be tracked during the conversation.

### Actions

The actions is a file containing all the logic in relation to database access and calculations needed during the conversation which can be used by the backend files.

Files:
- actions.py containing all the logic in relation to database access and calculations needed during the conversation.

### Database (db)

The database is a Mysql database storing all the relevant information from the conversation.
Meanwhile, a Postgres database stores all the session details, for example, every utterance of the chatbot and user.

## Running Steph locally

To run the chatbot locally:
1. Install Docker (in case you have not), which you can do by following the instructions [here](https://docs.docker.com/get-docker/).
2. Install Docker-compose by running:
	- `sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose` 
	- `sudo chmod +x /usr/local/bin/docker-compose`
3. Create a fork and clone this project.
4. Navigate to the root folder of this project (where this README is located).
5. Run `docker-compose up --build` to build docker and bootup the server for the chatbot.
6. Open `localhost/?userid=<some_user_id>&n=<sessionnumber>` and replace \<some_user_id\> and \<sessionnumber\> with the user id and session number respectively.


## Setup on Google Compute Engine

To run this project on a Google Compute Engine, follow these steps:

   - Create a Google Compute Engine instance:
	  	- Use Ubuntu 20.04.
	  	- Enable http and https traffic.
      	- Follow the instructions from [here](https://github.com/AmirStudy/Rasa_Deployment) in the sense that you “allow full access to all cloud APIs” on the Google Compute Engine instance. This is shown in this video: https://www.youtube.com/watch?v=qOHszxJsuGs&ab_channel=JiteshGaikwad. Also see this screenshot:
   
    	<img src = "Readme_images/allow_full_access.PNG" width = "500" title="Allowing full access to all cloud APIs.">
   
   - Open port 5005 for tcp on the Compute Engine instance:
	
   <img src = "Readme_images/firewall_rule.PNG" width = "500" title="Creating a firewall rule.">
	
   <img src = "Readme_images/firewall_rule_0.PNG" width = "250" title="Creating a firewall rule 0.">
	
   <img src = "Readme_images/firewall_rule_1.PNG" width = "500" title="Creating a firewall rule 1.">
	
   <img src = "Readme_images/firewall_rule_2.PNG" width = "250" title="Creating a firewall rule 2.">
   
   <img src = "Readme_images/firewall_rule_3.PNG" width = "250" title="Creating a firewall rule 3.">
	
   - Follow the instructions from [here](https://github.com/AmirStudy/Rasa_Deployment) for installing Docker on the Google Compute Engine instance. You can do this via the command line that opens after you click on "SSH":
   
   <img src = "Readme_images/ssh.PNG" width = "250" title="Connect via SSH.">
	
   - Install docker-compose on the instance:
		- `sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
		- `sudo chmod +x /usr/local/bin/docker-compose`
   - Create your own branch/fork from this project.
   - Clone your project from Github on the Google Compute Engine instance.
   - Navigate to your project folder on the Compute Engine instance and start your project with `docker-compose up`.
   - Check if all your containers are running on your Google Compute Engine instance via `docker container ls`.
   - You can access the frontend from your browser via `http://<your_instance_IP>/?userid=<some_user_id>&n=1`. `n` determines which session is started (1-5). Earlier sessions need to be completed by a user to be able to access later ones.
   - Open the chat here:
   
      <img src = "Readme_images/open_chat.PNG" width = "250" title="Open chat.">
   
      - The button can be very small on your phone.

## Accessing the database

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

   - The database is persistent because of the "volumes" we specified in docker-compose.yml for postgres. Read more about this here: https://medium.com/codex/how-to-persist-and-backup-data-of-a-postgresql-docker-container-9fe269ff4334.
      - So you can run `docker-compose down --volumes` and `docker-compose up --build` and the database content is still there.
	  - To delete the database content, just remove the "data"-folder.


The project further uses an mysql database to store specific data from the conversations:
   - The database is also persistent. The folder "data_mysql" is used for this, as set up in docker-compose.yml.
   - To inspect the database content content with DBeaver, first open port 3306 on your instance for tcp. Again, there is no need to restart your instance after opening this port.
   - When setting up the connection, use "db" for "Database", "root" for "Username", and the password specified in docker-compose.yml. Keep "Port" to 3306. The "Server Host" is the IP address of your instance.
      - You might have to set "allowPublicKeyRetrieval" to "true" in "Driver properties." 
   - To delete the database content, just delete the folder "data_mysql" on your Google Compute Engine instance.

## License

Copyright (C) 2023 Delft University of Technology.

Licensed under the Apache License, version 2.0. See LICENSE for details.
