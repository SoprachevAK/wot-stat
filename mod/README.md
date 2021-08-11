# Мод
В этом разделе находится исходный код мода для сбора статистики. От релизной версии он отличается файлом wot_stat/crypto.py, сейчас в нём расположена заглушка, релизная версия кодирует отправляемый на сервер json, дабы усложнить жизнь желающим заспамить сервер фейковыми сообщениями.

## Редактирование через PyCharm
1. Склонировать в текущую директорию декомпилированный код [WOT](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled). (git clone https://github.com/StranikS-Scan/WorldOfTanks-Decompiled.git)
2. Открыть текущую директорию через PyCharm (File->Open)
3. ПКМ -> Mark Directory as -> Sources Root по папкам
* /WorldOfTanks-Decompiled/source/res/scripts/client
* /WorldOfTanks-Decompiled/source/res/scripts/common
* /bigworld
4. Готово. Теперь в IDE будет работать подсветка синтаксиса и подсказка кода.

## Сборка мода
1. С помощью [PjOrion](https://koreanrandom.com/forum/topic/15280-) скомпилировать (Run -> Compile py folder)
2. Запустить Zip-Packer.cmd для получения .wotmod файла