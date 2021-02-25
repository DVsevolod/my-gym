**Backend сервер для сайта спортивного зала My-Gym.**

Реализовано:
- Регистрация
- Аутентефикация (jwt-токен)
- Авторизация
- Модели: Пользователь (базовая), профиль Клиента, профиль Работника, Сервис, Абонемент, Должность.
- CRUD
- Swagger.

Backend-сервер для сайта спортивного зала My-Gym. Пользователи делятся на 2 типа: клиент и работник спортзала. Модель клиента имеет поле абонемент, в котором указан срок дейстия абонемента и дата его обновления, плюс список используемых сервисов. Работник зала имеет поля должность  и список клиентов, которых он обслуживает. 

Для клиента реализована возможность просмотра доступных сервисов. В функционал работника входит возможность просмотра всех клиентов/работников с фильтрация обоих профилей по дате создания профиля, а также:
- У клиентов - фильтр по истечению срока подписки, по используемым сервисам.
- У работников - фильтр по конкретному клиенту или вхождению в список, по должности.

При регистрации создается кастомный User имеющий поле role, которая в дальнейшем используется для определения разрешений. Далее, при помощи созданного User создается  профиль: Client или Staff.

Staff может создавать, обновлять, удалять и просматривать: Должности, Сервисы. Абонементы можно только просмотреть.

Документация написана при помощи SwaggerUI и доступна по url /swagger/.

Деплой:

Проект залит на Docker Hub, устанавливается при помощи команды:

    docker pull vdanilintest/my-gym-backend-v1

Запуск:

    docker run --rm --name my_gym -p 8080:8080 vdanilintest/my-gym-backend-v1

**Swagger (url: /swagger/).**

Для проверки разрешений необходимо авторизоваться в Swagger при помощи токена. Токен вернется при вхождении в систему через Postman. 

Для упрощения проверки функциональности можно использовать готовые профили.

**Superuser**

    email: admin@admin.com
    password: admin
    
**Client**

    email: anton@client.com
    password: 12345678
    
**Staff**

    email: srj@kach.com
    password: 87654321

При использовании Swagger токен необходимо использовать по образцу:

![token_swagger](https://github.com/DVsevolod/my-gym/blob/main/img/token.png)

При использовании Postman токен необходимо вставить в header по образцу:

![token_postman](https://github.com/DVsevolod/my-gym/blob/main/img/postman.png)

Приложение auth:

![auth](https://github.com/DVsevolod/my-gym/blob/main/img/auth.png)

Приложение my_gym:

Модель User:

![users](https://github.com/DVsevolod/my-gym/blob/main/img/users.png)

Модель Service:

![services](https://github.com/DVsevolod/my-gym/blob/main/img/services.png)

Модель Subscription:

![sub](https://github.com/DVsevolod/my-gym/blob/main/img/sub.png)

Модель Position:

![position](https://github.com/DVsevolod/my-gym/blob/main/img/positions.png)
