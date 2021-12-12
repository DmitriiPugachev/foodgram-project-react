![example workflow](https://github.com/DmitriiPugachev/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

### Description:
API and frontend for Foodgram.
#### You can:
  * run the full project in docker containers;
  * get or create users;
  * get, create, change and delete recipes;
  * add a recipe to your favorites and get all your favorited recipes;
  * add a recipe to your shopping cart and get all the recipes from your cart;
  * download shopping list;
  * follow any author and get all the recipes of the following author;
  * do all that stuff at the website.
#### Techs:
  * requests==2.26.0
  * django==2.2.6
  * djangorestframework==3.11.0
  * drf-extra-fields==3.2.1
  * djoser==2.1.0
  * pillow==8.2.0
  * python-dotenv==0.13.0
  * django-filter==21.1
  * asgiref==3.2.10
  * gunicorn==20.0.4
  * psycopg2-binary==2.8.5
  * pytz==2020.1
  * sqlparse==0.3.1
### How to run the project local:
Clone the repo and go to the backend directory:
```bash
git clone https://github.com/DmitriiPugachev/foodgram-project-react
```
```bash
cd foodgram-project-react/backend
```
Create ```.env``` file in the root project directory with variables like in ```.env.example``` file.

Install Docker. [This gide](https://docs.docker.com/engine/install/ubuntu/) help you.

Go to infrastructure directory:
```bash
cd foodgram-project-react/infra
```
Build an image and run all the containers:
```bash
docker-compose up -d --build
```
Go to the web container:
```bash
docker exec -it infra_web_1 bash
```
Apply migrations:
```bash
python manage.py migrate --noinput
```
Create a superuser:
```bash
python manage.py createsuperuser
```
Copy ingredient data to the DB:
```bash
python manage.py load_data
```
### How to run project global:
Fork [this repo](https://github.com/DmitriiPugachev/foodgram-project-react) to your
GitHub account.

Create your DockerHub account.

Create your remote virtual machine.

On GitHub in repo Settings add secret variables for workflow like 
in ```.env.example``` file.

Run workflow in GitHub Actions.

Connect to your remote virtual machine:
```bash
ssh <username>@<public_ip>
```
Install Docker:
```bash
sudo apt install docker.io
```
Install [docker-compose](https://docs.docker.com/compose/install/).

Copy ```docker-compose.yaml```from local machine to remote virtual machine:
```bash
scp foodgram-project-react/infra/docker-compose.yaml <username>@<public_ip>:/home/<username>/
```
Copy ```nginx.conf``` from local machine to remote virtual machine:
```bash
scp foodgram-project-react/infra/nginx.conf <username>@<public_ip>:/home/<username>/
```
Go to the running web container on your remote virtual machine:
```bash
sudo docker exec -it <CONTAINER_ID> bash
```
Apply migrations, create superuser and load ingredients data in the database like 
in ```How to run the project local```.

Before every command don't forget to add:
```bash
sudo
```
### Links
[redoc](http://dmitrii-pugachev.tk/redoc/)

[admin](http://dmitrii-pugachev.tk/admin/)

[Website](http://dmitrii-pugachev.tk/)

[API](http://dmitrii-pugachev.tk/api/)

### Author
Dmitrii Pugachev
