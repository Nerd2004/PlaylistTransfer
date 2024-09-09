A Simple Website to transfer your playlist from spotify to youtube account using Google Oauth Flask selenium for webscraper and AWS Lambda for deploying the scraper

Login Page:
![image](https://github.com/user-attachments/assets/509a8e5a-c981-4a3c-b5fb-b1165e0e5300)

Home Page:
![image](https://github.com/user-attachments/assets/4f8cc066-d1ba-4590-b226-4b5d852411d7)

After entering Link and clicking on transfer:
![image](https://github.com/user-attachments/assets/d4386990-4f9b-4e3a-8498-1006968acdcd)

After Succesfully transferring:
![image](https://github.com/user-attachments/assets/e4a411f0-b1ce-49c5-84d4-bd3324b40d48)


To build locally first go to google dev console get oauth credentials for your project to enable login
You'll get a clients_secret.json like this:
![image](https://github.com/user-attachments/assets/95873dab-9f62-45ec-afb2-eb87fb1bec0b)


Add this to the .env variable also deploy the lambda project on AWS lambda create function uri and paste them all in .env

![image](https://github.com/user-attachments/assets/0fac47fd-f7c1-4a7f-bf92-23acec2acf41)



After putting all credentials first go to frontend directory:
1. npm run build
2. npm run start

Simultaneously open a new terminal and go to backend directory:
1. pip install -r requirements.txt
2. python wsgi.py

The project should work






