# Getting Started

user and password = root  
  
### Python 3.9  
Install the requirements in your python env "pip install -r requirements.txt"  
  
### Start the server  
For the start the server you need to install the requirements and use the command "python manage.py runserver"  
  
### API  
* All calls needs basic auth: with user and password root.  
* You can use postman to connect and get / update / create / delete the data or view the availability  
  
> Note: If you want use the implemented functional views first connect using django admin "/admin/" and then go to "/api/" and feel free  
  
### Swagger  
For show more info about the API is implemented a swagger or redoc as your preference.  
  
* /swagger/  
* /swagger.json/ or /swagger.yaml/  
* /redoc/  
  
### Run test:  
  > python manage.py test