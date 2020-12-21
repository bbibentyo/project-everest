#Project Everest
Web application used to host remote sensor data transmitted via internet 
and visualize sensor data.

## Running the program
The application is packaged into a docker image which can be executed using `docker` commands.
If you don't have docker and docker-compose installed, please proceed and install both. 
You can follow official docker documentation. 

If you are using **Windows** follow these instructions to install
[docker engine](https://docs.docker.com/docker-for-windows/install/) and
[docker compose](https://docs.docker.com/compose/install/).

Mac users, follow the instructions for Mac, to install
[docker engine](https://docs.docker.com/docker-for-mac/install/) and 
[docker-compose](https://docs.docker.com/compose/install/)

For Linux users, select the [instructions](https://docs.docker.com/engine/install/) 
appropriate for to your Linux distribution.

_after installing docker, docker compose and testing that it's working, proceed to running the application_

From terminal/command line, switch to the directory where 
you checked out the code `cd path/to/directory`. 
Once in the directory execute `docker-compose up` this should pull latest _python 3.8.6_ image, 
install all the dependencies and start the application.

## Flushing initial data in database
The application is storing its data in a SQLite database. 
There is some initial data that I am leaving in the database but is not required.
You can flush this data once docker is up and running. 
Execute the following command from the same directory as docker-compose.yml file which you checked out using git
`docker-compose run web python manage.py flush --no-input`

## Creating super user
The application is now ready to answer HTTP requests and test its functionalities. 
Before proceeding, we need to create a super user who will manage other users.
Execute the following command from the same directory as docker-compose.yml file which you checked out using git
and follow the prompt to provide your *username, email and password*. Please note that Django checks your password 
against commonly used passwords, and will refuse any commonly used passwords.

`docker-compose run web python manage.py createsuperuser`

If the user account creation works successfully, you should be able to navigate 
to the [admin page](http://localhost:8000/admin/) which will redirect you to the login page.
Enter the credentials you provided when creating superuser.

### Creating token for HTTP authentication
Now we need to create a service account (user) 
which we will use to generate random data from random data generator script.
In the browser, navigate to [user management](http://localhost:8000/admin/auth/user/) 
page and click on `add user`; enter the *username and password* of the service account and click on **save**.
You don't need to fill the information in the next page, unless you know what you are doing.
Above all, remember to give the application the least privilege necessary.

After creating the service account, create an authentication token by going to 
[token management](http://localhost:8000/admin/authtoken/tokenproxy/) page and clicking `add token`
in the user _dropdown_, select the newly created service account and click on **save**.
Copy the token displayed in key column and proceed to the next step.

> Do not use the super user to generate the token. It has elevated privileges that are not needed and could jeopardize the app

## Creating random data for testing/visualization
We can add random data to the web application by running the random data generator script.
Ensure that docker is running, and you are in the correct directory.
Execute the following command by replacing _{TOKEN}_ with the **token/key** you generated in the previous step.

`docker-compose run web python scripts/random_data_generator.py {TOKEN}`

Navigate to [home](http://localhost:8000/home/) page and checkout the time series graph of the random data.

## TODO
* Switch from HTTP to HTTPS with `self-signed certificate`, this has to be coordinated with the zephyr board code base.
* Give users the ability to select date range on home page
* Change random data generator script to use the same distance between two nodes