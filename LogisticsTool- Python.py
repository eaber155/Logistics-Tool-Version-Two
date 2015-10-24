#imports random module
from random import randint
import psycopg2
import collections

'''Database functions'''
def connect_database():
    try:
        conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
    except:
        print "I am unable to connect to the database"

    cursor_connect = conn.cursor()
    return cursor_connect

def women_dict_from_database():
    cur = connect_database()
    sql= "SELECT * FROM INFORMATION ORDER BY LOCATION"

    cur.execute(sql)

    results = cur.fetchall()

    women_dict = {}

    for value, key in results:
        women_dict.setdefault(key, []). append(value)

    cur.close()

    return women_dict

def neighbour_dict_from_database():
    cur = connect_database()
    sql= "SELECT * FROM NEIGHBOURS ORDER BY AREA"

    cur.execute(sql)

    results = cur.fetchall()

    neighbour_dict = {}

    for value, key in results:
        neighbour_dict.setdefault(key, []). append(value)

    return neighbour_dict

    cur.close()

def workers_list_from_database():
    cur = connect_database()
    sql= "SELECT * FROM WORKERS"

    cur.execute(sql)

    results = cur.fetchall()

    workers_list =[]

    for row in results:
        worker = row[0]
        workers_list.append(worker)

    return workers_list

    cur.close()

def areas_database():
    cur = connect_database()
    sql= "SELECT LOCATION FROM AREAS"

    cur.execute(sql)

    results = cur.fetchall()

    area_list =[]

    for row in results:
        area = row[0]
        area_list.append(area)

    return area_list

    cur.close()

def number_of_women_database():
    cur = connect_database()
    sql= "SELECT LOCATION, POPULATION FROM AREAS"

    cur.execute(sql)

    results = cur.fetchall()

    area_population_dict = {}

    for key, value in results:
        area_population_dict.setdefault(key, []). append(value)

    return area_population_dict

    cur.close()

def square_area_database():
    cur = connect_database()
    sql= "SELECT LOCATION, SQUARE_AREA FROM AREAS"

    cur.execute(sql)

    results = cur.fetchall()

    square_area_dict = {}

    for key, value in results:
        square_area_dict.setdefault(key, []). append(value)

    return square_area_dict

    cur.close()

women_dict = women_dict_from_database()
# Calling the main functions depending on weather first visit or second visit            
print"1: First Time Visit "
print "2: Subsequent Visit"
print "3: Schedule Neigbouring Areas"

w= int(raw_input("Choose kind of visit: "))
print " "

if w == 1:
    '''This is for first time visiting'''
    #A dictionary with the number of women per area got from the database
    #or another source
    women_number_dict = number_of_women_database()

    #A dictionary showing the workers available
    #will be got later from the database
    workers_list = workers_list_from_database()

    #A list of all the areas to be visited as from the database
    area_list = areas_database()

    #A function to get the number of women in a particular area
    def add_num_of_women(area):
        num_of_women = women_number_dict[area][0]
        return num_of_women

    #A function get the total number of women in all the areas
    def total_num_of_women():
        total_num_of_women = 0
        
        for area in area_list:
            total_num_of_women += women_number_dict[area][0]
        return total_num_of_women

    #A function to get the area of a particular location from the database
    def add_area(area):
        #A dictionary showing the different locations and their areas
        area_dict = square_area_database()

        if area_dict[area]:
            area_size = float (area_dict[area][0])

        return area_size

    #A function to get the density of women in the various location
    def calculate_density():
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = float (num_of_women/size)

        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        sql = "UPDATE AREAS SET POPULATION_DENSITY = (%s) WHERE LOCATION = ('%s')" %(density_of_women, area)
        cur.execute(sql)
        conn.rollback()
        cur.close()
        return density_of_women

    #A function that returns the characteristics of a given area
    def get_characteristics(area):
        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        sql = "SELECT POPULATION, SQUARE_AREA, POPULATION_DENSITY FROM AREAS WHERE LOCATION = ('%s')" %area
        cur.execute(sql)
        results= cur.fetchall()
        conn.rollback()
        cur.close()
        return results

    #A function to get the total number of workers in the database
    def total_number_of_workers():
        #The workers_list placed as a local variable so that ot can rmain unchanged
        workers_list = workers_list_from_database()
        number_of_workers = len(workers_list)

        return number_of_workers

    #A function that gets the total number of workers in the database and
    #calculates the number of workers to be assigned per area
    def add_workers_numbers():
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
        total_number_of_women = total_num_of_women()

        num_of_workers = total_number_of_workers()

        num_of_women_per_worker = total_number_of_women/num_of_workers

         
        workers_per_unit_area = density_of_women/num_of_women_per_worker

        workers_in_area = int (workers_per_unit_area * size)
        return workers_in_area


    #A function to assign workers to the different areas
    def assign_workers():
        workers_in_area = add_workers_numbers()

        count = 0
        workers_left = len(workers_list)
        last_count = len(workers_list)-1

        workers_assigned = []

        #assign workers to different areas
        if workers_in_area > workers_left:
            workers_assigned.extend(workers_list)
            print "The number of workers available is less than the required number"
            print " "  #for space
            print "%d workers assigned instead of %d" %(workers_left,workers_in_area)
            print " "
        else:
            while count < workers_in_area:
                number = randint(0, last_count)
                worker = workers_list[number]
                workers_assigned.append(worker)
                del workers_list[number]
                last_count-=1
                
                count+=1

        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        cur.execute("DROP TABLE IF EXISTS WORKERS_ASSIGNED_FIRST_TIME")

        sql = "CREATE TABLE WORKERS_ASSIGNED_FIRST_TIME (NAME VARCHAR(80) NULL)"
        cur.execute(sql)

        for worker in workers_assigned:
            sql2 = "INSERT INTO WORKERS_ASSIGNED_FIRST_TIME(NAME) VALUES ('%s')"%(worker)
            cur.execute(sql2)


        sql3 = "SELECT * FROM WORKERS_ASSIGNED_FIRST_TIME"

        cur.execute(sql3)

        results = cur.fetchall()

        print "WORKERS ASSIGNED ARE: "
        for row in results:
            print row[0]

        conn.rollback()
        cur.close()
        print " "
                                 
        message = "The workers scheduled successfully"
        return message

    #main function
    area_list = areas_database()

    for area in area_list:
        print area
        
    print " "
    
    for area in area_list:
        name = area
        area_list = areas_database()

        count = 0

        while count< len(area_list):
            if name == area_list[count]:
                workers_numbers = add_workers_numbers()      
                results = get_characteristics(area)
                print name
                print " "
                print "Characteristics"
                for row in results:
                    print "Population is: ", row[0]
                    print "Area is: ", row[1]
                    print "Density is: ", row[2]
                print " "
                print "The number of workers to be assigned to this area is: ", workers_numbers
                print " "
                workers_assigned = assign_workers()
                print workers_assigned
                print " "
                print " "
                break
            count +=1
    
elif w == 2:
    '''This is for the subsequent visit'''
    #A dictionary showing the women in different locations from the database.
    women_dict = women_dict_from_database()

    #A dictionary showing the workers available
    #will be got later from the database
    workers_list = workers_list_from_database()

    #A list of all the areas to be visited as from the database
    area_list = areas_database()

    try:
        conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
    except:
        print "I am unable to connect to the database"

    cur = conn.cursor()
    conn.autocommit=True

    cur.execute("DROP TABLE IF EXISTS FOLLOW_UP_CHARACTERISTICS")

    sql = "CREATE TABLE FOLLOW_UP_CHARACTERISTICS (LOCATION VARCHAR(20) NULL, NUMBER_OF_WOMEN INT NULL, DENSITY_OF_WOMEN INT NULL)"
    cur.execute(sql)
    
    for area in area_list:
        sql2 = "INSERT INTO FOLLOW_UP_CHARACTERISTICS (LOCATION) VALUES ('%s') " %(area)
        cur.execute(sql2)
    conn.rollback()
    cur.close()

    #A function to get the number of women in a particular area
    def add_num_of_women(area):
        women_list = []

        if women_dict[area]:
            for women in women_dict[area]:
                women_list.append(women)

        num_of_women = len (women_list)

        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        sql = "UPDATE FOLLOW_UP_CHARACTERISTICS SET NUMBER_OF_WOMEN = (%s) WHERE LOCATION = ('%s')" %(num_of_women, area)
        cur.execute(sql)
        conn.rollback()
        cur.close()
        return num_of_women

    #A function to get the total number of women in the database
    def total_num_of_women():
        women_list = []
            
        for area in area_list:
            for women in women_dict[area]:
                women_list.append(women)
            
        total_num_of_women = len (women_list) 
        return total_num_of_women

    #A function to add the women in a particular area
    #to a list so that it can  be manipulated
    def add_list_of_women(area):
        women_list = []

        if women_dict[area]:
            for women in women_dict[area]:
                women_list.append(women)

        return women_list

    #A function to get the area of a particular location from the database
    def add_area(area):
        #A dictionary showing the different locations and their areas
        area_dict = square_area_database()

        if area_dict[area]:
            area_size = float (area_dict[area][0])
        return area_size

    #A function to get the density of women (women who are known) in the various location
    def calculate_density():
        num_of_women = add_num_of_women(area)
        size = add_area(area)

        density_of_women = float (num_of_women/size)
        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        sql = "UPDATE FOLLOW_UP_CHARACTERISTICS SET DENSITY_OF_WOMEN = (%s) WHERE LOCATION = ('%s')" %(density_of_women, area)
        cur.execute(sql)
        conn.rollback()
        cur.close()

        return density_of_women

    #A function that returns the characteristics of a given area
    def get_characteristics (area):
        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        sql = "SELECT NUMBER_OF_WOMEN, DENSITY_OF_WOMEN FROM FOLLOW_UP_CHARACTERISTICS WHERE LOCATION = ('%s')" %area
        cur.execute(sql)
        results= cur.fetchall()
        conn.rollback()
        cur.close()
        return results

    #A function to get the total number of workers in the database
    def total_number_of_workers():
        #The workers_list placed as a local variable so that it can remain unchanged
        workers_list = workers_list_from_database()
        number_of_workers = len(workers_list)

        return number_of_workers

    #A function that gets the total number of workers in the database and
    #calculates the number of workers to be assigned per area
    def add_workers_numbers():
        #The workers_list placed as a local variable so that ot can rmain unchanged
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
        list_of_women = add_list_of_women(area)
        total_number_of_women = total_num_of_women()

        num_of_workers = total_number_of_workers()

        num_of_women_per_worker = total_number_of_women/num_of_workers

         
        workers_per_unit_area = density_of_women/num_of_women_per_worker

        workers_in_area = int (workers_per_unit_area * size)
        return workers_in_area

    #A function to assign workers to the different areas
    def assign_workers():
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
        list_of_women = add_list_of_women(area)
        total_number_of_women = total_num_of_women()

        num_of_workers = total_number_of_workers()

        num_of_women_per_worker = total_number_of_women/num_of_workers

         
        workers_per_unit_area = density_of_women/num_of_women_per_worker
        
        workers_in_area = add_workers_numbers()

        count = 0
        workers_left = len(workers_list)
        last_count = len(workers_list)-1

        workers_assigned = []

        if workers_in_area > workers_left:
            workers_assigned.extend(workers_list)
            print "The number of workers available is less than the required number"
            print " "  #for space
            print "%d workers assigned instead of %d" %(workers_left,workers_in_area)
        else:
            while count < workers_in_area:
                number = randint(0, last_count)
                worker = workers_list[number]
                workers_assigned.append(worker)
                del workers_list[number]
                last_count-=1
                
                count+=1                

        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        cur.execute("DROP TABLE IF EXISTS WORKERS_ASSIGNED_MAPPED")
        sql = "CREATE TABLE WORKERS_ASSIGNED_MAPPED(WORKER VARCHAR (80) NULL, WOMAN VARCHAR (80) NULL)"
        cur.execute(sql)
        
        #assign workers to different women
        while len(list_of_women)!=0:
            for worker in workers_assigned:
                if len(list_of_women)==0:
                    break
                else:
                    i= 0
                    while i < num_of_women_per_worker:
                        if len(list_of_women)==1:
                            sql2 = "INSERT INTO WORKERS_ASSIGNED_MAPPED(WORKER, WOMAN) VALUES ('%s','%s')"%(worker, list_of_women[0])
                            cur.execute(sql2)
                            del list_of_women[0]
                        else:
                            sql3 = "INSERT INTO WORKERS_ASSIGNED_MAPPED(WORKER, WOMAN) VALUES ('%s','%s')"%(worker, list_of_women[i])
                            cur.execute(sql3)
                            del list_of_women[i]
                        i+=1

        cur.execute("DROP TABLE IF EXISTS WORKERS_ASSIGNED_FOLLOW_UP")

        sql4 = "CREATE TABLE WORKERS_ASSIGNED_FOLLOW_UP (NAME VARCHAR(80) NULL)"
        
        cur.execute(sql4)

        for worker in workers_assigned:
            sql5 = "INSERT INTO WORKERS_ASSIGNED_FOLLOW_UP(NAME) VALUES ('%s')"%(worker)
            cur.execute(sql5)


        sql6 = "SELECT * FROM WORKERS_ASSIGNED_FOLLOW_UP"
        cur.execute(sql6)
        results = cur.fetchall()
  
        print "WORKERS ASSIGNED ARE: "
        for row in results:
            print row[0]

        print " "

        print "WORKERS ASSIGNED TO THE WOMEN:"
        print " "
       
        for worker in workers_assigned:
            woman = []
            sql7 = "SELECT WOMAN FROM WORKERS_ASSIGNED_MAPPED WHERE WORKER = '%s'"%worker
            cur.execute(sql7)
            results2 = cur.fetchall()
            for row in results2:
                woman.append(row[0])
            if len(woman)==1:
                print worker, ": ", woman[0]
            elif len(woman)>1:
                print worker, ": ", woman
            else:
                print "No woman assigned to this worker"
            
        print " "
        print " "

        #This code allows you to find out the exact women any worker has been
        #assigned to
        a=0
        length2 = len(workers_assigned)
        print "Enter the worker (to see the women that he has been assigned to): "
        print " "
        while a< length2:
            w = raw_input("Worker: ")
            print " "
            k = []
            n = 0
            l = 0

            sql8 = "SELECT WOMAN FROM WORKERS_ASSIGNED_MAPPED WHERE WORKER = '%s'"%w
            cur.execute(sql8)

            results3 = cur.fetchall()

            print "THE WOMEN ASSIGNED TO ", w, "ARE: "
            for row in results3:
                print row[0]

            print " "
            
            w = int(raw_input("Enter 0 to continue or any other number to find another worker's information: "))
            print " "
            if w ==0:
                break
            else:
                continue
            a+=1
        conn.rollback()
        cur.close()
        print " "
        message= "The workers in %s scheduled successfully" %area
        return message
    
    #The main function
    area_list = areas_database()
    area_length = 0
    
    print "AREAS AVAILABLE"
    print " "
    for area in area_list:
        index = area_list.index(area)
        print index, "-", area

    while area_length< len(area_list):
        area_index = int(raw_input("Choose area (using code): "))
        print " "
                
        for area in area_list:
            index = area_list.index(area)
            if area_index == index:
                name = area
                print name
                print " " #space
                workers_numbers = add_workers_numbers()      
                results = get_characteristics(area)
                print "Characteristics"
                for row in results:
                    print "Number of Women is: ", row[0]
                    print "Density of Women is: ", row[1]
                print " "
                print "The number of workers to be assigned to this area is: ", workers_numbers
                print " "
                workers_assigned = assign_workers()
                print workers_assigned
                print " "
                print " "
                break
        y = int(raw_input("Enter 0 to finish or any other number to move to another area: "))
        print " "
        if y ==0:
            break
        else:
            continue
        area_length+=1

elif w==3:
    ''''This is for the subsequent visit while visiting new areas'''
    #A dictionary showing neighbours to the different areas, got from database
    neighbour_dict = neighbour_dict_from_database()
    
    #A dictionary with women in different locations, got from the database
    women_dict = women_dict_from_database()

    #A dictionary showing the workers available
    #will be got later from the database
    workers_list = workers_list_from_database()

    #A list of all the areas to be visited as from the database
    area_list = areas_database()

    #A function to get the number of women in a particular area
    def add_num_of_women(area):
        women_list = []

        if women_dict[area]:
            for women in women_dict[area]:
                women_list.append(women)

        num_of_women = len (women_list)

        return num_of_women

    #A function to get the total number of women in the database
    def total_num_of_women():
        women_list = []
            
        for area in area_list:
            for women in women_dict[area]:
                women_list.append(women)
            
        total_num_of_women = len (women_list) 
        return total_num_of_women

    #A function to add the women in a particular area
    #to a list so that it can  be manipulated
    def add_list_of_women(area):
        women_list = []

        if women_dict[area]:
            for women in women_dict[area]:
                women_list.append(women)

        return women_list

    #A function to get the area of a particular location from the database
    def add_area(area):
        #A dictionary showing the different locations and their areas
        area_dict = square_area_database()

        if area_dict[area]:
            area_size = float (area_dict[area][0])

        return area_size

    #A function to get the density of women in the various location
    def calculate_density():
        num_of_women = add_num_of_women(area)
        size = add_area(area)

        density_of_women = float (num_of_women/size)

        return density_of_women

    #A function that returns the characteristics of a given area
    def get_characteristics ():
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
            
        characteristics = {'num_of_women':num_of_women, 'size':size,
                               'density_of_women': density_of_women}
        return characteristics

    #A function to get the total number of workers in the database
    def total_number_of_workers():
        #The workers_list placed as a local variable so that it can remain unchanged
        workers_list = workers_list_from_database()
        number_of_workers = len(workers_list)

        return number_of_workers

    #A function that gets the total number of workers in the database and
    #calculates the number of workers to be assigned per area
    def add_workers_numbers():
        #The workers_list placed as a local variable so that ot can rmain unchanged
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
        list_of_women = add_list_of_women(area)
        total_number_of_women = total_num_of_women()

        num_of_workers = total_number_of_workers()

        num_of_women_per_worker = total_number_of_women/num_of_workers

         
        workers_per_unit_area = density_of_women/num_of_women_per_worker

        workers_in_area = int (workers_per_unit_area * size)
        return workers_in_area

    #A function to assign workers to the different areas
    def assign_workers():
        num_of_women = add_num_of_women(area)
        size = add_area(area)
        density_of_women = calculate_density()
        list_of_women = add_list_of_women(area)
        total_number_of_women = total_num_of_women()

        num_of_workers = total_number_of_workers()

        num_of_women_per_worker = total_number_of_women/num_of_workers

         
        workers_per_unit_area = density_of_women/num_of_women_per_worker
        
        workers_in_area = add_workers_numbers()

        count = 0
        workers_left = len(workers_list)
        last_count = len(workers_list)-1

        workers_assigned = []

        if workers_in_area > workers_left:
            workers_assigned.extend(workers_list)
            print "The number of workers available is less than the required number"
            print "%d workers assigned instead of %d" %(workers_left,workers_in_area)
            print " "  #for space

        else:
            while count < workers_in_area:
                number = randint(0, last_count)
                worker = workers_list[number]
                workers_assigned.append(worker)
                del workers_list[number]
                last_count-=1
                
                count+=1                
        return workers_assigned

    #When we connect to the database, this entire code before this will be replaced
    #by a database query of the workers in the areas. The workers got from the database
    #will be assigned to the different neignours
    #Assign workers to the neighbouring areas

    def get_neighbour_list(area):
        neighbour_list = []

        if neighbour_dict[area]:
            for neighbour in neighbour_dict[area]:
                neighbour_list.append(neighbour)
        return neighbour_list
        
    
    def assign_workers_to_neighbours():
        workers_in_the_area = assign_workers()
       
        neighbour_list = get_neighbour_list(area)

        workers_per_neighbour = len(workers_in_the_area)/len(neighbour_list)

        try:
            conn = psycopg2.connect("dbname= 'Women_In_Areas' user= 'postgres' host= 'localhost'  password= 'namusokez'")
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()
        conn.autocommit=True

        cur.execute("DROP TABLE IF EXISTS NEIGHBOURS_ASSIGNED")
        sql = "CREATE TABLE NEIGHBOURS_ASSIGNED(NEIGHBOUR VARCHAR(80) NULL, WORKER VARCHAR(80) NULL)"
        cur.execute(sql)
        
        #assign workers to different women
        while len(workers_in_the_area)!=0:
            for neighbour in neighbour_list:
                if len(workers_in_the_area)==0:
                    break                
                else:
                    i= 0
                    while i < workers_per_neighbour:
                        if len(workers_in_the_area)==1:
                            sql2 = "INSERT INTO NEIGHBOURS_ASSIGNED(NEIGHBOUR, WORKER) VALUES ('%s','%s')"%(neighbour, workers_in_the_area[0])
                            cur.execute(sql2)
                            del workers_in_the_area[0]
                        else:
                            sql3 = "INSERT INTO NEIGHBOURS_ASSIGNED(NEIGHBOUR, WORKER) VALUES ('%s','%s')"%(neighbour, workers_in_the_area[i])
                            cur.execute(sql3)
                            del workers_in_the_area[i]
                        i+=1

        print "WORKERS ASSIGNED TO THE NEIGHBOURS:"
        print " "
       
        for neighbour in neighbour_list:
            worker = []
            sql4 = "SELECT WORKER FROM NEIGHBOURS_ASSIGNED WHERE NEIGHBOUR = '%s'"%neighbour
            cur.execute(sql4)
            results = cur.fetchall()
            for row in results:
                worker.append(row[0])
            if len(worker)==1:
                print neighbour, ": ", worker[0]
            elif len(worker)>1:
                print neighbour, ": ", worker
            else:
                print "No workers assigned to %s" %neighbour
            
        print " "
        print " "

        #This code allows you to find out the exact workers that have been assigned
        #to a neighbouring place


        print "Available Neighbours to ", area
       
        for neighbour in neighbour_list:
            neighbour_index = neighbour_list.index(neighbour)
            print neighbour_index, "- ", neighbour
        print " "
        a=0
        length2 = len(neighbour_list)
        print "Enter the neighbouring area to see the workers assigned to that area: "
        print " "
        while a< length2:
            w = raw_input("Neighbouring Area: ")
            print " "
            k = []
            n = 0
            l = 0

            sql5 = "SELECT WORKER FROM NEIGHBOURS_ASSIGNED WHERE NEIGHBOUR = '%s'"%w
            cur.execute(sql5)

            results2 = cur.fetchall()

            print "THE WORKERS ASSIGNED TO ", w, "ARE: "
            for row in results2:
                print row[0]

            print " "
            
            w = int(raw_input("Enter 0 to continue or any other number to find another worker's information: "))
            print " "
            if w ==0:
                break
            else:
                continue
            a+=1
        conn.rollback()
        cur.close()
        print " "
        message= "Workers have been successfully scheduled to the areas around %s" %area
        return message
        
    #The main function
    area_list = areas_database()
    area_length = 0
    
    print "AREAS AVAILABLE"
    print " "
    for area in area_list:
        index = area_list.index(area)
        print index, "-", area

    while area_length< len(area_list):
        area_index = int(raw_input("Choose area (using code): "))
        print " "
                
        for area in area_list:
            index = area_list.index(area)
            if area_index == index:
                name = area

                workers_numbers = add_workers_numbers()
                print name
                print " " #space
                print "The number of workers to be assigned to this area is: ", workers_numbers
                print " "
                workers_assigned = assign_workers_to_neighbours()
                print workers_assigned
                print " "
                print " "
                break
        y = int(raw_input("Enter 0 to finish or any other number to move to another area: "))
        print " "
        if y ==0:
            break
        else:
            continue
        area_length+=1
    
else:
    print "Wrong option chosen"




    


