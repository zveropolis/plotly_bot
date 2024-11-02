import os
import uuid
from dataclasses import dataclass

import aiofiles
import pyqrcode
from pytils.numeral import get_plural

from core.config import settings
from core.path import PATH
from db.models import UserActivity, UserData, WgConfig

me = {"я", "мои данные", "данные", "конфиги", "мои конфиги", "config", "подключения"}
yes = {"yes", "y", "da", "да"}
no = {"no", "n", "нет"}

only_admin = "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."

DB_ERROR = "Ошибка подключения к БД. Обратитесь к администратору."
WG_ERROR = "Ошибка подключения к серверу wireguard. Обратитесь к администратору."
YOO_ERROR = "Ошибка подключения к серверу yoomoney. Попробуйте еще раз позже"
UNPAY = "Функционал создания конфигураций заблокирован. Действующие конфигурации заблокированы. Для разблокировки оплатите подписку."

rates = {0.3: "Пробный", 1: "Базовый", 2.5: "Расширенный", 5: "Люкс"}

BOT_INFO = """
🌐 Добро пожаловать в наш VPN-сервис на базе WireGuard!

Наш сервис предоставляет надежное и быстрое решение для обеспечения вашей онлайн-безопасности и конфиденциальности. Вот как он работает:

🔒 Безопасное соединение: WireGuard использует современные криптографические протоколы для создания защищенного канала связи между вашим устройством и интернетом. Это означает, что ваши данные остаются в безопасности и недоступны для посторонних.

⚡ Высокая скорость: Благодаря своей легковесной архитектуре, WireGuard обеспечивает высокую скорость соединения, что позволяет вам наслаждаться потоковым видео, играми и другими онлайн-активностями без задержек.

🤖 Управление через чат-бота: Мы сделали процесс управления вашим VPN-сервисом максимально удобным. С помощью нашего чат-бота вы можете легко подключать себе VPN, а также получать помощь и советы по использованию сервиса.

🔧 Простота использования: Наша платформа разработана с учетом удобства пользователей. Вы сможете быстро настроить соединение и начать пользоваться всеми преимуществами VPN без лишних усилий.

Присоединяйтесь к нам и обеспечьте свою онлайн-безопасность уже сегодня! Если у вас есть вопросы, не стесняйтесь обращаться к нашему чат-боту — он всегда готов помочь!
"""

BOT_STEPS = [
    """1. <b>Запустите бота</b>: 
    
    - Если вы только что начали, введите команду /start , чтобы запустить или перезагрузить бота (🔘кнопка 'Перезагрузка').""",
    """2. <b>Создайте аккаунт</b>: 
    
    - Для начала работы с сервисом вам нужно зарегистрироваться. Введите команду `/reg` (либо воспользуйтесь соответствующей кнопкой в чате), чтобы создать аккаунт.""",
    """3. <b>Пополните баланс</b>: 
    
    - Далее вам необходимо пополнить баланс. Используйте команду `/sub` (🔘кнопка 'Подписка'), чтобы выбрать и купить тариф пользования.""",
    """4. <b>Создайте конфигурацию</b>: 
    
    - После пополнения баланса введите команду /create (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.""",
    """5. <b>Скачайте WireGuard</b>: 
    
    - Убедитесь, что у вас установлено приложение WireGuard. Вы можете скачать его на официальном сайте WireGuard (https://www.wireguard.com/install/), приложение работает на Windows, macOS, Linux, Android и iOS.""",
    """6. <b>Подключите конфигурацию</b>: 
    
    - После создания конфигурации получите ее (🔘кнопка 'Подключения') 
        📄 в текстовом виде (🔘кнопка 'TEXT'),
        
        📱 в виде qr-кода (🔘кнопка 'QR'),
        
        🗂️ или скачайте файл (🔘кнопка 'FILE'), 
        
и импортируйте ее в приложение WireGuard. Это позволит вам установить защищенное соединение. \n(Если вы не знаете как ипортировать конфигурацию, воспользуйтесь командой `/help` - 🔘'Помощь' и выберите 'Как мне настроить WireGuard?')""",
    """7. <b>Управление аккаунтом</b>:
    
    - Для доступа к основному функционалу вашего аккаунта используйте команду /account или /app, либо 🔘кнопку 'Статус'.
    - Если вам нужно временно приостановить использование сервиса, используйте /freeze (🔘'Заморозить аккаунт'), а для восстановления доступа — команду /recover (🔘'Разморозить аккаунт').""",
    """8. <b>Получите помощь</b>: 
    
    - Если у вас возникли вопросы, введите /help (🔘кнопка 'Помощь'), чтобы получить информацию о доступных командах и функциях.""",
    """9. <b>Дополнительные команды</b>:
    
    - Для получения списка всех команд введите /cmd .
    - Если вы администратор, используйте команду /admin для доступа к функционалу администратора.
    - Чтобы сообщить о баге, используйте /bug .
    - Для получения вашего Telegram ID введите /id .
    - Если хотите узнать время запуска бота, введите /time .""",
]

WG_STEPS = {
    "Windows": [
        """1. <b>Скачайте и установите WireGuard</b>:
    
    - Перейдите на официальный сайт WireGuard (https://www.wireguard.com/install/) и скачайте версию для Windows.
    - Установите приложение, следуя инструкциям на экране.""",
        """2. <b>Создайте конфигурационный файл</b>:
    
    - Пополнив баланс у чат-бота, введите команду `/create` (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.
    - В появившемя меню конфигурации (🔘кнопка 'Подключения') получите файл конфигурации (🔘кнопка 'FILE') либо создайте его самостоятельно:
    
        ~ Откройте текстовый редактор (например, Блокнот) и вставьте конфигурацию, которую вы получили от чат-бота (🔘кнопка 'TEXT').
        ~ Сохраните файл с расширением `.conf` , например, `my_vpn.conf` .""",
        """3. <b>Импортируйте конфигурацию в WireGuard</b>:
    
    - Откройте приложение WireGuard.
    - Нажмите на кнопку "Import tunnel from file" (Импортировать туннель из файла) и выберите созданный вами конфигурационный файл.""",
        """4. <b>Подключитесь к VPN</b>:
    
    - После импорта конфигурации вы увидите ваш туннель в списке. Нажмите на кнопку "Activate" (Подключить), чтобы подключиться к VPN.""",
        """5. <b>Проверьте подключение</b>:
    
    - Убедитесь, что ваше соединение активно. Вы можете проверить свой IP-адрес через любой онлайн-сервис для определения IP, чтобы убедиться, что вы подключены к VPN. (Например, https://2ip.ru/)""",
    ],
    "Linux": [
        """1. <b>Установите WireGuard</b>:
    
    - Перейдите на официальный сайт WireGuard (https://www.wireguard.com/install/) и найдите команду установки для вашего дистрибутива.
    - Откройте терминал.
    - Установите приложение, следуя инструкциям на сайте.""",
        """2. <b>Создайте конфигурационный файл</b>:

    - Пополнив баланс у чат-бота, введите команду `/create` (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.
    - В появившемя меню конфигурации (🔘кнопка 'Подключения') получите файл конфигурации (🔘кнопка 'FILE') либо создайте его самостоятельно:
    
        ~ Откройте текстовый редактор (например, `nano` или `vim` ) и создайте новый файл конфигурации. Например, `wg0.conf` .
        ~ Вставьте конфигурацию, которую вы получили от чат-бота. 
        ~ Сохраните файл и закройте текстовый редактор.
        ~ Переместите конфигурацию по адресу `/etc/wireguard/wg0.conf`""",
        """3. <b>Запустите WireGuard</b>:

    - Чтобы активировать VPN-соединение, выполните следующую команду:
    <pre>sudo wg-quick up wg0</pre>""",
        """4. <b>Проверьте подключение</b>:

    - Убедитесь, что ваше соединение активно, выполнив команду:
    <pre>sudo wg</pre>

    - Также вы можете проверить свой IP-адрес через любой онлайн-сервис для определения IP, чтобы убедиться, что вы подключены к VPN. (Например, https://2ip.ru/)""",
        """5. <b>Отключите WireGuard</b>:

    - Чтобы отключить VPN-соединение, выполните команду:
    <pre>sudo wg-quick down wg0</pre>""",
    ],
    "macOS": [
        """1. <b>Скачайте и установите приложение WireGuard</b>:

    - Откройте Mac App Store на вашем Mac.
    - Найдите приложение "WireGuard" и скачайте его (либо скачайте на официальном сайте WireGuard https://www.wireguard.com/install/).
    - Установите приложение, следуя инструкциям на экране.""",
        """2. <b>Создайте конфигурационный файл</b>:
        
    - Пополнив баланс у чат-бота, введите команду `/create` (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.
    - В появившемя меню конфигурации (🔘кнопка 'Подключения') получите файл конфигурации (🔘кнопка 'FILE') либо создайте его самостоятельно:
    
        ~ Откройте текстовый редактор (например, TextEdit).
        ~ Вставьте конфигурацию, которую вы получили от чат-бота. Пример конфигурации:
        ~ Сохраните файл с расширением  `.conf` , например,  `my_vpn.conf`.""",
        """3. <b>Импортируйте конфигурацию в WireGuard</b>:

    - Откройте приложение WireGuard.
    - Добавьте конфигурацию WireGuard, нажав кнопку «Импорт туннелей из файла...» или кнопку ✚ в нижней левой части окна приложения WireGuard и «Импорт туннелей из файла...».
    - Настройте автоподключение для локальной сети или Wi-Fi (для всех Wi-Fi подключений или какого-то отдельного по Вашему выбору) и нажмите «Сохранить». 
    - При добавлении новой конфигурации может появиться окно с запросом разрешения на добавление конфигураций VPN. Нажмите «Разрешить» для добавления новой конфигурации. """,
        """4. <b>Подключитесь к VPN</b>:

    - После успешного добавления конфигурации WireGuard для подключения к серверу нажмите «Подключен» в меню приложения на панели задач или «Подключение» (Activate) в программе WireGuard.  
    - В случае успешного подключения статус изменится на «Подключен» (Active).""",
        """2. <b>Проверьте подключение</b>:

    - Убедитесь, что ваше соединение активно. Вы можете проверить свой IP-адрес через любой онлайн-сервис для определения IP, чтобы убедиться, что вы подключены к VPN. (Например, https://2ip.ru/)""",
    ],
    "Android": [
        """1. <b>Скачайте и установите приложение WireGuard</b>:
    
    - Перейдите в Google Play Store на вашем устройстве.
    - Найдите приложение "WireGuard" и скачайте его (либо скачайте на официальном сайте WireGuard https://www.wireguard.com/install/).
    - Установите приложение, следуя инструкциям на экране.""",
        """2. <b>Создайте конфигурационный файл</b>:
        
    - Пополнив баланс у чат-бота, введите команду `/create` (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.
    - В появившемя меню конфигурации (🔘кнопка 'Подключения') получите файл конфигурации: 
        📄 в текстовом виде (🔘кнопка 'TEXT'),
        
        📱 в виде qr-кода (🔘кнопка 'QR'),
        
        🗂️ или скачайте файл (🔘кнопка 'FILE')""",
        """3. <b>Импортируйте конфигурацию в WireGuard</b>:
    
    - Откройте приложение WireGuard.
    - Нажмите на кнопку "Добавить туннель" (или значок ✚ в правом нижнем углу).
    - Выберите "Импорт из файла", "Сканировать QR-код", или "Создать с нуля"(для опытных) в зависимости от того, как вы сохранили конфигурацию.
    
    - Если вы выбрали "Импорт из файла", найдите и выберите ваш `.conf` файл. 
    - Если вы выбрали "Сканировать QR-код", отсканируйте его в чате с ботом.
    - Если вы выбрали "Создать с нуля", самостоятельно заполните все поля согласно полученной конфигурации.""",
        """4. <b>Подключитесь к VPN</b>:
    
    - После импорта конфигурации вы увидите ваш туннель в списке. Нажмите на переключатель рядом с названием туннеля, чтобы активировать VPN-соединение.""",
        """5. <b>Проверьте подключение</b>:
    
    - Убедитесь, что ваше соединение активно. Вы можете проверить свой IP-адрес через любой онлайн-сервис для определения IP, чтобы убедиться, что вы подключены к VPN. (Например, https://2ip.ru/)""",
    ],
    "iOS": [
        """1. <b>Скачайте и установите приложение WireGuard</b>:
    
    - Откройте App Store на вашем iPhone или iPad.
    - Найдите приложение "WireGuard" и скачайте его (либо скачайте на официальном сайте WireGuard https://www.wireguard.com/install/).
    - Установите приложение, следуя инструкциям на экране.""",
        """2. <b>Создайте конфигурационный файл</b>:
        
    - Пополнив баланс у чат-бота, введите команду `/create` (🔘кнопка 'Подключения'), чтобы создать конфигурацию WireGuard для вашего устройства.
    - В появившемя меню конфигурации (🔘кнопка 'Подключения') получите файл конфигурации: 
        📄 в текстовом виде (🔘кнопка 'TEXT'),
        
        📱 в виде qr-кода (🔘кнопка 'QR'),
        
        🗂️ или скачайте файл (🔘кнопка 'FILE')""",
        """3. <b>Импортируйте конфигурацию в WireGuard</b>:
    
    - Откройте приложение WireGuard.
    - Нажмите на кнопку "Добавить туннель" (или значок ✚ в правом верхнем углу).
    - Выберите "Импорт из файла", "Сканировать QR-код", или "Создать с нуля"(для опытных) в зависимости от того, как вы сохранили конфигурацию.
    
    - Если вы выбрали "Импорт из файла", найдите и выберите ваш `.conf` файл. 
    - Если вы выбрали "Сканировать QR-код", отсканируйте его в чате с ботом.
    - Если вы выбрали "Создать с нуля", самостоятельно заполните все поля согласно полученной конфигурации.""",
        """4. <b>Подключитесь к VPN</b>:
    
    - После импорта конфигурации вы увидите ваш туннель в списке. Нажмите на переключатель рядом с названием туннеля, чтобы активировать VPN-соединение.""",
        """5. <b>Проверьте подключение</b>:
    
    - Убедитесь, что ваше соединение активно. Вы можете проверить свой IP-адрес через любой онлайн-сервис для определения IP, чтобы убедиться, что вы подключены к VPN. (Например, https://2ip.ru/)""",
    ],
}

BOT_ERROR_STEP = [
    """1. <b>Проверьте подключение к интернету</b>:
    
    - Убедитесь, что ваше устройство подключено к интернету. Попробуйте открыть веб-сайт или использовать другое приложение, чтобы проверить соединение.""",
    """2. <b>Перезагрузите приложение WireGuard</b>:
    
    - Закройте приложение WireGuard и откройте его снова. Это может помочь устранить временные проблемы.""",
    """3. <b>Переподключитесь к VPN</b>:
    
    - Отключите VPN-соединение и снова подключитесь. Это может помочь восстановить стабильность соединения.""",
    """4. <b>Проверьте конфигурацию</b>:
    
    - Убедитесь, что вы используете правильную конфигурацию. Проверьте, что все ключи и адреса указаны корректно.""",
    """5. <b>Проверьте настройки брандмауэра</b>:
    
    - Убедитесь, что брандмауэр на вашем устройстве или роутере не блокирует соединение WireGuard. Возможно, потребуется настроить исключения.""",
    """6. <b>Обновите приложение</b>:
    
    - Проверьте, есть ли обновления для приложения WireGuard. Убедитесь, что вы используете последнюю версию.""",
    """7. <b>Перезагрузите устройство</b>:
    
    - Перезагрузите ваше устройство. Это может помочь устранить временные сбои в работе системы.""",
    """8. <b>Проверьте состояние сервиса</b>:
    
    - Убедитесь, что сервис WireGuard работает корректно. Если есть известные проблемы, они могут быть указаны на нашем сайте или в социальных сетях.""",
    """9. <b>Обратитесь за поддержкой</b>:
    
    - Если проблема не решается, воспользуйтесь командой `/bug` и напишите в службу поддержки с описанием вашей проблемы. Укажите, какие шаги вы уже предприняли для устранения проблемы.""",
]


@dataclass
class AccountStatuses:
    freezed = "Заморожен"
    admin = "Администратор"
    user = "Пользовательский"
    deleted = "Удален"
    banned = "Забанен"


def get_account_status(user_data: UserData):
    if user_data.active == UserActivity.freezed:
        return AccountStatuses.freezed
    elif user_data.admin:
        return AccountStatuses.admin
    else:
        return AccountStatuses.user


def get_sub_status(user_data: UserData):
    if user_data.active == UserActivity.active:
        return f"Активна | {rates.get(user_data.stage,'Неопознанный')} Тариф"
    elif user_data.active == UserActivity.inactive:
        return "Неактивна"
    else:
        return ""


def get_config_data(user_config: WgConfig):
    return f"""[Interface]
PrivateKey = {user_config.user_private_key}
Address = {user_config.address}
DNS = {user_config.dns}
[Peer]
PublicKey = {settings.WG_SERVER_KEY}
AllowedIPs = {user_config.allowed_ips}
Endpoint = {user_config.endpoint_ip}:{user_config.endpoint_port}
PersistentKeepalive = 25
"""


async def create_config_file(config: str):
    path = os.path.join(PATH, "tmp", f"{uuid.uuid3(uuid.NAMESPACE_DNS, config)}.conf")

    async with aiofiles.open(path, "w") as file:
        await file.write(config)

    return path


def create_config_qr(config: str):
    path = os.path.join(PATH, "tmp", f"{uuid.uuid3(uuid.NAMESPACE_DNS, config)}.png")

    qr = pyqrcode.create(config)
    qr.png(path, scale=8)

    return path


def get_end_sub(user_data: UserData):
    try:
        end = round(user_data.fbalance / (user_data.stage * settings.cost))
    except ZeroDivisionError:
        end = 0
    else:
        if end < 0:
            end = 0

    return end


def get_rate_descr(rate: int):
    general_1 = "\n<b>‼️ (Плата взимается ежедневно!)</b>"
    general_2 = "\n\n❗️ (Одна конфигурация может быть подключена к нескольким устройствам, однако такие подключения не могут быть одновременными, поэтому рекомендуется создавать по одной конфигурации на каждое устройство)"

    match rate:
        case 0:
            descr = "<b>Тариф: Нулевой</b>" "\nНе подключен никакой тариф" + general_2
        case 0.3:
            descr = (
                "<b>Тариф: Пробный</b>\n"
                "\n❗️ Может быть подключен <b>единоразово</b>"
                "\nПодключение другого тарифа лишает пользователя возможности подключить этот тариф"
                "\n\n‼️ Время действия пробного периода <b>7 дней</b>"
                "\n\n✅ Позволяет опробовать функционал подключения к VPN сервису"
                "\n✅ Доступно создание 1 конфигурации (1 устройство)" + general_2
            )
        case 1:
            descr = (
                "<b>Тариф: ⭐️Базовый⭐️</b>\n"
                "\n✅ Позволяет получить доступ к базовому функционалу VPN сервиса"
                "\n✅ Доступно создание 3 конфигураций (3 устройства)"
                + general_2
                + f"\n\n‼️ Актуальная стоимость тарифа: <b>{get_plural(settings.cost * rate, 'рубль, рубля, рублей')} в день</b>."
                + general_1
            )
        case 2.5:
            descr = (
                "<b>Тариф: 🌟Расширенный🌟</b>\n"
                "\n✅ Позволяет получить доступ к расширенному функционалу VPN сервиса"
                "\n✅ Доступны различные инструменты анализа работы VPN сервиса"
                "\n✅ Возможность отключать ненужные уведомления"
                "\n✅ Доступно создание 8 конфигураций (8 устройств)"
                + general_2
                + f"\n\n‼️ Актуальная стоимость тарифа: <b>{get_plural(settings.cost * rate, 'рубль, рубля, рублей')} в день</b>. "
                + general_1
            )
        case 5:
            descr = (
                "<b>Тариф: 💰Люкс💰</b>\n"
                "\n✅ Позволяет получить доступ к максимально доступному функционалу VPN сервиса"
                "\n✅ Доступны различные инструменты анализа работы VPN сервиса"
                "\n✅ Возможность отключать ненужные уведомления"
                "\n✅ Круглосуточный доступ к техподдержке сервиса (Поможет и расскажет как все настроить или починить)"
                "\n✅ Только обладатели тарифа Люкс могут подать заявку на получение статуса Администратор"
                "\n✅ Доступно создание 15 конфигураций (15 устройств)"
                + general_2
                + f"\n\n‼️ Актуальная стоимость тарифа: <b>{get_plural(settings.cost * rate, 'рубль, рубля, рублей')} в день</b>. "
                + general_1
            )
    return descr
