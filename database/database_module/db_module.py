import psycopg2

# 테이블 정보 추가 함수
def insert_table(conn, table_name, user_input1=None, user_input2=None, user_input3=None):
    try:
        cur = conn.cursor()
        
        if table_name == "category": # category 테이블 정보 추가 - 받는 매개변수: category_name
            insert_category(cur, user_input1)
            
        elif table_name == "product": # product 테이블 정보 추가 - 받는 매개변수: category_id, product_name, price
            insert_product(cur, user_input1, user_input2, user_input3)
            
        elif table_name == "product_detail": # product_detail 테이블 정보 추가 - 받는 매개변수: product_id, product_description
            insert_product_detail(cur, user_input1, user_input2)

        else: # 잘못된 테이블 이름 입력 시 예외 처리
            raise TableSortException
            
        conn.commit()
        return True

    except psycopg2.ProgrammingError as exception: # table이 존재하지 않음
        print("입력한 테이블이 존재하지 않습니다.")
        conn.rollback()
        return False

    except psycopg2.IntegrityError as exception: # 값이 이미 존재하는 경우
        if table_name == "category":
            print("입력한 값이 이미 category 테이블에 존재합니다.")
        
        elif table_name == "product":
            print("입력한 값이 이미 product 테이블에 존재합니다.")
        
        elif table_name == "product_detail":
            print("입력한 값이 이미 product_detail 테이블에 존재합니다.")

        conn.rollback()
        return False

    except NullPointerException as exception: # table에 값이 존재하지 않는 경우
        if table_name == "category":
            print("입력한 값이 category 테이블에 존재하지 않습니다.")

        elif table_name == "product":
            print("입력한 값이 product 테이블에 존재하지 않습니다.")
        
        elif table_name == "product_detail":
            print("입력한 값이 product_detail 테이블에 존재하지 않습니다.")

        conn.rollback()
        return False
    
    except psycopg2.DataError as exception: # id가 유효한 범위를 초과한 경우
        print("입력한 id(프라이머리 키)가 유효한 범위를 초과했습니다.")
        conn.rollback()
        return False
	  
    except Exception as exception:
        print(f"Exception: {exception}")
        conn.rollback()
        return False
        
    finally:
        cur.close() # 커서 닫기


# 테이블 정보 수정 함수
def modify_table(conn, table_name, user_input1=None, user_input2=None, user_input3=None):
    try:
        cur = conn.cursor()

        updates = []
        values = []

        # 테이블과 컬럼 설정
        if table_name == "category":
            id_column = "category_id"
            if user_input1 is not None:  # 새로운 category_name
                updates.append("category_name = %s")
                values.append(user_input1)

        elif table_name == "product":
            id_column = "product_id"
            if user_input1 is not None:  # 새로운 category_id
                updates.append("category_id = %s")
                values.append(user_input1)
            if user_input2 is not None:  # 새로운 product_name
                updates.append("product_name = %s")
                values.append(user_input2)
            if user_input3 is not None:  # 새로운 price
                updates.append("price = %s")
                values.append(user_input3)

        elif table_name == "product_detail":
            id_column = "product_detail_id"
            if user_input1 is not None:  # 새로운 product_description
                updates.append("product_description = %s")
                values.append(user_input1)

        else:
            print("잘못된 테이블 이름입니다.")
            return False

        # 업데이트할 값이 없을 경우 처리
        if not updates:
            print("수정할 정보가 없습니다.")
            return False

        # 업데이트 쿼리 생성
        query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {id_column} = %s"
        values.append(user_input1)  # ID를 마지막에 추가

        # 쿼리 실행
        cur.execute(query, tuple(values))
        conn.commit()
        print(f"{table_name} 테이블의 {id_column} {user_input1}가 성공적으로 수정되었습니다.")
        return True

    except Exception as exception:
        print(f"Exception: {exception}")
        conn.rollback()
        return False

    finally:
        cur.close()


# 테이블 정보 삭제 함수
def delete_table(conn, table_name, id_value, force_delete = False):
    try:
        cur = conn.cursor()

        if not force_delete: # 강제 삭제 시, 경고 메시지 출력 없이 삭제 수행
            if table_name == "category": # 경고 메시지 출력: 카테고리 삭제 시 해당 카테고리에 속한 제품과 제품 세부 정보도 함께 삭제됨
                print("category 테이블의 값을 삭제할 경우, 해당 카테고리에 속한 제품과 제품 세부 정보도 함께 삭제됩니다. 정말 삭제하시겠습니까?")
                answer = input("Y/N: ")
                if answer.lower() != "y":
                    print("삭제를 취소합니다.")
                    return False
            
            elif table_name == "product": # 경고 메시지 출력: 제품 삭제 시 해당 제품에 대한 제품 세부 정보도 함께 삭제됨
                print("product 테이블의 값을 삭제할 경우, 해당 제품에 대한 제품 세부 정보도 함께 삭제됩니다. 정말 삭제하시겠습니까?")
                answer = input("Y/N: ")
                if answer.lower() != "y":
                    print("삭제를 취소합니다.")
                    return False

        id_column = f"{table_name}_id" # ID 컬럼 생성

        # id_value가 문자열일 경우, 이름을 통해 ID 조회
        if isinstance(id_value, str) and table_name != "product_detail":
            query = f"SELECT {id_column} FROM {table_name} WHERE {table_name}_name = %s"
            cur.execute(query, (id_value,))
            result = cur.fetchone()

            if result is None:  # 조회 결과가 없을 경우
                raise NullPointerException
            else:
                id_value = result[0]

        # 최종적으로 ID에 기반해 삭제 수행
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        cur.execute(query, (id_value,))
        conn.commit()
        return True

    except psycopg2.ProgrammingError as exception: # table이 존재하지 않음
        print("입력한 테이블이 존재하지 않습니다.")
        conn.rollback()
        return False

    except Exception as exception: 
        print(f"Exception: {exception}")
        conn.rollback()
        return False

    finally:
        cur.close()

# 테이블 정보 조회 함수
def search_table(conn, table_name, id_value):
    try:
        cur = conn.cursor()
        
        if id_value == "all": # 모든 데이터 조회
            query = f"SELECT * FROM {table_name}"
            cur.execute(query)
            return cur.fetchall()
        
        if isinstance(id_value, str): # id_value가 문자열인 경우, 해당하는 id로 변환
            query = "SELECT {table_name}_id FROM {table_name} WHERE {table_name}_name = %s"
            cur.execute(query, (id_value,))
            result = cur.fetchone()

            if result is None:
                raise NullPointerException
            else:
                id_value = result[0]

        query = f"SELECT * FROM {table_name} WHERE {table_name}_id = %s"
        cur.execute(query, (id_value,))
        return cur.fetchone()

    except psycopg2.ProgrammingError as exception: # table이 존재하지 않음
        print("입력한 테이블이 존재하지 않습니다.")
        conn.rollback()
        return False

    except psycopg2.IntegrityError as exception: # category table 예외 처리
        if table_name == "category":
            print("입력한 값이 이미 category 테이블에 존재합니다.")
        
        elif table_name == "product":
            print("입력한 값이 이미 product 테이블에 존재합니다.")
        
        elif table_name == "product_detail":
            print("입력한 값이 이미 product_detail 테이블에 존재합니다.")

        conn.rollback()
        return False

    except NullPointerException as exception: # product table 예외 처리
        if table_name == "category":
            print("입력한 값이 category 테이블에 존재하지 않습니다.")

        elif table_name == "product":
            print("입력한 값이 product 테이블에 존재하지 않습니다.")
        
        elif table_name == "product_detail":
            print("입력한 값이 product_detail 테이블에 존재하지 않습니다.")

        conn.rollback()
        return False
    
    except psycopg2.DataError as exception:
        print("입력한 id(프라이머리 키)가 유효한 범위를 초과했습니다.")
        conn.rollback()
        return False
	  
    except Exception as exception:
        print(f"Exception: {exception}")
        conn.rollback()
        return False
        
    finally:
        cur.close()


# 사진 정보 저장 함수
def save_image(conn, product_id, image_path):
    try:
        cur = conn.cursor()
        if isinstance(product_id, str):
            query = "SELECT product_id FROM product WHERE product_name = %s"
            cur.execute(query, (product_id,))
            result = cur.fetchone()

            if result is None:
                raise NullPointerException
            else:
                product_id = result[0]  # product_id 할당
        
        query = "INSERT INTO product_image (product_id, image_path) VALUES (%s, %s)"

        query = "UPDATE product SET image = %s WHERE product_id = %s"
        cur.execute(query, (image_path, product_id))
        conn.commit()
        return True

    except NullPointerException as exception:
        print("입력한 값이 존재하지 않습니다.")
        conn.rollback()
        return False
    
    except Exception as exception:
        print(f"Exception: {exception}")
        conn.rollback()
        return False
    
    finally:
        cur.close()

# 사진 정보 불러오기 함수
def load_image(conn, product_id):
    try:
        cur = conn.cursor()

        # product_identifier가 문자열이면 제품명을 통해 product_id 조회
        if isinstance(product_id, str):
            query = "SELECT product_id FROM product WHERE product_name = %s"
            cur.execute(query, (product_id,))
            result = cur.fetchone()

            if result is None:
                raise NullPointerException
            else:
                product_id = result[0]

        # product_id로 이미지 경로 조회
        query = "SELECT image FROM product WHERE product_id = %s"
        cur.execute(query, (product_id,))
        result = cur.fetchone()

        if result is None or result[0] is None:
            print("이미지 경로가 존재하지 않거나 제품이 없습니다.")
            return None
        else:
            return result[0]  # 이미지 경로 반환
        
    except NullPointerException as exception:
        print("입력한 값이 존재하지 않습니다.")
        return None


    except Exception as exception:
        print(f"Exception: {exception}")
        return None

    finally:
        cur.close()

# ---------------------------- 구분선 ----------------------------

# 사용자 정의 예외 클래스

# 테이블이 존재하지 않음
class TableSortException(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "입력한 테이블이 존재하지 않습니다."

# 입력한 값이 존재하지 않음
class NullPointerException(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "입력한 값이 존재하지 않습니다."

# 데이터베이스 연결 함수
def db_connect(_dbname, _user, _password, _host, _port):
    conn = psycopg2.connect(dbname=_dbname, user=_user, password=_password, host=_host, port=_port)
    return conn

# 테이블 정렬 함수 
def table_sort(conn, table_name, standard_column="id"):
    try:
        cur = conn.cursor()
        standard_column = f"{table_name}_{standard_column}"

        cur.execute(f"SELECT * FROM {table_name} ORDER BY {standard_column}")
        return True
    
    except Exception as exception:
        print(f"Exception: {exception}")
        conn.rollback()
        return False
    
    finally:
        cur.close()

# 카테고리 테이블 정보 추가 함수
def insert_category(cur, category_name):
    query = "INSERT INTO category (category_name) VALUES (%s)"
    cur.execute(query, (category_name,))
    return True


# 제품 테이블 정보 추가 함수
def insert_product(cur, category_id, product_name, price):
    # 입력한 값이 문자열인 경우, 해당하는 category_id를 찾아서 그 값을 찾음
    if isinstance(category_id, str):
        query = "SELECT category_id FROM category WHERE category_name = %s"
        cur.execute(query, (category_id,))
        result = cur.fetchone()

        if result is not None:
            category_id = result[0]
        else:
            raise NullPointerException

    query = "INSERT INTO product (category_id, product_name, price) VALUES (%s, %s, %s)"
    cur.execute(query, (category_id, product_name, price))
    return True


# product_detail 테이블에 데이터 삽입
def insert_product_detail(cur, product_id, product_description):
    if isinstance(product_id, str):
        query = "SELECT product_id FROM product WHERE product_name = %s"
        cur.execute(query, (product_id,))
        result = cur.fetchone()

        if result is not None:
            product_id = result[0]
        else:
            raise NullPointerException

    query = "INSERT INTO product_detail (product_id, product_description) VALUES (%s, %s)"
    cur.execute(query, (product_id, product_description))
    return True


# 메인 함수(출력 예시)
def main():
    # 데이터베이스 연결 예시
    host = "127.0.0.1"
    dbname = "rag_db"
    user = "postgres"
    password = "1234"
    port = "5432"

    # 데이터베이스 연결 함수
    conn = db_connect(dbname, user, password, host, port)

    # 테이블 정보 추가 예시 (table_name, value_id, value_name, value_price)
    insert_table(conn, "category", "취미") 

    insert_table(conn, "product", "전자", "iPhone 16", 1000) # category_name를 직접 입력해도 자동으로 변환됨

    insert_table(conn, "product", 2, "iPhone 16 Pro", 1500) # category_id를 직접 입력해도 변환됨 

    insert_table(conn, "product_detail", "iPhone 16", "A18 프로세서 탑재") # product_name을 입력해도 자동으로 변환됨

    insert_table(conn, "product_detail", 18, "A18 Pro 프로세서 탑재") # product_id를 입력해도 변환됨

    # 테이블 정보 수정 예시 (table_name, value_id, value_name, value_price)
    modify_table(conn, "product", 18, "S24 Ultra", 1500) # product_name을 입력해도 자동으로 변환됨

    # 테이블 정보 조회 예시 (table_name, value_id) -> return값은 쿼리 결과(튜플)
    # 전체 값 조회
    categories = search_table(conn, "category", "all")
    for category in categories:  
        print(category)

    # 부분 값 조회
    products = [search_table(conn, "product", "S24 Ultra"), search_table(conn, "product", 13)] 
    # product를 입력해도 자동 변환
    # product_id를 입력해도 변환

    for product in products:
        print(product)
    
    # 테이블 정보 삭제 예시 (table_name, value_id, force_delete)
    delete_table(conn, "category", "취미") # category 삭제시 경고 메시지가 출력됨
    delete_table(conn, "product", "iPhone 16", True) # 경고 무시하고 삭제 (마지막 매개변수를 True로 변경)
    delete_table(conn, "product_detail", 15) # product_detail 삭제 (경고 메시지가 출력되지 않음)

    # 이미지 정보 저장 및 불러오기 예시
    insert_table(conn, "product", 2, "S24 Ultra", 1500)
    save_image(conn, "S24 Ultra", "C:\\Users\\USER\\Desktop\\s24ultra")
    image_path = load_image(conn, "S24 Ultra")
    print(image_path)
    
    conn.close()  # 데이터베이스 연결 닫기
    

if __name__ == '__main__':
    main()