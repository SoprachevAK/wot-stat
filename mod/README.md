# Мод
В этом разделе находится исходный код мода для сбора статистики. От релизной версии он отличается файлом wot_stat/common/crypto.py, сейчас в нём расположена заглушка, релизная версия кодирует отправляемый на сервер json, дабы усложнить жизнь желающим заспамить сервер фейковыми сообщениями.

## Структура 1.0.0.0
Задача [eventLogger](wotstat/res/scripts/client/gui/mods/wot_stat/logger/eventLogger.py) -- создавать события [events](wotstat/res/scripts/client/gui/mods/wot_stat/logger/events.py) и добавлять их в [battleEventSession](wotstat/res/scripts/client/gui/mods/wot_stat/logger/battleEventSession.py).

[BattleEventSession](wotstat/wotstat/res/scripts/client/gui/mods/wot_stat/logger/battleEventSession.py) группирует события и раз в N=5 секунд отправляет их на сервер. Каждый бой создаётся новый экземпляр `BattleEventSession(Events.OnEndLoad())`, все события внутри этого боя отправляют через этот экземпляр. Экземпляр завершает своё существование событием `Events.OnBattleResult()`.

Все остальные файлы служебные и не выполняют ключевой роли. 

## Редактирование через PyCharm
Для корректной подсветки синтаксиса в IDE необходимы зависимости танков. 

1. Склонировать репозиторий с подмодулями (`git clone --recursive https://github.com/SoprachevAK/wot-stat.git`)
   * **WorldOfTanks-Decompiled** - исходный код клиента танков
   * **BigWorldPlaceholder** - заглушки функций библиотеки движка, объявлены только те, которые были нужны мне
2. Запустить Zip-Unpacker.exe для исправления регистра названия файлов 
3. Открыть текущую директорию через PyCharm (*File->Open*)
4. Отметить следующие папки как корень исходников (*ПКМ -> Mark Directory as -> Sources Root*)
   * `/WorldOfTanks-Decompiled/source/res/scripts/client`
   * `/WorldOfTanks-Decompiled/source/res/scripts/common`
   * `/BigWorldPlaceholder`
5. Готово. Теперь в IDE будет работать подсветка синтаксиса и подсказка кода.

## Сборка мода
1. С помощью [PjOrion](https://koreanrandom.com/forum/topic/15280-) скомпилировать (Run -> Compile py folder)
2. Запустить Zip-Packer.cmd для получения .wotmod файла

## Тестовый сервер
Мод сохраняет события на сервер, если вы хотите протестировать мод локально, вы можете запустить [тестовый сервер](https://github.com/SoprachevAK/wot-stat/tree/main/mod/serverPlaceholder) на NodeJS

1. В папке `World_of_Tanks/mods/configs/wot_stat` создать текстовый файл `config.cfg`, в который прописать `{"eventURL": "http://localhost:5000/sendEvent"}`
2. Запустить serverPlaceholder
3. Запустить танки
4. Готово. Теперь мод будет отправлять события на локальный сервер. Их можно посмотреть в консоле сервера. 
