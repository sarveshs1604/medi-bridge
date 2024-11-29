# import os

# class Config:
#     # Flask configuration
#     SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

#     # Database configuration
#     MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
#     MYSQL_USER = os.getenv('MYSQL_USER', 'root')
#     MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
#     MYSQL_DB = os.getenv('MYSQL_DB', 'hospital_management')

#     @property
#     def MYSQL_DATABASE_URI(self):
#         return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}/{self.MYSQL_DB}"
