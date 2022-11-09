from datetime import datetime

release_date = {
    'v2_1': datetime.strptime("2022-09-10 10:00:00.00", "%Y-%m-%d %H:%M:%S.%f"),
    'v3': datetime.strptime("2022-10-24 12:00:00.00", "%Y-%m-%d %H:%M:%S.%f"),
    'v3.1': datetime.strptime("2022-10-30 00:00:00.00", "%Y-%m-%d %H:%M:%S.%f"),
    'v3.2': datetime.strptime("2022-11-09 12:00:00.00", "%Y-%m-%d %H:%M:%S.%f"),
}

mobilisation_date = datetime.strptime("2022-09-21 10", "%Y-%m-%d %H")

all_test_commands = {
    'polls_start': 'Начало: опросы (start_how_to_manipulate)',
    'proptest': 'Антипропаганда (antip_what_is_prop)',
    'test_goals': '🍤 НОВЫЕ 🍤 Причины войны (goals_war_point_now)',
    'test_reasons': 'Причины войны (antip_only_tip_of_the_berg)',
    'donbass': 'Донбас (donbass_big_tragedy)',
    'testnazi': 'Нацизм (start_nazi)',
    'teststrike': 'Превентивный удар (prevent_strike_start)',
    'test_nato': 'НАТО',
    'teststop': 'Остановить войну (stopwar_start)',
    'test_mob': 'Мобилизация',
    'putest': 'Путин (reasons_who_to_blame)',
    'testend': 'Концовка перед таймером (stopwar_first_manipulation_argument)',
    'mainskip69': 'Главное меню (mainmenu_really_menu)',
    'commands_clear': 'Сбросить команды на стандартный для всех юзеров набор',
    'commands_restore': 'Получить все тестовые команды в меню'
}

stat_points = {
    "Вступление": "prop_ex",
    "Антипропаганда": "antip_final_reaction",
    "Донбас": "donbas_final_result",
    "Превентивный Удар": "preventive_final_result",
    "НАТО": "nato_end",
    "Причины войны": "goals_final_result",
    "Подведем итоги": "sum_up_done",
    "Мобилизация": "mob_feedback",
    "Как закончить войну": "stopwar_done",
    "Полностью прошли бота": "main_menu",
    "Получили политический статус": "NewPolitStat_start",
    "Забанили бота": "is_ban"
}
