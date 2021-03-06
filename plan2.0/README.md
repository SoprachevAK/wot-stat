# WotStat 2.0 (WIP)

Тут расписаны планы на версию мода 1.0 (Название кликбейт. Сейчас версия 0.0.8)\
Воспринимать как дизайн документ

**Разработка новой версии мода в ветке v1.0.0.0**

## Описание 
Новая версия мода будет записывать различные события внутри боя, на сайте в [статистике](https://wotstat.soprachev.com) можно будет посмотреть график событий от времени боя по боям.

События отправляют пачками (массивами) раз в 5 секунд

## События
Единица статистики: Бой\
Каждый бой состоит из событий, всегда начинается с события кнопка **"Загрузка боя завершена"**, заканчивается событием **"РЕЗУЛЬТАТ БОЯ"**\
Каждое событие имеет время и имя (EventName)

Тегом [v1] обозначаются события второстепенной важности, [v2] -- события на следующее обновление.

## Порядок событий
* Начало боя (последовательно)
  * [DEP] [Вход в очередь боя](#Вход-в-очередь-боя)
  * [DEP] [Бой сформирован](#Бой-сформирован)
  * [Загрузка боя завершена](#Загрузка-боя-завершена)
* Во время боя (в любом порядке)
  * [Совершен выстрел](#Совершен-выстрел)
  * [v1] Выстрел повлиял на противника
  * [v1] Уничтожен противник
  * [v1] Нанесён урон
  * [v1] Выстрел повлиял на свой танк
  * [v1] Получен урон
  * [v1] Свой танк уничтожен
  * [v1] Засвечен танк противника 
  * [v2] Изменено время на таймере (отлично от стандартного тика)
  * [v2] Получен ассист (оглушение/гусля/свет)
  * [v2] Переворот/утопление 
  * [v2] Смена танка для линии фронта
  * [v2] Сброс расходников для режимов где они есть 
* Завершение боя
  * [v1] Выход в ангар (по кнопке/автоматом)
  * [v1] [Результат боя (или недоступен)](#Результат-боя)

## События
### Вход в очередь боя

Срабатывает в момент входа в очередь (вне зависимости от взвода)\
Хук: [*тут должна быть ссылка на функцию исходника, пока что не нашел её*]

|  Поле     | Тип       | Описание  |
| -         | -         | -         |
| EventName | String    | == 'DoBattleQueue' |
| Date      | DateTime  | Время нажатия кнопки "в бой" |
| Squad     | Boolean   | Является ли вход в бой в составе взвода |
| Own       | Boolean   | Является ли вход в бой результатом нажатия кнопки "в бой" |


### Бой сформирован

Срабатывает в момент начала загрузки боя (дублируются при перезаходе в игру)\
Хук: [PlayerAvatar.onEnterWorld](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/850513514625af4d2e001651fad8914c7d8f0623/source/res/scripts/client/Avatar.py#L511)

|  Поле       | Тип       | Описание          |
| -           | -         | -                 |
| EventName   | String    | == 'OnEnterWorld' |
| Date        | DateTime  | Время начала загрузки |

### Загрузка боя завершена

Срабатывает в момент завершения загрузки боя (дублируются при перезаходе в игру). В этот момент отправляются прошлые события.\
Хук: [PlayerAvatar.updateTargetingInfo](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/850513514625af4d2e001651fad8914c7d8f0623/source/res/scripts/client/Avatar.py#L1381)

В ответ на это событие сервер отправляет токен боя, который надо отправлять вместо со всеми следующими событиями

| Поле      | Тип     | Пример                  | Описание      | 
| -         | -       | -                       | -             |
| EventName | String  | == 'OnEndLoad'          |               |
| Date      | DateTime|                         | Время         |
| ArenaTag  | String  | 'spaces/07_lakeville'   | Тег карты     |
| ArenaID   | String  |                         | ??            |
| Base      | ??      |                         | База          | 
| PlayerName| String  |                         | Имя игрока            | 
| PlayerBDID| String  |                         | BDID игрока           | 
| PlayerClan| String  |                         | Тег клана игрока      | 
| TankTag   | String  | 'usa:A21_T14'           | Тег танка     | 
| TankType  | String  | 'LT'                    | Тег типа танка| 
| TankLevel | Number  | 1                       | Уровень танка |
| GunTag    | String  |                         | Тег пушки     |
| StartDis  | Number  |                         | Разброс пушки |
| SpawnPoint| Vector3 |                         | Координата своего танка |
| TimerToStart | Number |                       | Время до старта боя в секундах, после начала боя будет отрицательным   |
| BattleMode| String  | 'EPIC_RANDOM'           | Режим боя     |
| GameVersion| String | 'ru_1.14.0'             | Версия игры   |
| ModVersion | String | '1.0.0.0'               | Версия мода   |


### Совершен выстрел
Срабатывает в момент попадания выстрела куда либо

Хуки: 
* Получение координаты маркера (серверного) [PlayerAvatar.updateGunMarker](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/16d7d1357349de98d93613f11dfdcb81bacab1fe/source/res/scripts/client/Avatar.py#L1327)
* В момент перед выстрелом [PlayerAvatar.shoot](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/850513514625af4d2e001651fad8914c7d8f0623/source/res/scripts/client/Avatar.py#L1942)
* Отображение трассера [PlayerAvatar.showTracer](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/850513514625af4d2e001651fad8914c7d8f0623/source/res/scripts/client/Avatar.py#L1609)
* Отображение трассера [PlayerAvatar.showTracer](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/850513514625af4d2e001651fad8914c7d8f0623/source/res/scripts/client/Avatar.py#L1609)
* Получение точки попадания [PlayerAvatar.explodeProjectile](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/blob/16d7d1357349de98d93613f11dfdcb81bacab1fe/source/res/scripts/client/Avatar.py#L1560)



|  Поле       | Тип       | Описание                          |
| -           | -         | -                                 |
| EventName   | String    | == 'OnShot'                       |
| Date        | DateTime  | Время нажатия лкм перед выстрелом |
| Token       | String    | Токен боя                         |
| ServerMarkerPoint | Vector3   | Координата серверного маркера                |
| ClientMarkerPoint | Vector3   | Координата клиентского маркера               |
| ServerShotDispersion  | Number| Тангенс **серверного** угла разброса в момент выстрела с учётом всех модификаторов (осадный режим, перки, оглушение) |
| ClientShotDispersion  | Number| Тангенс **клиентского** угла разброса в момент выстрела с учётом всех модификаторов (осадный режим, перки, оглушение) |
| HitPoint    | Vector3   | Координата попадание              |
| GunPoint    | Vector3   | Координата опорной точки орудия   |
| TracerStart | Vector3   | Координата начала трассера        |
| TracerVel   | Vector3   | Скорость снаряда в точке старта трассера |
| Gravity     | Number    | Гравитация снаряда                |
| BattleDispersion| Number| Разброс на момент старта боя, с учётом перков, но без учёта временных модификаторов |
| GunDispersion   | Number| Разброс по ТТХ (без учёта любых модификаторов)  |
| ShellTag    | String    | Тег снаряда                       |
| ServerAim   | Boolean   | Включен ли серверный прицел       |
| AutoAim     | Boolean   | Включен ли автоприцел             |
| Ping        | Number    | Пинг                              |
| ShotID      | Number    | Уникальный **внутри боя** ID выстрела           |



### Результат боя

Завершающие событие любого боя. Отправляется в момент получения подробного результата, или автоматически добавляется сервером спустя 60 минут после начала боя.

Хук: [*тут должна быть ссылка на функцию исходника, пока что не искал её*] что то типа OnBattleResult

|  Поле     | Тип       | Описание  |
| -         | -         | -         |
| EventName | String    | == 'OnBattleResult' |
| Status    | String    | Статус завершения боя (успешен, недоступен или завершен сервером по истечению времени) |
| Result    | String?   | Результат боя (Победа, поражение, успех или иное в зависимости от режима боя) |
| XP        | Number?   | Полученный опыт за бой |
| Money     | Number?   | Полученные кредиты за бой |

