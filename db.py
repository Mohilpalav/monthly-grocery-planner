import os
import re
import sqlite3

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'db.db')


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(SQLITE_PATH)

    def select(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        return c.fetchall()

    def execute(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        self.conn.commit()


    def create_user(self, name, username, encrypted_password):
        self.execute('INSERT INTO user (name, user_name, password) VALUES (?, ?, ?)',
                     [name, username, encrypted_password])

    def get_user(self, username):
        data = self.select('SELECT * FROM user WHERE user_name=?', [username])
        if data:
            d = data[0]
            user_id = d[0]
            return {
                'user_id': d[0],
                'user_name': d[1],
                'password': d[2],
                'name': d[3]
            }
        else:
            return None

    def get_products(self):
        data = self.select('SELECT * FROM grocery')
        if data:
            return data

    def add(self,product_id,quantity,user_id):
        self.execute('DELETE from monthly_list WHERE product_id = ? AND user_id = ?',(product_id,user_id))
        self.execute('INSERT INTO monthly_list (user_id, product_id, quantity) VALUES (?, ?, ?)',
                     [user_id, product_id, quantity])

    def remove(self,product_id,user_id):
        self.execute('DELETE from monthly_list WHERE product_id = ? AND user_id = ?',(product_id,user_id))

    def get_list(self,user_id):
        data = self.select('Select G.product_name,G.product_price,G.product_image,M.quantity,G.product_id from grocery G, monthly_list M where G.product_id = M.product_id  and M.user_id = ?',[user_id])
        if data:
            return data
        else:
            return 0

    def get_bill(self,bill_id,user_id):
        data = self.select('Select G.product_name,G.product_price,G.product_image,B.product_quantity from grocery G, bills B where G.product_id = B.product_id  and B.user_id = ? and B.bill_id = ?',(user_id,bill_id))
        if data:
            return data
        else:
            return 0

    def get_total(self,user_id):
        data = self.select('Select sum(G.product_price * M.quantity) from grocery G, monthly_list M where G.product_id = M.product_id and M.user_id = ?',[user_id])
        if(data[0][0]):
            data = format(data[0][0], '.2f')
            return data
        else:
            return 0

    def get_missed_products(self,bill_id,user_id):
        data = self.select('Select product_name,product_image from grocery where product_id in  (select product_id from monthly_list where user_id = ? and product_id not in (select product_id from bills where bill_id=? and user_id = ?))',(user_id,bill_id,user_id))
        if data:
            return data
        else:
            return 0

    def top_categories(self,bill_id,user_id):
        data = self.select('Select G.product_category,sum(G.product_price * B.product_quantity) as value ,count(B.product_id) from grocery G, bills B where G.product_id = B.product_id and B.user_id = ? and B.bill_id=? group by G.product_category order by value desc;',(user_id,bill_id))
        if data:
            return data
        else:
            return 0
    def get_extra_products(self,bill_id,user_id):
        data = self.select('Select product_name,product_image from grocery where product_id in  (select product_id from bills where user_id = ? and bill_id=? and product_id not in (select product_id from monthly_list where user_id = ?))',(user_id,bill_id,user_id))
        if data:
            return data
        else:
            return 0

    def get_bill_total(self,bill_id,user_id):
        data = self.select('Select sum(product_price * B.product_quantity) from grocery G, bills B where G.product_id = B.product_id and B.user_id = ? and B.bill_id=?',(user_id,bill_id))
        if(data[0][0]):
            data = format(data[0][0], '.2f')
            return data
        else:
            return 0


    def close(self):
        self.conn.close()
