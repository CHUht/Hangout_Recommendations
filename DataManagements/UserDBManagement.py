import sqlite3
from BackendAPIStaticList import singleton
from threading import Lock

# manipulation of Users table
@singleton
class UserDBManager:
    def __init__(self):
        """
            Here we start all the points necessary to start this class
            We need to connect to the database
            and get the last id!
        """
        self.lock = Lock()
        self.set_last_id()

    def dbconnect(self):
        self.connection = sqlite3.connect("Database.db", check_same_thread=False)
        self.controller = self.connection.cursor()

    def dbdeconnect(self):
        self.connection.close()

    def set_last_id(self):

        """
            In this function we find the last id on the database
            this is done since we need to assign a new
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT user_id
                        FROM Users
                    """
            self.controller.execute(sql_command)
            all_ids = self.controller.fetchall()
            self.dbdeconnect()
        # print('all_ids')
        # print(all_ids)
        if len(all_ids) == 0:
            self.last_id = -1
        else:
            self.last_id = all_ids[-1][0]


    def create_new_user(self, uname, psw, email ,address = None, city = 'Paris'):

        """
            This function adds a new user to the user db table!
            It takes the given username and password to create it
            We assume the check for unique usernames is done at the front end level
        """
        with self.lock:
            self.dbconnect()
            self.last_id = self.last_id + 1
            sql_command = """
                INSERT INTO Users(user_id, uname, pword, email, address, city)
                VALUES ( ?, ?, ?, ?, ?, ? );
            """

            values = (self.last_id, uname, psw, email, address, city)
            self.controller.execute(sql_command, values)
            self.connection.commit()
            self.dbdeconnect()
        print('DB message: user {0} --- user id {1} --- created by {2}'
              .format(uname, self.last_id, email))


    def return_user_data(self, uname):

        """
            This function must return the user profile based on the username
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT *
                        FROM Users
                        WHERE uname='{0}'
                    """.format(uname)
            self.controller.execute(sql_command)
            data = self.controller.fetchall()
            if len(data) != 0:
                result = [data[0]]
            else:
                result = []
            self.dbdeconnect()
        return result

    def return_user_data_by_email(self, email:str):

        """
            This function must return the user profile based on the email
            It needs other database classes to work with it!
            For now just return the basic stuff
        """
        # self.dbconnect()
        # sql_command = """
        #             SELECT *
        #             FROM Users
        #         """
        # self.controller.execute(sql_command)
        # data = self.controller.fetchall()
        all_users = self.check_database()
        result = []
        for user in all_users:
            if user[3] == email:
                result.append(user)
        return result

    def return_user_id(self, uname):

        """
            This function takes in a username and returns a user id!
            The user names must all be unique
            We check the creation of usernames to avoid duplicates
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                                SELECT user_id
                                FROM Users
                                WHERE uname='{0}'
                            """.format(uname)
            self.controller.execute(sql_command)
            user_id = self.controller.fetchall()
            self.dbdeconnect()

        if(len(user_id) != 1):
            raise Exception("Fatal error occurred two ids for one username")

        return user_id[0][0]



    def return_user_by_id(self, user_id):

        """
            This function takes in a user id and returns a user!
            The user id must all be unique
            We check the creation of user id to avoid duplicates
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                                   SELECT *
                                   FROM Users
                                   WHERE user_id='{0}'
                               """.format(user_id)
            self.controller.execute(sql_command)
            users = self.controller.fetchall()
            self.dbdeconnect()
        if len(users) == 0:
            return []
        if (len(users) > 1):
            raise Exception("Fatal error occurred two users for one user id")

        return users[0]

    def return_usernames(self):

        """
            This function returns a list with all usernames
            This is done in the server level to check if there are any matching usernames
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT uname
                        FROM Users
                    """
            self.controller.execute(sql_command)
            unames = []
            for value in self.controller.fetchall():
                unames.append(value[0])
            self.dbdeconnect()
        return unames

    def return_emails(self):

        """
            This function returns the list of emails from all the users
            This is done to not have repeated emails on the database
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                            SELECT email
                            FROM Users
                        """
            self.controller.execute(sql_command)
            emails = []
            for value in self.controller.fetchall():
                emails.append(value[0])
            self.dbdeconnect()
        return emails

    def user_authentication(self, uname, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT uname, pword 
                        FROM Users
                        WHERE uname = '{0}'
                    """.format(uname)
            self.controller.execute(sql_command)
            compare = self.controller.fetchall()
            self.dbdeconnect()
        if password == compare[0][1]:
            return True
        else:
            return False

    def email_authentication(self, email, password):
        """
            This function returns true if the username matches the password
            False otherwise
        """
        check_user = self.return_user_data_by_email(email)
        if len(check_user) == 0:
            return False
        elif len(check_user) > 1:
            raise IndexError('fatal error: one email shared by multiple users')
        if password == check_user[0][2]:
            return True
        else:
            return False

    def modify_password(self, mail, newpw):
        """
                    This function modify the password for the user
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                                UPDATE Users SET pword = ?
                                WHERE email = ?
                        """
            self.controller.execute(sql_command, (newpw, mail))
            self.connection.commit()
            self.dbdeconnect()
        print('updated user: ', self.return_user_data_by_email(mail))



    def check_database(self):
        # Returns everything in it
        with self.lock:
            self.dbconnect()
            sql_command = """
                        SELECT *
                        FROM Users
                    """
            self.controller.execute(sql_command)

            # print('checke_database')

            # for col in self.controller.fetchall():
            #     print(col)
            result = self.controller.fetchall()
            self.dbdeconnect()
        return result

    def delete_user_table(self):
        """
            Created for debuging
            Deletes the data in the user table!
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                            DELETE FROM Users;
                        """
            self.controller.execute(sql_command)
            self.connection.commit()

            sql_command = """
                            VACUUM;
                        """
            self.controller.execute(sql_command)
            self.connection.commit()
            self.dbdeconnect()

    def drop_table(self):
        """
            Created for debuging
            Drops the table!
        """
        with self.lock:
            self.dbconnect()
            sql_command = """
                        DROP TABLE Users;
                    """
            self.connection.execute(sql_command)
            self.dbdeconnect()

if __name__ == "__main__":
    userDBManager = UserDBManager()
    # userDBManager.delete_user_table()
    print(userDBManager.check_database())
    # exit()
    # userDBManager.modify_password('jiahao.lu@student-cs.fr', 'newpw')
    # print(userDBManager.return_user_data('adnaneh'))
    # email = 'lujiahao8146@gmail.com'
    # print(userDBManager.return_user_data_by_email(email))
    # print(userDBManager.email_authentication(email,'nopw'))
    # print(userDBManager.return_user_data('who'))
    # userDBManager.create_new_user('who', 'nopw', '123@gmail.com')
    # userDBManager.create_new_user('who2', 'nopw', 'lujiahao8146@gmail.com')
    # userDBManager.create_new_user('Lu1','withpw','jiahao.lu@student-cs.fr')
    # userDBManager.delete_user_table()
    # userDBManager.drop_table()
    # print(userDBManager.return_usernames())
    # print(userDBManager.check_database())
