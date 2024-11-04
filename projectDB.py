from flask import *
import pymysql
import datetime

class db_connection:
    def __init__(self):
        pass
    
		# DB 연결
		# Connection을 반환하는 메서드
		# 클래스메서드는 인스턴스 생성 없이 호출 가능: db_connection.get_db()
    @classmethod
    def get_db(self):
        # return pymysql.connect(
        #     host='localhost',
        #     user='root',
        #     password='rnrtmdqls98!',
        #     db='mini1',
        #     charset='utf8',
        #     autocommit=True  # 테스트환경에서는 이렇게 사용
        # )
        return pymysql.connect(
            host='localhost',
            user='newuser',
            password='qwer1234',
            db='mini3',
            charset='utf8',
            autocommit=True  # 테스트환경에서는 이렇게 사용
        )

class UserDao:
    def __init__(self):
        pass
    
    def add_credit(self, user_id, amount):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = "UPDATE users SET credit = credit + %s WHERE user_id = %s"
        curs.execute(sql, (amount, user_id))  # 수정된 부분
        conn.commit()  # 변경 사항을 데이터베이스에 반영
        curs.close()
    
    # 사용자 조회
    def get_user(self, id, password):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = "SELECT * FROM users WHERE id = %s AND password = %s"
        curs.execute(sql, (id, password))
        user = curs.fetchone()
        conn.close()
        return user
    
    # 사용자 정보 ID로 조회 (마이페이지에서 사용)
    def get_user_by_id(self, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용
        sql = "SELECT * FROM users WHERE user_id = %s"
        curs.execute(sql, (user_id,))
        user = curs.fetchone()
        conn.close()
        return user
    
    def insert_user(self, user_name, id, password):
        curs = db_connection.get_db().cursor()
        sql = 'INSERT INTO users (user_name, id, password) VALUES (%s, %s, %s);'
        insert_num = curs.execute(sql, (user_name, id, password))
        db_connection.get_db().close()
        return f'Insert OK: {insert_num}'

    def get_current_user(self):
        user_id = session.get('user_id')  # 세션에서 사용자 ID를 가져옴
        if user_id:
            return UserDao().get_user_by_id(user_id)  # 사용자 ID로 사용자 정보를 조회
        return None


class PostDao:
    def __init__(self):
        pass
    
    # 모든 게시글 조회
    def get_all_posts(self):
        conn = db_connection.get_db()
        
        curs = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용
        sql = "SELECT * FROM posts ORDER BY created_at DESC"
        curs.execute(sql)
        posts = curs.fetchall()
        conn.close()
        return posts

    # 게시글 ID로 조회
    def get_post_by_id(self, post_id):
        conn = db_connection.get_db()
        curs = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용
        sql = "SELECT post_id, user_id, title, content, created_at FROM posts WHERE post_id = %s"
        curs.execute(sql, (post_id,))
        post = curs.fetchone()
        conn.close()
        return post

    # 게시글 추가
    def insert_post(self, user_id, title, content):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = "INSERT INTO posts (user_id, title, content, created_at) VALUES (%s, %s, %s, %s)"
        curs.execute(sql, (user_id, title, content, datetime.datetime.now()))
        conn.commit()
        conn.close()

    # 게시글 수정
    def update_post(self, post_id, new_title, new_content):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = "UPDATE posts SET title = %s, content = %s, updated_at = NOW() WHERE post_id = %s"
        curs.execute(sql, (new_title, new_content, post_id))
        conn.commit()
        conn.close()

# 상품 관련 DB
class productDAO:
    def __init__(self):
        pass
    
    def get_sold_products(self, user_id):
        conn = db_connection.get_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 판매자가 user_id인 모든 상품과 판매 상태 조회
        query = '''
            SELECT p.product_name AS product_name, p.price AS price, 
                IF(o.order_id IS NULL, '판매 중', '판매 완료') AS status, 
                o.order_date AS sold_date, o.user_id AS buyer_id
            FROM products p
            LEFT JOIN orders o ON p.product_id = o.product_id
            WHERE p.user_id = %s
            ORDER BY p.product_id DESC
        '''
        cursor.execute(query, (user_id,))
        selling_products = cursor.fetchall()
        cursor.close()
        
        return selling_products
    
    def get_all_products(self):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = "SELECT * FROM products"  # 상품 정보를 가져오는 SQL
        curs.execute(sql)
        rows = curs.fetchall()
        columns = [column[0] for column in curs.description]  # 컬럼 이름을 가져오기
        products = [dict(zip(columns, row)) for row in rows]  # 딕셔너리로 변환
        conn.close()
        return products

    
    # Productid 조회
    def get_product_by_id(self, product_id):
        conn = db_connection.get_db()
        # DictCursor를 사용하여 딕셔너리 형태로 결과를 반환
        curs = conn.cursor(pymysql.cursors.DictCursor)  
        sql = 'SELECT * FROM products WHERE product_id = %s'
        curs.execute(sql, (product_id,))
        product = curs.fetchone()  # 단일 상품이므로 fetchone 사용
        curs.close()
        
        if product is None:
            print("No product found for ID:", product_id)
        else:
            print("Product found:", product)  # Debugging output
            
        return product
    
    # product_id  - 구매페이지
    def purchase_product(self, product_id, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor()

        # 1. 해당 상품의 가격을 확인하고 유저의 크레딧 확인
        product_sql = 'SELECT price FROM products WHERE product_id = %s'
        curs.execute(product_sql, (product_id,))
        product = curs.fetchone()
        
        if not product:
            curs.close()
            return "상품을 찾을 수 없습니다."

        price = product[0]
        
        # 2. 유저의 크레딧 확인
        user_sql = 'SELECT credit FROM users WHERE user_id = %s'
        curs.execute(user_sql, (user_id,))
        user = curs.fetchone()

        if not user or user[0] < price:
            curs.close()
            return "크레딧이 부족합니다."

        # 3. 유저의 크레딧 차감 및 상품 상태를 'sold'로 업데이트
        update_user_sql = 'UPDATE users SET credit = credit - %s WHERE user_id = %s'
        update_product_sql = 'UPDATE products SET status = %s WHERE product_id = %s'

        curs.execute(update_user_sql, (price, user_id))
        curs.execute(update_product_sql, ('sold', product_id))

        conn.commit()  # 데이터베이스에 변경 사항 반영
        curs.close()
        
        return "구매가 완료되었습니다."
    
    # 상품 추가
    def add_product(self, product_name, description, image_path, price, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor()
        add_sql = '''
        INSERT INTO products (product_name, description, image_path, price, user_id)
                VALUES (%s, %s, %s, %s, %s)
        '''
        curs.execute(add_sql, (product_name, description, image_path, price, user_id))
        conn.commit()  
        curs.close()
        conn.close()

    # 상품 목록 가져오기 -- 메인페이지
    def get_all_products(self):
        conn = db_connection.get_db()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT product_id, product_name, description, image_path, status FROM products"
        curs.execute(sql)
        products = curs.fetchall()
        conn.close()
        return products

    # user_id로 상품 조회
    def get_products_by_user_id(self, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = 'SELECT * FROM products WHERE user_id = %s'
        curs.execute(sql, (user_id,))
        curs.close()
    
    # 상품 삭제
    def delete_product(self, product_id):
        conn = db_connection.get_db()
        curs = conn.cursor()
        sql = 'DELETE FROM products WHERE product_id = %s'
        curs.execute(sql, (product_id,))
        curs.close()
    
    # 상품 수정
    def update_product(self, product_id, **kwargs):
        conn = db_connection.get_db()
        curs = conn.cursor()
        fields = ', '.join([f'{key} = %s' for key in kwargs.keys()])
        sql = f'UPDATE products SET {fields} WHERE product_id = %s'
        values = list(kwargs.values()) + [product_id]
        curs.execute(sql, values)
        curs.close()
        
    # 상품 생성 시 크레딧 500 감소하도록 처리
    def generate_image(self, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor()
        
        # 크레딧이 충분한지 확인하고 감소시키는 쿼리
        update_sql = '''
        UPDATE users
        SET credit = credit - 500
        WHERE user_id = %s AND credit >= 500
        '''
        curs.execute(update_sql, (user_id,))
        conn.commit()  # 변경 사항 적용
        
        # 변경 사항이 적용되었는지 확인
        if curs.rowcount == 0:
            # 크레딧 부족으로 인해 업데이트되지 않음
            curs.close()
            return False
        
        curs.close()
        return True
    # def generate_image(self,user_id):
    #     conn = db_connection.get_db()
    #     curs = conn.cursor()
    #     # 추가될 때 크레딧 감소시켜야 함
    #     update_sql = '''
    #     UPDATE users
    #     SET credit = credit - 500
    #     WHERE user_id = %s AND credit >= 500
    #     '''
    #     curs.execute(update_sql,(user_id,))
    #     curs.close()
    
class orderDAO:
    def __init__(self):
        pass
    
    def createOrder(self,product_id, user_id, order_price):
        conn = db_connection.get_db()
        curs = conn.cursor()
        
        sql = '''
        INSERT INTO orders (product_id, user_id, order_price)
                VALUES (%s, %s, %s)
        '''
        curs.execute(sql, (product_id, user_id, order_price,))
        curs.close()
        
    def get_orders_by_user(self, user_id):
        conn = db_connection.get_db()
        curs = conn.cursor()
        
        query = '''
        SELECT products.product_name, orders.order_date, orders.order_price, products.status
        FROM orders
        JOIN products ON orders.product_id = products.product_id
        WHERE products.user_id = %s
        '''
        curs.execute(query, (user_id,))
        result = curs.fetchall()
        
        curs.close()
        return result
    
    # 판매자가 등록한 상품의 판매 내역 조회
    

# 클래스 수정해서 사용
        
if __name__ == '__main__':
    # 새로운 UserDao 테스트 코드
    user = UserDao().get_user('test_user@example.com', 'test_password') # 확인용
    if user:
        print(f"User found: {user}")
    else:
        print("User not found")
    