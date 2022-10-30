from datetime import datetime, timedelta

from bata import all_data
from data_base.DBuse import mongo_count_docs
from log import logg
from resources.variables import stat_points, release_date


def count_visual(full_count, part_count, name: str):
    full_count = 1 if not full_count else full_count
    pr = round(int(part_count) / int(full_count) * 100)
    exit_string = ""
    for ten in range(round(pr / 10)):
        exit_string += '🟩'
    exit_string = exit_string.ljust(10, "⬜")
    title = f'{name}: {pr}%'
    foot = f'Всего {part_count}'.ljust(10, ' ')
    exit_string = f'<code>{title}\n' + exit_string + f'\n{foot}</code>\n\n'
    return exit_string


async def pretty_progress_stats():
    past = datetime.now() - timedelta(days=1)
    day_unt = await mongo_count_docs('database', 'statistics_new',
                                     {"datetime": {"$gte": past}}, check_default_version=False)
    stat = await mongo_count_docs('database', 'statistics_new', {"come": {"$exists": True}})
    stat_statistics = await mongo_count_docs('database', 'statistics_new',
                                             {"datetime": {"$gte": release_date['v3.1']}}, check_default_version=False)
    text = ""
    for point in stat_points:
        users_count = await mongo_count_docs('database', 'statistics_new',
                                             {stat_points[point]: {'$exists': True},
                                              "datetime": {"$gte": release_date['v3.1']}}, check_default_version=False)
        text += count_visual(stat_statistics, users_count, point)
    text = f"<code>Всего пользователей: {stat}\n" \
           f"Пользователей после установки всех флагов: {stat_statistics}\n" \
           f"Новых пользователей за сутки: {day_unt}</code>\n\n" + text
    return text


async def pretty_add_progress_stats(ad_tag: str, title: str | None = None):
    try:
        client = all_data().get_mongo()
        database = client['database']
        stat_collection = database['statistics_new']
        user_collection = database['userinfo']
        all_count = await user_collection.count_documents({"advertising": ad_tag})
        text = f"<code>Пришло по ссылке: {all_count}\n\n</code>"
        if title:
            text = f"Результаты для\n<b>{title}</b>\n\n" + text
        async for result in stat_collection.aggregate([
            {"$match": {
                "datetime": {"$gte": release_date["v3"]},
                "origin": {"$exists": True}
            }},
            {"$lookup": {
                "from": "userinfo",
                "localField": "_id",
                "foreignField": "_id",
                "pipeline": [
                    {"$match": {
                        "advertising": ad_tag
                    }}],
                "as": "userinfo"
            }},
            {"$match": {
                "userinfo": {"$ne": []}
            }},
            {"$project": {
                "prop_ex": 1,
                "antip_final_reaction": 1,
                "donbas_final_result": 1,
                "preventive_final_result": 1,
                "nato_end": 1,
                "goals_final_result": 1,
                "sum_up_done": 1,
                "mob_feedback": 1,
                "stopwar_done": 1,
                "main_menu": 1
            }},
            {"$facet": {
                "prop_ex": [
                    {"$match": {"prop_ex": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "antip_final_reaction": [
                    {"$match": {"antip_final_reaction": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "donbas_final_result": [
                    {"$match": {"donbas_final_result": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "preventive_final_result": [
                    {"$match": {"preventive_final_result": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "nato_end": [
                    {"$match": {"nato_end": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "goals_final_result": [
                    {"$match": {"goals_final_result": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "sum_up_done": [
                    {"$match": {"sum_up_done": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "mob_feedback": [
                    {"$match": {"mob_feedback": {"$exists": True}}},
                    {"$count": "Sum"}
                ],
                "stopwar_done": [
                    {"$match": {"stopwar_done": {"$exists": True}}},
                    {'$count': "Sum"}
                ],
                "main_menu": [
                    {"$match": {"main_menu": {"$exists": True}}},
                    {"$count": "Sum"}
                ]
            }},
            {"$project": {
                "prop_ex": {"$arrayElemAt": ["$prop_ex.Sum", 0]},
                "antip_final_reaction": {"$arrayElemAt": ["$antip_final_reaction.Sum", 0]},
                'donbas_final_result': {"$arrayElemAt": ["$donbas_final_result.Sum", 0]},
                "preventive_final_result": {"$arrayElemAt": ["$preventive_final_result.Sum", 0]},
                "nato_end": {"$arrayElemAt": ["$nato_end.Sum", 0]},
                "goals_final_result": {"$arrayElemAt": ["$goals_final_result.Sum", 0]},
                "sum_up_done": {"$arrayElemAt": ["$sum_up_done.Sum", 0]},
                "mob_feedback": {"$arrayElemAt": ["$mob_feedback.Sum", 0]},
                "stopwar_done": {"$arrayElemAt": ["$stopwar_done.Sum", 0]},
                "main_menu": {"$arrayElemAt": ["$main_menu.Sum", 0]}
            }}
        ]):
            for point in stat_points:
                count = result.get(point, 0)
                text += count_visual(all_count, count, point)
        return text
    except Exception as ex:
        await logg.get_error(f"Pretty ad stats is failed!\n\n{ex}")
