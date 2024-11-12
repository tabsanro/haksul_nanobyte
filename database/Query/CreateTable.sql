-- 테이블 초기화 및 생성
DROP TABLE IF EXISTS product_detail;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS category; 


-- 카테고리 테이블 생성
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    UNIQUE (category_name)
);

-- 제품명 테이블 생성 및 이는 각 카테고리를 참조
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL, -- 카테고리 코드
    FOREIGN KEY (category_id) REFERENCES category (category_id) ON DELETE CASCADE,
    product_name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL DEFAULT 0, -- 가격
    image TEXT, -- 이미지
    UNIQUE (product_id, product_name)
);

-- 상세정보 테이블 생성 및 이는 각 제품명을 참조
CREATE TABLE product_detail (
    product_detail_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL, -- 제품 코드
    FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE,
    product_description VARCHAR(500) NOT NULL, -- 상세설명
    UNIQUE (product_id, product_description)
);