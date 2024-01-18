import sqlite3 
def check_medicine_in_database(medicine_name):
     conn = sqlite3.connect('mrs.db')
     cursor = conn.cursor()

     cursor.execute("SELECT * FROM mrs_medicine WHERE medicine_name = ?", (medicine_name,))
    
     result = cursor.fetchone()

     conn.close()

     if result:
        return True
     else:
        return False
