const CONTRACT_PRICE_TEXT =
    'Ориентировочная общая цена договора составляет 8 400 000 (восемь миллионов четыреста тысяч) рублей, включая НДС.';
const CONTRACT_VAT_TEXT =
    'Цена Товара указывается в Спецификациях и включает НДС по ставке 20%, стоимость упаковки и доставки до склада Покупателя.';
const CONTRACT_DELIVERY_TERM_TEXT =
    'Поставка Товара осуществляется партиями в течение 10 (десяти) рабочих дней с даты подписания Сторонами Спецификации на соответствующую партию.';
const CONTRACT_DELIVERY_DATE_TEXT =
    'Датой поставки считается дата подписания Покупателем универсального передаточного документа (УПД).';
const CONTRACT_PAYMENT_TEXT =
    'Покупатель оплачивает Товар в течение 30 (тридцати) календарных дней с даты подписания универсального передаточного документа (УПД) на соответствующую партию.';
const CONTRACT_PENALTY_TEXT =
    'За просрочку оплаты Товара Покупатель уплачивает Поставщику неустойку в размере 0,1% от неоплаченной суммы за каждый день просрочки, но не более 10% от неоплаченной суммы.';
const CONTRACT_LIABILITY_TEXT =
    'Общий размер ответственности каждой из Сторон по настоящему договору, включая неустойки и возмещение убытков, ограничен суммой, равной 50% от общей цены договора, указанной в п. 2.2.';

const REGULATION_PARTIES_TEXT = 'Проект договора согласуется с юридическим отделом и главным бухгалтером.';
const REGULATION_ORIGINAL_TEXT =
    'Подписанный оригинал договора передаётся в юридический отдел для хранения в течение 3 (трёх) рабочих дней с даты подписания.';

/**
 * @param {string} text
 * @returns {Record<string, string>}
 */
function sameInContractEditions(text) {
    return {original: text, ds1: text};
}

/**
 * @param {string} text
 * @returns {Record<string, string>}
 */
function sameInRegulationEditions(text) {
    return {'edition-2023': text, 'edition-2025': text};
}

/** @type {Readonly<Record<string, import('@/core/types/document').LegalDocument>>} */
export const DOCUMENTS = Object.freeze({
    'p-17-2024': {
        id: 'p-17-2024',
        title: 'Договор поставки № П-17/2024',
        kindLabel: 'Договор · поставка · ООО «Альфа-Трейд»',
        image: 'contracts',
        editions: [
            {id: 'original', label: 'Исходная', date: '12.02.2024'},
            {id: 'ds1', label: 'ДС № 1', date: '03.09.2024'},
        ],
        outline: [
            {id: '1', title: '1. Предмет договора'},
            {id: '2', title: '2. Цена договора'},
            {id: '3', title: '3. Порядок поставки'},
            {id: '4', title: '4. Порядок расчётов'},
            {id: '5', title: '5. Качество и гарантия'},
            {id: '6', title: '6. Приёмка Товара'},
            {id: '7', title: '7. Ответственность сторон'},
            {id: '8', title: '8. Разрешение споров'},
            {id: '9', title: '9. Срок действия'},
        ],
        sections: [
            {
                id: '2',
                title: '2. Цена договора',
                clauses: [
                    {id: '2.1', versions: sameInContractEditions(CONTRACT_VAT_TEXT)},
                    {id: '2.2', versions: sameInContractEditions(CONTRACT_PRICE_TEXT)},
                ],
            },
            {
                id: '3',
                title: '3. Порядок поставки',
                clauses: [
                    {id: '3.1', versions: sameInContractEditions(CONTRACT_DELIVERY_TERM_TEXT)},
                    {
                        id: '3.2',
                        versions: {
                            original:
                                'Товар доставляется Поставщиком по адресу: г. Москва, ул. Складская, д. 4, стр. 2.',
                            ds1: 'Товар доставляется Поставщиком по адресу: Московская область, г. Химки, ул. Заводская, д. 15, склад № 3.',
                        },
                    },
                    {id: '3.3', versions: sameInContractEditions(CONTRACT_DELIVERY_DATE_TEXT)},
                ],
            },
            {
                id: '4',
                title: '4. Порядок расчётов',
                clauses: [{id: '4.2', versions: sameInContractEditions(CONTRACT_PAYMENT_TEXT)}],
            },
            {
                id: '7',
                title: '7. Ответственность сторон',
                clauses: [
                    {id: '7.2', versions: sameInContractEditions(CONTRACT_PENALTY_TEXT)},
                    {id: '7.5', versions: sameInContractEditions(CONTRACT_LIABILITY_TEXT)},
                ],
            },
        ],
        citations: [
            {clauseId: '2.2', dialogId: '412', dialogNumber: '№412', dialogTitle: 'Согласование П-17/2024', cite: 2},
            {clauseId: '7.2', dialogId: '407', dialogNumber: '№407', dialogTitle: 'Неустойка за просрочку', cite: 1},
        ],
        comments: [
            {
                id: 'comment-1',
                author: 'Ольга Шишкина',
                initials: 'ОШ',
                clauseId: '3.2',
                dateLabel: '04.09.2024',
                text: 'Новый адрес — только для партий по спецификациям после 01.10.2024. Старые партии везут на Складскую.',
            },
            {
                id: 'comment-2',
                author: 'Анна Корнеева',
                initials: 'АК',
                clauseId: '7.2',
                dateLabel: 'сегодня',
                text: 'Контрагент в претензии считает по 0,5 % — в договоре 0,1 %.',
            },
        ],
        files: ['Договор П-17-2024.pdf', 'ДС № 1 от 03.09.2024.pdf'],
    },
    reglament: {
        id: 'reglament',
        title: 'Регламент согласования договоров',
        kindLabel: 'Внутренний документ · ООО «Меридиан»',
        image: 'internal',
        editions: [
            {id: 'edition-2023', label: 'Ред. 2023', date: '10.01.2023', note: 'утратила силу 01.03.2025'},
            {id: 'edition-2025', label: 'Ред. 2025', date: '01.03.2025'},
        ],
        outline: [
            {id: '1', title: '1. Общие положения'},
            {id: '2', title: '2. Порядок согласования'},
            {id: '3', title: '3. Оформление согласования'},
            {id: '4', title: '4. Типовые формы'},
            {id: '5', title: '5. Особые случаи'},
        ],
        sections: [
            {
                id: '2',
                title: '2. Порядок согласования',
                clauses: [
                    {id: '2.1', versions: sameInRegulationEditions(REGULATION_PARTIES_TEXT)},
                    {
                        id: '2.2',
                        versions: {
                            'edition-2023':
                                'Срок согласования юридическим отделом — 3 (три) рабочих дня, главным бухгалтером — 2 (два) рабочих дня.',
                            'edition-2025':
                                'Срок согласования юридическим отделом — 3 (три) рабочих дня, главным бухгалтером — 2 (два) рабочих дня. Срок может быть продлён не более чем на 2 рабочих дня по мотивированному запросу согласующего.',
                        },
                    },
                    {
                        id: '2.3',
                        versions: {
                            'edition-2023':
                                'Договоры на сумму свыше 1 000 000 (одного миллиона) рублей дополнительно согласуются с финансовым директором.',
                            'edition-2025':
                                'Договоры на сумму свыше 3 000 000 (трёх миллионов) рублей дополнительно согласуются с финансовым директором.',
                        },
                    },
                    {
                        id: '2.4',
                        versions: {
                            'edition-2023':
                                'Договоры на сумму свыше 10 000 000 (десяти миллионов) рублей подлежат одобрению генеральным директором до подписания.',
                            'edition-2025':
                                'Договоры на сумму свыше 15 000 000 (пятнадцати миллионов) рублей подлежат одобрению генеральным директором до подписания.',
                        },
                    },
                    {
                        id: '2.5',
                        versions: {
                            'edition-2025':
                                'Договоры, по которым Общество выступает поручителем или залогодателем, согласуются с финансовым директором независимо от суммы.',
                        },
                    },
                ],
            },
            {
                id: '3',
                title: '3. Оформление согласования',
                clauses: [
                    {
                        id: '3.1',
                        versions: {
                            'edition-2023': 'Согласование оформляется в листе согласования на бумажном носителе.',
                            'edition-2025':
                                'Согласование оформляется в СЭД. Лист согласования на бумажном носителе не требуется.',
                        },
                    },
                    {id: '3.2', versions: sameInRegulationEditions(REGULATION_ORIGINAL_TEXT)},
                ],
            },
        ],
        citations: [
            {clauseId: '2.1', dialogId: '412', dialogNumber: '№412', dialogTitle: 'Согласование П-17/2024', cite: 1},
            {clauseId: '2.3', dialogId: '412', dialogNumber: '№412', dialogTitle: 'Согласование П-17/2024', cite: 3},
            {clauseId: '2.4', dialogId: '412', dialogNumber: '№412', dialogTitle: 'Согласование П-17/2024', cite: 4},
            {clauseId: '3.1', dialogId: '412', dialogNumber: '№412', dialogTitle: 'Согласование П-17/2024', cite: 5},
        ],
        comments: [
            {
                id: 'comment-3',
                author: 'Ольга Шишкина',
                initials: 'ОШ',
                clauseId: '2.3',
                dateLabel: '02.03.2025',
                text: 'Порог для финдиректора вырос с 1 до 3 млн ₽ — старые ответы по этому пункту пересмотреть.',
            },
        ],
        files: ['Регламент ред. 2025.pdf', 'Регламент ред. 2023 (утратил силу).pdf'],
    },
    'nk-164': {
        id: 'nk-164',
        title: 'Налоговый кодекс РФ, статья 164',
        kindLabel: 'Закон · только действующая редакция',
        image: 'taxes',
        editions: [{id: 'current', label: 'Действующая', date: '01.01.2026'}],
        outline: [
            {id: '1', title: '1. Ставка 0 процентов'},
            {id: '2', title: '2. Ставка 10 процентов'},
            {id: '3', title: '3. Общая ставка'},
            {id: '4', title: '4. Расчётные ставки'},
        ],
        sections: [
            {
                id: '3',
                title: '3. Общая ставка',
                clauses: [
                    {
                        id: '3',
                        versions: {
                            current:
                                'Налогообложение производится по налоговой ставке 22 процента в случаях, не указанных в пунктах 1, 2 и 4 настоящей статьи.',
                        },
                    },
                ],
            },
        ],
        citations: [{clauseId: '3', dialogId: '405', dialogNumber: '№405', dialogTitle: 'Ставка НДС в 2018 году', cite: 1}],
        comments: [],
        files: ['НК РФ ст. 164 (действующая редакция).txt'],
    },
});
