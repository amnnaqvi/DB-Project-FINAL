import pyodbc

#RAYYAN PC
# def get_db_connection():
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=localhost;'
#         'DATABASE=DBProject;'
#         'UID=sa;'
#         'PWD=rs9190678_'
#     )
#     return conn

#Amn PC
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=AMN-NAQVI\\SQLEXPRESS;'
        'DATABASE=DBProject;'
        'Trusted_Connection=yes;'
    )
    return conn


def initialize_database(conn, script_path='C:\\Projects\\hu_eats_py\\db\\database.sql'):
    cursor = conn.cursor()
    with open(script_path, 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.execute(sql_script)
    conn.commit()

conn = get_db_connection()
# initialize_database(conn)  # Run this only if tables do not exist

class DatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    # ADMIN

    def get_admin_info_login(self, email):
        query = "SELECT admin_id, password, name FROM Admin WHERE email = ? and is_active = 1"
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        return cursor.fetchone()

    #for admins

    def view_admin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Admin")
        info = cursor.fetchall()
        cursor.close()
        return info
    
    def count_admin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM Admin")
        info = cursor.fetchall()
        cursor.close()
        return info

    def add_admin(self, a_id, a_name, a_email, a_pass):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SET IDENTITY_INSERT Admin ON; 
                INSERT INTO Admin (admin_id, name, email, password, is_active) 
                VALUES (?, ?, ?, ?, ?); 
                SET IDENTITY_INSERT Admin OFF;
                """,
                (a_id, a_name, a_email, a_pass, 1)
            )
            self.conn.commit()
            cursor.close()
            return 1
        except Exception:
            return 0

    def edit_admin(self, a_id, a_name, a_email, a_pass):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE Admin 
                SET name = ?, email = ?, password = ? 
                WHERE admin_id = ?;
                """,
                (a_name, a_email, a_pass, a_id)
            )
            self.conn.commit()
            cursor.close()
            return 1
        except Exception:
            return 0

    def update_admin_status(self, a_id, new_status):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE Admin 
                SET is_active = ? 
                WHERE admin_id = ?;
                """,
                (new_status, a_id)
            )
            self.conn.commit()
            cursor.close()
            return 1
        except Exception:
            return 0
        
    # VENDORS
    
    def fetch_current_order_status(self,order_id):
        query="select status from Orders where order_id=?"
        cursor = self.conn.cursor()
        cursor.execute(query, (order_id,))
        status=cursor.fetchall()
        return status[0][0]

    def get_completed_orders(self,vendor_id):
        query="""
        select OD.order_id,item_name,quantity,price_per_unit,
        quantity*price_per_unit as [Total Price], order_placed, order_received, status 
        from Order_Details OD INNER JOIN Orders O ON O.order_id=OD.order_id 
        INNER JOIN Menu_Items M on OD.item_id=M.item_id where O.vendor_id=? and status='Confirmed'
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,))
        return cursor.fetchall()

    def update_order_status(self,order_id,text,user_id):
        query="""
            CALL UpdateOrderStatus
             
              """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (text,order_id))
            self.conn.commit()
    
    def get_live_orders(self,vendor_id):
        query="""
        select OD.order_id,item_name,user_id,quantity,
        quantity*price_per_unit as [Total Price], order_placed, status 
        from Order_Details OD INNER JOIN Orders O ON O.order_id=OD.order_id 
        INNER JOIN Menu_Items M on OD.item_id=M.item_id 
        where O.vendor_id=? 
        and (status='Ready' or status='Making' or status='Pending')
        and is_pickup=0
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,))
        return cursor.fetchall()

    def get_pickup_orders(self,vendor_id):
        query="""
        select OD.order_id,item_name,user_id,quantity,
        quantity*price_per_unit as [Total Price], order_placed, status 
        from Order_Details OD INNER JOIN Orders O ON O.order_id=OD.order_id 
        INNER JOIN Menu_Items M on OD.item_id=M.item_id 
        where O.vendor_id=? 
        and (status='Ready' or status='Confirmed' or status='Pending')
        and is_pickup=1
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,))
        return cursor.fetchall()
    
    def vendor_change_price(self,vendor_id,item_id,new_price):
        query="""
            Update Menu_Items
            set price=?
            where vendor_id=? and item_id=?
            """
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (new_price,vendor_id,item_id))
            self.conn.commit()
    
    def vendor_change_stock(self,vendor_id,item_id,new_stock):
        query="""
            Update Menu_Items
            set units_in_stock=?
            where vendor_id=? and item_id=?
            """
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (new_stock,vendor_id,item_id))
            self.conn.commit()
    
    def vendor_change_name(self,vendor_id,item_id,new_name):
        query="""
            Update Menu_Items
            set item_name=?
            where vendor_id=? and item_id=?
            """
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (new_name,vendor_id,item_id))
            self.conn.commit()
    
    def vendor_add_item(self,vendor_id,item_name,price,sub_id,units_in_stock):
        query="insert into Menu_Items (vendor_id, item_name, price, sub_id, units_in_stock) VALUES (?,?,?,?,?)"
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,item_name,price,sub_id,units_in_stock))
        self.conn.commit()
        cursor.close()
    
    def vendor_view_items (self,vendor_id):
        query="""
        select item_id, item_name, price, sub_type, units_in_stock, is_sold 
        from Menu_Items M ,SubCategory S 
        where vendor_id=? and M.sub_id=S.sub_id
        group by is_sold,item_id,item_name, price, sub_type, units_in_stock
        order by is_sold desc
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (vendor_id))
            result=cursor.fetchall()
            self.conn.commit()
        return result
    
   
    
    def update_subcategory_id(self,sub_id,vendor_id,item_id):
        query="""
            Update Menu_Items
            set sub_id=?
            where vendor_id=? and item_id=?
            """
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (sub_id,vendor_id,item_id))
            self.conn.commit()

    def find_subcategory_id(self,sub_name):
        query="select sub_id from SubCategory where sub_type=?"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (sub_name))
            result=cursor.fetchall()
            self.conn.commit()
        return result
    
    def find_subcategories(self):
        query="select sub_type from SubCategory"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            result=cursor.fetchall()
            self.conn.commit()
        return result
    
    def vendor_disable_item(self,item_id):
        query='''update Menu_Items
        set is_sold=0 where item_id=?'''
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (item_id))
            self.conn.commit()
    
    def vendor_enable_item(self,item_id):
        query='''update Menu_Items
        set is_sold=1 where item_id=?'''
        cursor = self.conn.cursor()
        with self.conn.cursor() as cursor:
            cursor.execute(query, (item_id))
            self.conn.commit()

    def is_enable(self,item_id):
        query="select is_sold from Menu_Items where item_id=?"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (item_id,))
            enable=cursor.fetchone()
        return enable[0]
    
    def fetch_vendor_order_history(self,vendor_id):
        query="""
        select OD.order_id,item_name,user_id,quantity,
        quantity*price_per_unit as [Total Price], order_placed, order_received, is_pickup
        from Order_Details OD INNER JOIN Orders O ON O.order_id=OD.order_id 
        INNER JOIN Menu_Items M on OD.item_id=M.item_id 
        where O.vendor_id=? 
        and status='Completed'
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,))
        return cursor.fetchall()
    
    def fetch_vendor_rating(self,vendor_id):
        query="""
            SELECT AVG(f.rating) AS mean_rating
            FROM Feedback f JOIN Orders o ON f.order_id = o.order_id
            WHERE o.vendor_id = ? -- Replace `?` with the specific vendor_id
            GROUP BY o.vendor_id"""
        cursor = self.conn.cursor()
        cursor.execute(query, (vendor_id,))
        return cursor.fetchone()

    #USER

    def place_order(self, user_id, is_pickup, total_cost):
        """Call the PlaceOrder stored procedure."""
        cursor = self.conn.cursor()
        try:
            # Execute the stored procedure with required parameters
            cursor.execute("{CALL PlaceOrder (?, ?, ?)}", (user_id, is_pickup, total_cost))
            self.conn.commit()
            return True, "Order placed successfully."
        except Exception as e:
            self.conn.rollback()
            print(f"Error in place_order: {e}")
            return False, str(e)
        finally:
            cursor.close()


    def deposit_money(self, user_id, deposit_amount):
        """Call the DepositMoney stored procedure."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("{CALL DepositMoney (?, ?)}", (user_id, deposit_amount))
            self.conn.commit()
            return True, "Deposit successful."
        except Exception as e:
            self.conn.rollback()
            print(f"Error in deposit_money: {e}")
            return False, str(e)
        finally:
            cursor.close()

    def add_to_user_favorites(self, user_id, item_id):
        cursor = self.conn.cursor()
        
        # Check if the item is already in favorites for the user
        test = "SELECT item_id FROM User_Favorites WHERE user_id = ?"
        cursor.execute(test, (user_id,))
        results = [row[0] for row in cursor.fetchall()]  # Extract item_ids from tuples
        
        # If item_id is already in results, it’s already a favorite
        if item_id in results:
            return False  # Indicating the item is already in favorites
        
        # Insert the new favorite item
        query = """INSERT INTO User_Favorites (user_id, item_id, added_at)
                VALUES (?, ?, GETDATE())
                """
        try:
            cursor.execute(query, (user_id, item_id))
            self.conn.commit()
        
        except Exception as e:
            print(f"Error in add_to_user_favorites: {e}")
            self.conn.rollback()
            return False
        
        finally:
            cursor.close()
        
        return True
    


    def fetch_user_order_history(self, user_id):
        query = """
        SELECT DISTINCT
            Orders.order_id,
            Orders.total_cost,
            Orders.order_placed AS order_date,
            Vendors.vendor_name,
            Orders.status AS status
        FROM Orders
        JOIN Vendors ON Orders.vendor_id = Vendors.vendor_id
        WHERE Orders.user_id = ?
        ORDER BY Orders.order_placed DESC
        """

        orders = []
        with self.conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            # Process results into a list of dictionaries
            for row in results:
                orders.append({
                    'order_id': row.order_id,
                    'total_cost': row.total_cost,
                    'order_date': row.order_date.strftime("%Y-%m-%d %H:%M"),
                    'vendor_name': row.vendor_name,
                    'order_status': row.status
                })
        
        return orders

    def get_user_info(self, user_id):
        """Fetch user's name and current balance."""
        cursor = self.conn.cursor()
        query = "SELECT full_name, current_balance FROM Users WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        user_info = cursor.fetchone()
        cursor.close()
        return user_info
    
    def add_or_update_cart_item(self, user_id, vendor_id, item_id):
        cursor = self.conn.cursor()
        
        try:
            # Check if the user has items from a different vendor in their cart
            cursor.execute("""SELECT TOP 1 mi.vendor_id FROM Cart c 
                            JOIN Menu_Items mi ON c.item_id = mi.item_id
                            WHERE c.user_id = ?""", (user_id,))
            existing_vendor = cursor.fetchone()
            
            if existing_vendor and existing_vendor[0] != vendor_id:
                return False, "different_vendor"

            # Check if the item is already in the cart
            cursor.execute("SELECT quantity FROM Cart WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            existing_item = cursor.fetchone()

            if existing_item:
                new_quantity = existing_item[0] + 1
                cursor.execute("UPDATE DBProject.dbo.Cart SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, user_id, item_id))
                self.conn.commit()
                return True, "quantity_updated"

            # Item is not in the cart, so add it
            cursor.execute("INSERT INTO DBProject.dbo.Cart (user_id, item_id, quantity) VALUES (?, ?, ?)", (user_id, item_id, 1))
            self.conn.commit()
            return True, "item_added"

        except Exception as e:
            print(f"Error in add_or_update_cart_item: {e}")
            self.conn.rollback()
            return False, f"error: {e}"

        finally:
            cursor.close()

    def get_vendor_info(self, vendor_id):
        cursor = self.conn.cursor()
        query = "SELECT * FROM Vendors WHERE vendor_id = ?"
        cursor.execute(query, (vendor_id,))
        vendor_info = cursor.fetchone()
        cursor.close()
        return vendor_info
    

    def fetch_order_details(self, order_id):
        cursor = self.conn.cursor()
        query = """SELECT 
                    o.user_id,
                    o.vendor_id,
                    v.vendor_name,
                    u.full_name AS user_name,
                    STRING_AGG(mi.item_name + ' (Qty: ' + CAST(od.quantity AS VARCHAR) + ')' + '              '+'x'+ CAST(od.price_per_unit AS VARCHAR), '\n') AS items_and_quantities,
                    o.total_cost,
                    o.order_placed AS order_date,
                    o.is_pickup,
                    ubh.record_no AS transaction_id
                FROM 
                    Orders o
                JOIN 
                    Users u ON o.user_id = u.user_id
                JOIN 
                    Vendors v ON o.vendor_id = v.vendor_id
                JOIN 
                    Order_Details od ON o.order_id = od.order_id
                JOIN 
                    Menu_Items mi ON od.item_id = mi.item_id
                LEFT JOIN
                    User_Balance_History ubh ON ubh.order_id = o.order_id AND ubh.is_deposit = 0
                WHERE 
                    o.order_id = ?
                GROUP BY 
                    o.user_id, o.vendor_id, v.vendor_name, u.full_name, o.total_cost, o.order_placed, o.is_pickup, ubh.record_no"""
        
        cursor.execute(query, (order_id,))
        info = cursor.fetchone()
        cursor.close()
        return info
    
    def fetch_cart_details(self, user_id):
        cursor = self.conn.cursor()
        query = """SELECT 
                    mi.item_name,
                    c.quantity,
                    (mi.price * c.quantity) AS item_total_cost,
                    mi.item_id
                FROM 
                    Cart c
                JOIN 
                    Menu_Items mi ON c.item_id = mi.item_id
                WHERE 
                    c.user_id = ?"""
        
        cursor.execute(query, (user_id,))
        cart_items = cursor.fetchall()
        
        total_cost = sum(item[2] for item in cart_items) 
        
        cursor.close()
        return cart_items, total_cost

    def fetch_balance_history(self, user_id):
        cursor = self.conn.cursor()
        query = """SELECT 
                    CASE WHEN is_deposit = 1 THEN 'Deposit' ELSE 'Spent' END AS change_type,
                    record_no,
                    amount,
                    CONVERT(DATE, record_date) AS date,
                    CONVERT(TIME, record_date) AS time,
                    CASE
                        WHEN is_deposit = 1 THEN 'Deposited'
                        ELSE 'Order Deduction'
                    END AS description
                FROM 
                    User_Balance_History
                WHERE 
                    user_id = ?
                ORDER BY 
                    record_date DESC""" 
        cursor.execute(query, (user_id,))
        balance_history = cursor.fetchall()
        cursor.close()
        return balance_history

    def remove_item_from_cart(self, user_id, item_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM Cart WHERE user_id = ? AND item_id = ?"
        cursor.execute(query, (user_id, item_id))
        self.conn.commit()
        cursor.close()

    def fetch_user_notifications(self, user_id):
        cursor = self.conn.cursor()
        query = """SELECT 
                    notif_no,
                    notif_content,
                    priority,
                    sent_at
                FROM 
                    Notifications n
                JOIN 
                    Notif_Type nt ON n.notif_type = nt.reference_id
                WHERE 
                    n.user_id = ?
                ORDER BY 
                    sent_at DESC"""
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()
        cursor.close()
        return notifications

    def fetch_user_favorite_items(self, user_id):
        cursor = self.conn.cursor()
        query = """SELECT 
                        uf.item_id,
                        mi.item_name,
                        v.vendor_name,
                        uf.added_at AS date_added,
                        mi.price,
                        v.vendor_id
                    FROM 
                        User_Favorites uf
                    JOIN 
                        Menu_Items mi ON uf.item_id = mi.item_id
                    JOIN 
                        Vendors v ON mi.vendor_id = v.vendor_id
                    WHERE 
                        uf.user_id = ? AND mi.is_sold = 1 AND v.is_active = 1"""
        
        cursor.execute(query, (user_id,))
        favorite_items = cursor.fetchall()
        cursor.close()
        
        return favorite_items

    def remove_favorites(self, user_id, item_id):
        cursor = self.conn.cursor()
        query = """DELETE FROM User_Favorites WHERE user_id = ? AND item_id = ?"""
        try:
            cursor.execute(query, (user_id, item_id))
            self.conn.commit()
            return True, "Item removed from favorites"
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False, f"error: {e}"
        finally:
            cursor.close()
    

    def delete_item(self, vendor_id, item_id):
        cursor = self.conn.cursor()

        try:
            
            cursor.execute("DELETE FROM User_Favorites WHERE item_id = ?", (item_id,))
            

            cursor.execute("DELETE FROM Cart WHERE item_id = ?", (item_id,))
            
            cursor.execute("DELETE FROM Menu_Items WHERE item_id = ? AND vendor_id = ?", (item_id, vendor_id))
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            print(f"error while deleting: {e}")

        cursor.close()
    
    def insert_item(self, item_name, vendor_id, price, sub_id, units_in_stock, description, image_url):
        cursor = self.conn.cursor()
        try:
            query = """INSERT INTO Menu_Items 
                        (item_name, vendor_id, price, sub_id, units_in_stock, description, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (item_name, vendor_id, price, sub_id, units_in_stock, description, image_url))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Error while adding item: {e}")
        finally:
            cursor.close()
        
    
    def empty_cart(self, user_id):
        cursor = self.conn.cursor()
        query = """DELETE FROM Cart WHERE user_id = ?"""

        try:
            cursor.execute(query, (user_id,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Error while deleting cart items: {e}")
        finally:
            cursor.close()


        
    def get_user_info_login(self, email):
        query = "SELECT user_id, password, is_active FROM Users WHERE email = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        return cursor.fetchone()

    def add_rating(self, user_id, order_id, rating):
        cursor = self.conn.cursor()
        check = "SELECT user_id, order_id FROM Feedback WHERE user_id = ? AND order_id = ?"
        cursor.execute(check, (user_id, order_id, rating))
        if check:
            try:
                query = "UPDATE Feedback (user_id, order_id, rating, rated_at) VALUES (?, ?, ?, GETDATE())"
                cursor.execute(query, (user_id, order_id, rating))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                print(f"Error while adding rating: {e}")
            finally:
                cursor.close()
        try:
            query = "INSERT INTO Feedback (user_id, order_id, rating, rated_at) VALUES (?, ?, ?, GETDATE())"
            cursor.execute(query, (user_id, order_id, rating))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Error while adding rating: {e}")
        finally:
            cursor.close()
