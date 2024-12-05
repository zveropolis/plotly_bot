
const planDetails = {
    'Пробный': {
        description: 'Идеально подходит для тестирования нашего сервиса. Может быть подключен единоразово. Подключение другого тарифа лишает пользователя возможности подключить этот тариф',
        tax: 0,
        features: {
            'Базовый функционал': 'Воспользуйтесь базовыми функциями VPN с ограниченным доступом к сервисам',
            'Неограниченная скорость': 'Скорость подключения по VPN не ограничена',
            'Отсутствие рекламы': 'Никакой рекламы, никакого спама, никаких уведомлений',
            '1 Устройство': 'Доступно создание 1 конфигурации'
        }
    },
    'Базовый': {
        description: 'Отлично подходит для индивидуальных пользователей, которым требуется быстрый и легкий VPN сервис',
        tax: 0,
        features: {
            'Базовый функционал': 'Воспользуйтесь базовыми функциями VPN с ограниченным доступом к сервисам',
            'Неограниченная скорость': 'Скорость подключения по VPN не ограничена',
            'Отсутствие рекламы': 'Никакой рекламы, никакого спама, никаких уведомлений',
            '3 Устройства': 'Доступно создание 3-х конфигураций'
        }
    },
    'Расширенный': {
        description: 'Наш самый популярный тарифный план, идеально подходящий для семей или пользователей с несколькими устройствами.',
        tax: 25,
        features: {
            'Расширенный функционал': 'Полный доступ ко всем возможностям сервиса',
            'Неограниченная скорость': 'Скорость подключения по VPN не ограничена',
            'Отсутствие рекламы': 'Никакой рекламы, никакого спама, никаких уведомлений',
            '8 Устройств': 'Доступно создание 8-ми конфигураций',
            'Уведомления': 'Возможность отключать ненужные уведомления от сервиса',
            'Инструменты': 'Доступны различные инструменты анализа работы VPN сервиса: скорость и загруженность сервера, ',
        }
    },
    'Люкс': {
        description: 'Премиальный тариф для тех, кто хочет поддержать создателей сервиса',
        tax: 50,
        features: {
            'Расширенный функционал': 'Полный доступ ко всем возможностям сервиса',
            'Неограниченная скорость': 'Скорость подключения по VPN не ограничена',
            'Отсутствие рекламы': 'Никакой рекламы, никакого спама, никаких уведомлений',
            '15 Устройств': 'Доступно создание 15-ти конфигураций',
            'Уведомления': 'Возможность отключать ненужные уведомления от сервиса',
            'Инструменты': 'Доступны различные инструменты анализа работы VPN сервиса: скорость и загруженность сервера',
            '👑Приоритетный статус': 'Только обладатели тарифа Люкс могут подать заявку на получение статуса Администратор и имеют круглосуточный доступ к техподдержке сервиса (Поможет и расскажет как все настроить или починить)',
        }
    }
};

document.querySelectorAll('.pricing-card').forEach(card => {
    card.addEventListener('click', (e) => {
        if (e.target.classList.contains('cta-button')) return;

        const planName = card.querySelector('h3').textContent;
        const plan = planDetails[planName];

        const modal = document.getElementById('modal');
        const modalTitle = modal.querySelector('.modal-title');
        const modalDescription = modal.querySelector('.modal-description');
        const modalDescriptionTax = modal.querySelector('.modal-description-tax');
        const modalFeatures = modal.querySelector('.modal-features');

        modalTitle.textContent = planName + ' тариф';
        modalDescription.textContent = plan.description;
        modalDescriptionTax.textContent = 'Комиссия при понижении данного тарифа: ' + plan.tax + ' ₽';

        modalFeatures.innerHTML = Object.entries(plan.features)
            .map(([feature, detail]) => `
    <div class="feature-detail">
        <svg width="20" height="20" viewBox="0 0 20 20">
            <path d="M8.43 14.43L3.85 9.85L5.27 8.43L8.43 11.59L14.73 5.29L16.15 6.71L8.43 14.43Z"/>
        </svg>
    <div>
        <strong>${feature}:</strong> ${detail}
        </div>
    </div>
    `).join('');

        modal.classList.add('active');
    });
});

document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('modal').classList.remove('active');
});

document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
        e.target.classList.remove('active');
    }
});
