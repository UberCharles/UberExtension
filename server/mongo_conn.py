import motor

# Connect to mongod and create reference to database "uber_db"
mongo = motor.MotorClient('localhost', 27017)["uber_db"]
