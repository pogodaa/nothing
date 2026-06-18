PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_article TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_article) REFERENCES products(article)
        );
INSERT INTO "order_items" VALUES(1,1,'A112T4',2);
INSERT INTO "order_items" VALUES(2,1,'G843H5',2);
INSERT INTO "order_items" VALUES(3,2,'G843H5',1);
INSERT INTO "order_items" VALUES(4,2,'A112T4',1);
INSERT INTO "order_items" VALUES(5,3,'D325D4',10);
INSERT INTO "order_items" VALUES(6,3,'S432T5',10);
INSERT INTO "order_items" VALUES(7,4,'F325D4',5);
INSERT INTO "order_items" VALUES(8,4,'D325D4',4);
INSERT INTO "order_items" VALUES(9,5,'G432G6',20);
INSERT INTO "order_items" VALUES(10,5,'H542F5',20);
INSERT INTO "order_items" VALUES(11,6,'A112T4',2);
INSERT INTO "order_items" VALUES(12,6,'G843H5',2);
INSERT INTO "order_items" VALUES(13,7,'C346F5',3);
INSERT INTO "order_items" VALUES(14,7,'F256G6',3);
INSERT INTO "order_items" VALUES(15,8,'F325D4',1);
INSERT INTO "order_items" VALUES(16,8,'G432G6',1);
INSERT INTO "order_items" VALUES(17,9,'J532V5',5);
INSERT INTO "order_items" VALUES(18,9,'F256G6',1);
INSERT INTO "order_items" VALUES(19,10,'F256G6',5);
INSERT INTO "order_items" VALUES(20,10,'J532V5',5);
CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            articles_text TEXT NOT NULL,
            order_date TEXT,
            delivery_date TEXT,
            pickup_point_id INTEGER,
            client_name TEXT,
            pickup_code INTEGER,
            status TEXT,
            FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id)
        );
INSERT INTO "orders" VALUES(1,'A112T4, 2, G843H5, 2','2023-02-27','2023-04-20',1,'Степанов Михаил Артёмович',901,'Новый');
INSERT INTO "orders" VALUES(2,'G843H5, 1, A112T4, 1','2022-09-28','2023-04-21',11,'Никифорова Весения Николаевна',902,'Новый');
INSERT INTO "orders" VALUES(3,'D325D4, 10, S432T5, 10','2023-03-21','2023-04-22',2,'Сазонов Руслан Германович',903,'Новый');
INSERT INTO "orders" VALUES(4,'F325D4, 5, D325D4, 4','2023-02-20','2023-04-23',11,'Одинцов Серафим Артёмович',904,'Завершен');
INSERT INTO "orders" VALUES(5,'G432G6, 20, H542F5, 20','2023-03-17','2023-04-24',2,'Степанов Михаил Артёмович',905,'Завершен');
INSERT INTO "orders" VALUES(6,'A112T4, 2, G843H5, 2','2023-03-01','2023-04-25',15,'Никифорова Весения Николаевна',906,'Завершен');
INSERT INTO "orders" VALUES(7,'C346F5, 3, F256G6, 3','30.02.2023','2023-04-26',3,'Сазонов Руслан Германович',907,'Завершен');
INSERT INTO "orders" VALUES(8,'F325D4, 1, G432G6, 1','2023-03-31','2023-04-27',19,'Одинцов Серафим Артёмович',908,'Новый');
INSERT INTO "orders" VALUES(9,'J532V5, 5, F256G6, 1','2023-04-02','2023-04-28',5,'Степанов Михаил Артёмович',909,'Новый');
INSERT INTO "orders" VALUES(10,'F256G6, 5, J532V5, 5','2023-04-03','2023-04-29',19,'Степанов Михаил Артёмович',910,'Новый');
CREATE TABLE pickup_points (
            id INTEGER PRIMARY KEY,
            address TEXT NOT NULL
        );
INSERT INTO "pickup_points" VALUES(1,'420151, г. Лесной, ул. Вишневая, 32');
INSERT INTO "pickup_points" VALUES(2,'125061, г. Лесной, ул. Подгорная, 8');
INSERT INTO "pickup_points" VALUES(3,'630370, г. Лесной, ул. Шоссейная, 24');
INSERT INTO "pickup_points" VALUES(4,'400562, г. Лесной, ул. Зеленая, 32');
INSERT INTO "pickup_points" VALUES(5,'614510, г. Лесной, ул. Маяковского, 47');
INSERT INTO "pickup_points" VALUES(6,'410542, г. Лесной, ул. Светлая, 46');
INSERT INTO "pickup_points" VALUES(7,'620839, г. Лесной, ул. Цветочная, 8');
INSERT INTO "pickup_points" VALUES(8,'443890, г. Лесной, ул. Коммунистическая, 1');
INSERT INTO "pickup_points" VALUES(9,'603379, г. Лесной, ул. Спортивная, 46');
INSERT INTO "pickup_points" VALUES(10,'603721, г. Лесной, ул. Гоголя, 41');
INSERT INTO "pickup_points" VALUES(11,'410172, г. Лесной, ул. Северная, 13');
INSERT INTO "pickup_points" VALUES(12,'614611, г. Лесной, ул. Молодежная, 50');
INSERT INTO "pickup_points" VALUES(13,'454311, г.Лесной, ул. Новая, 19');
INSERT INTO "pickup_points" VALUES(14,'660007, г.Лесной, ул. Октябрьская, 19');
INSERT INTO "pickup_points" VALUES(15,'603036, г. Лесной, ул. Садовая, 4');
INSERT INTO "pickup_points" VALUES(16,'394060, г.Лесной, ул. Фрунзе, 43');
INSERT INTO "pickup_points" VALUES(17,'410661, г. Лесной, ул. Школьная, 50');
INSERT INTO "pickup_points" VALUES(18,'625590, г. Лесной, ул. Коммунистическая, 20');
INSERT INTO "pickup_points" VALUES(19,'625683, г. Лесной, ул. 8 Марта');
INSERT INTO "pickup_points" VALUES(20,'450983, г.Лесной, ул. Комсомольская, 26');
INSERT INTO "pickup_points" VALUES(21,'394782, г. Лесной, ул. Чехова, 3');
INSERT INTO "pickup_points" VALUES(22,'603002, г. Лесной, ул. Дзержинского, 28');
INSERT INTO "pickup_points" VALUES(23,'450558, г. Лесной, ул. Набережная, 30');
INSERT INTO "pickup_points" VALUES(24,'344288, г. Лесной, ул. Чехова, 1');
INSERT INTO "pickup_points" VALUES(25,'614164, г.Лесной,  ул. Степная, 30');
INSERT INTO "pickup_points" VALUES(26,'394242, г. Лесной, ул. Коммунистическая, 43');
INSERT INTO "pickup_points" VALUES(27,'660540, г. Лесной, ул. Солнечная, 25');
INSERT INTO "pickup_points" VALUES(28,'125837, г. Лесной, ул. Шоссейная, 40');
INSERT INTO "pickup_points" VALUES(29,'125703, г. Лесной, ул. Партизанская, 49');
INSERT INTO "pickup_points" VALUES(30,'625283, г. Лесной, ул. Победы, 46');
INSERT INTO "pickup_points" VALUES(31,'614753, г. Лесной, ул. Полевая, 35');
INSERT INTO "pickup_points" VALUES(32,'426030, г. Лесной, ул. Маяковского, 44');
INSERT INTO "pickup_points" VALUES(33,'450375, г. Лесной ул. Клубная, 44');
INSERT INTO "pickup_points" VALUES(34,'625560, г. Лесной, ул. Некрасова, 12');
INSERT INTO "pickup_points" VALUES(35,'630201, г. Лесной, ул. Комсомольская, 17');
INSERT INTO "pickup_points" VALUES(36,'190949, г. Лесной, ул. Мичурина, 26');
CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            unit TEXT,
            price REAL NOT NULL CHECK(price >= 0),
            supplier TEXT,
            manufacturer TEXT,
            category TEXT,
            discount REAL DEFAULT 0 CHECK(discount >= 0),
            quantity INTEGER DEFAULT 0 CHECK(quantity >= 0),
            description TEXT,
            photo_path TEXT
        );
INSERT INTO "products" VALUES(1,'A112T4','Велосипед взрослый горный Slash Stream 27.5 колеса (2025) 17" Черный (162-172 см)','шт.',19775.0,'ВелоСтрана','Slash','Велосипед взрослый горный',30.0,15,'Горный велосипед Slash Stream 27.5 (2025) – легкий и надежный компаньон для поездок по пересеченной местности. Мощные шатуны интенсивно передают усилия мышц на вал каретки.','import/1.JPG');
INSERT INTO "products" VALUES(2,'G843H5','Велосипед взрослый горный Slash Stream 27.5 колеса (2025) 19" Синий (172-182 см)','шт.',19791.0,'ВелоСтрана','Slash','Велосипед взрослый горный',30.0,9,'В комплектацию включены дисковые механические тормоза RPT DSC-310. Особый упор разработчики рамы данной модели сделали на увеличение прочности мест наибольшей нагрузки.','import/2.JPG');
INSERT INTO "products" VALUES(3,'D325D4','Велосипед городской подростковый серый','шт.',9919.0,'ЯндексМаркет','Shimano','Велосипед городской подростковый',5.0,12,'Городской подростковый велосипед - идеальный выбор для активного образа жизни!
Откройте для себя комфорт и свободу передвижения с нашим стильным городским велосипедом.','import/3.JPG');
INSERT INTO "products" VALUES(4,'S432T5','Велосипед Skill Bike 3051, городской, 21 скорость, сталь, 29" колеса, черно-красный','шт.',16442.0,'Скилс','Skill bike','Велосипед городской взрослый',15.0,15,'SKILL BIKE модель 3051 - горный велосипед на спицах, обеспечивающий уверенную и комфортную езду как по городским улицам, так и по горной местности.','import/4.JPG');
INSERT INTO "products" VALUES(5,'F325D4','Велосипед Skillbike 3052, горный, складной, рама 17 дюймов, колеса 26 дюймов, 21 скорость','шт.',17985.0,'Скилс','Skill bike','Велосипед взрослый горный',18.0,50,'SKILL BIKE модель 3052 - велосипед складной, предназначен для тех, кто ценит комфорт, стиль и максимальную мобильность. Горный велосипед легко помещается в багажник и идеально подходит для активных поездок в городской суете.','import/5.JPG');
INSERT INTO "products" VALUES(6,'G432G6','Велосипед Skill Bike 3053, горный, двухподвесный, рама 17 дюймов, колеса 26 дюймов, 21 скорость','шт.',17621.0,'Скилс','Skill bike','Велосипед взрослый горный',20.0,0,'SKILL BIKE модель 3053 - горный велосипед на литых дисках, имеет амортизаторы как на переднем, так и на заднем колесе.','import/6.JPG');
INSERT INTO "products" VALUES(7,'H542F5','Велосипед MILANO M300, горный, для взрослых, 26", 7 скоростей','шт.',13509.0,'ПерспективаГрупп','NEXT','Велосипед взрослый горный',4.0,5,'Горный велосипед MILANO M300 с диаметром колес 26 дюйма подойдет для подростков и взрослых, без усилий позволит преодолевать любые непроходимые каменистые поверхности и зоны бездорожья.','import/7.JPG');
INSERT INTO "products" VALUES(8,'C346F5','Горный велосипед скоростной, колёса 24", рама - 14", черно-красный','шт.',15212.0,'ПерспективаГрупп','Aero','Велосипед детский горный',5.0,4,'Горный велосипед – это надежный и стильный выбор для любителей активного отдыха. Удобное седло из искусственной кожи и наличие подножки добавляют удобства во время поездок.','import/8.JPG');
INSERT INTO "products" VALUES(9,'F256G6','26" Велосипед Fizard, 15" алюминий, дисковые тормоза, 21 скорость, серый','шт.',15126.0,'ПерспективаГрупп','Fizard','Велосипед детский горный',25.0,3,'Горный велосипед Fizard — надёжный универсальный маунтинбайк для города и бездорожья.','import/9.JPG');
INSERT INTO "products" VALUES(10,'J532V5','Велосипед двухколесный детский 14 дюймов, со светящимися колесами, черный','шт.',6417.0,'kari','kari','Велосипед детский городской',8.0,6,'Велосипед двухколесный детский 14 дюймов от Kari - это надежный и безопасный транспорт для вашего ребенка.','import/picture.png');
CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
INSERT INTO "users" VALUES(1,'Администратор','Никифорова Весения Николаевна','94d5ous@gmail.com','uzWC67');
INSERT INTO "users" VALUES(2,'Администратор','Сазонов Руслан Германович','uth4iz@mail.com','2L6KZG');
INSERT INTO "users" VALUES(3,'Администратор','Одинцов Серафим Артёмович','5d4zbu@tutanota.com','rwVDh9');
INSERT INTO "users" VALUES(4,'Менеджер','Ситдикова Елена Анатольевна','ptec8ym@yahoo.com','LdNyos');
INSERT INTO "users" VALUES(5,'Менеджер','Ворсин Петр Евгеньевич','1qz4kw@mail.com','gynQMT');
INSERT INTO "users" VALUES(6,'Менеджер','Старикова Елена Павловна','4np6se@mail.com','AtnDjr');
INSERT INTO "users" VALUES(7,'Авторизированный клиент','Никифорова Анна Семеновна','yzls62@outlook.com','JlFRCZ');
INSERT INTO "users" VALUES(8,'Авторизированный клиент','Стелина Евгения Петровна','1diph5e@tutanota.com','8ntwUp');
INSERT INTO "users" VALUES(9,'Авторизированный клиент','Михайлюк Анна Вячеславовна','tjde7c@yahoo.com','YOyhfR');
INSERT INTO "users" VALUES(10,'Авторизированный клиент','Степанов Михаил Артёмович','wpmrc3do@tutanota.com','RSbvHv');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',10);
INSERT INTO "sqlite_sequence" VALUES('products',10);
INSERT INTO "sqlite_sequence" VALUES('order_items',20);
COMMIT;
PRAGMA foreign_keys = ON;
