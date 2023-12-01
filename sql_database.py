import csv
import mysql.connector


mydb = mysql.connector.connect(host="localhost",user="root",passwd="p?CF6!&EGeDzD5Jg",database="mydatabase")
mycursor = mydb.cursor()

def create_database():
    query = """
    CREATE TABLE pamir_simulation_data (
        simulation_uuid VARCHAR(255),
        check_in_avg_waiting_time VARCHAR(255),
        check_out_avg_waiting_time VARCHAR(255),
        gym_avg_waiting_time VARCHAR(255),
        pool_avg_waiting_time VARCHAR(255),
        dine_avg_waiting_time VARCHAR(255),
        total_revenue INT,
        downgraded_from_premium INT,
        downgraded_from_deluxe INT
    );
"""
    mycursor.execute(query)

    print("Table has been created")

def delete_database():
    mycursor.execute("DROP TABLE pamir_simulation_data")

    print("Table has been dropped")

def add_data(data):

    # SQL insert statement with all the necessary fields
    sql_insert = """
    INSERT INTO pamir_simulation_data 
    (simulation_uuid, downgraded_from_premium, downgraded_from_deluxe, 
     check_in_avg_waiting_time, check_out_avg_waiting_time, gym_avg_waiting_time, 
     pool_avg_waiting_time, dine_avg_waiting_time, total_revenue) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Extracting the values from the data dictionary in the same order as the SQL statement
    values = (
        data['simulation_uuid'], 
        data['downgraded_from_premium'], 
        data['downgraded_from_deluxe'], 
        data['check_in_avg_waiting_time'], 
        data['check_out_avg_waiting_time'], 
        data['gym_avg_waiting_time'], 
        data['pool_avg_waiting_time'], 
        data['dine_avg_waiting_time'], 
        data['total_revenue']
    )

    # Executing the SQL command
    mycursor.execute(sql_insert, values)

    # Committing the changes
    mydb.commit()

    print(mycursor.rowcount, "record(s) inserted.")

def print_data():
    #print the labels  
    mycursor.execute("SELECT * FROM pamir_simulation_data")

    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)

def get_data():
    mycursor.execute("SELECT * FROM pamir_simulation_data")

    myresult = mycursor.fetchall()

    return myresult


def save_to_csv():
    mycursor.execute("SELECT * FROM pamir_simulation_data")

    myresult = mycursor.fetchall()

    with open('simulation_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['simulation_uuid', 'check_in_avg_waiting_time', 'check_out_avg_waiting_time', 'gym_avg_waiting_time', 'pool_avg_waiting_time', 'dine_avg_waiting_time', 'total_revenue','downgraded_from_premium', 'downgraded_from_deluxe'])
        writer.writerows(myresult)
