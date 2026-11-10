import {ROUTE_NAMES} from '@/core/constants';

export const NAVIGATION_ITEMS = Object.freeze([
    {id: 'base', label: 'База', ariaLabel: 'База знаний', routeName: ROUTE_NAMES.home, icon: 'BookOpen'},
    {id: 'dialogs', label: 'Диалоги', ariaLabel: 'Диалоги', routeName: ROUTE_NAMES.dialogs, icon: 'MessageSquareText'},
    {id: 'documents', label: 'Документы', ariaLabel: 'Документы', routeName: ROUTE_NAMES.document, icon: 'FileText'},
    {
        id: 'verification',
        label: 'Проверка',
        ariaLabel: 'Схема проверки ответа',
        routeName: ROUTE_NAMES.verification,
        icon: 'ShieldCheck',
    },
]);
