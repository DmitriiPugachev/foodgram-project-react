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
cd foodgram_project_react/backend
```
Create ```.env``` file in the root project directory with variables like in ```.env.example``` file.

Install Docker. [This gide](https://docs.docker.com/engine/install/ubuntu/) help you.

Go to infrastructure directory:
```bash
cd foodgram_project_react/infra
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

### Links
[redoc](http://localhost/api/docs/)

[admin](http://localhost/admin/)

[Website](http://localhost/)

[API](http://localhost/api/)

### Author
Dmitrii Pugachev
