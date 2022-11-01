from datetime import datetime, timedelta

from bata import all_data
from data_base.DBuse import mongo_count_docs
from log import logg
from resources.variables import stat_points, release_date


def count_visual(full_count, part_count, name: str):
    full_count = 1 if not full_count else full_count
    pr = round(int(part_count) / int(full_count) * 100)
    exit_string = ""
    emojy = '🟩'
    if name.__contains__("Забанили"):
        emojy = "🟥"
    for ten in range(round(pr / 10)):
        exit_string += emojy
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
    is_ban = await mongo_count_docs('database', 'userinfo',
                                    {"datetime": {"$gte": release_date['v3.1']}}, check_default_version=False)
    text = ""
    for point in stat_points:
        users_count = await mongo_count_docs('database', 'statistics_new',
                                             {stat_points[point]: {'$exists': True},
                                              "datetime": {"$gte": release_date['v3.1']}}, check_default_version=False)
        text += count_visual(stat_statistics, users_count, point)
    text += count_visual(stat, is_ban, 'Забанили бота')
    text = f"<code>Всего пользователей: {stat}\n" \
           f"Пользователей после установки всех флагов: {stat_statistics}\n" \
           f"Новых пользователей за сутки: {day_unt}\n\n</code>" \
           + text
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
                "             ": 1,
                "donbas_final_result": 1,
                "preventive_final_result": 1,
                "nato_end": 1,
                "goals_final_result": 1,
                "sum_up_done": 1,
                "mob_feedback": 1,
                "stopwar_done": 1,
                "main_menu": 1,
                "is_ban": 1,
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
                ],
                "is_ban": [
                    {"$match": {"is_ban": {"$exists": True}}},
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
                "main_menu": {"$arrayElemAt": ["$main_menu.Sum", 0]},
                "is_ban": {"$arrayElemAt": ["is_ban.Sum", 0]}
            }}
        ]):
            for point in stat_points:
                count = result.get(stat_points[point], 0)
                text += count_visual(all_count, count, point)
        return text
    except Exception as ex:
        await logg.get_error(f"Pretty ad stats is failed!\n\n{ex}")


async def pretty_polit_stats(ad_tag: str, title: str | None = None):
    client = all_data().get_mongo()
    database = client['database']
    stat_collection = database['statistics_new']
    text = "\n\n————————\n\n"
    async for result in stat_collection.aggregate([
        {
            "$match": {
                "NewPolitStat_start": {"$exists": True}
            }
        },
        {
            "$lookup": {
                "from": "userinfo",
                "localField": "_id",
                "foreignField": "_id",
                "pipeline": [
                    {
                        "$match": {
                            "advertising": ad_tag
                        }
                    }
                ],
                "as": "userinfo"
            }
        },
        {
            "$match": {
                "userinfo": {"$ne": []}
            }
        },
        {
            "$project": {
                "NewPolitStat_start": 1,
                "NewPolitStat_end": 1
            }
        },
        {
            "$facet": {
                "Total": [
                    {
                        "$count": "Total"
                    },

                ],
                "Groups": [
                    {
                        "$match": {"NewPolitStat_end": {"$exists": True}}
                    },
                    {
                        "$group": {
                            "_id": {
                                "Start": "$NewPolitStat_start",
                                "End": "$NewPolitStat_end"
                            },
                            "users_count": {
                                "$sum": 1
                            }
                        }
                    }],
                "StartСounts": [{
                    "$group": {
                        "_id": "$NewPolitStat_start",
                        "users_count": {
                            "$sum": 1
                        }
                    }
                }],
                "EndСounts": [
                    {
                        "$match": {"NewPolitStat_end": {"$exists": True}}
                    },
                    {
                        "$group": {
                            "_id": "$NewPolitStat_start",
                            "users_count": {
                                "$sum": 1
                            }
                        }
                    }],
            }
        },
        {
            "$addFields": {
                "Total": {
                    "$arrayElemAt": [
                        "$Total",
                        0
                    ]
                }
            }
        },
        {
            "$unwind": "$StartСounts",
        },
        {
            "$unwind": "$Groups",
        },
        {
            "$unwind": "$EndСounts",
        },
        {"$match": {"$expr": {"$and": [
            {"$eq": ["$StartСounts._id", "$Groups._id.Start"]},
            {"$eq": ["$EndСounts._id", "$Groups._id.Start"]}
        ]
        }}},
        {
            "$project": {
                "Groups": 1,
                "StartCount": "$StartСounts.users_count",
                "EndCount": "$EndСounts.users_count",
                "Total": "$Total.Total"
            }
        },

        {
            "$project": {
                "_id": 0,
                "Start": "$Groups._id.Start",
                "End": "$Groups._id.End",
                "changed_percentage": {
                    "$multiply": [
                        {
                            "$divide": [
                                "$Groups.users_count",
                                "$EndCount"
                            ]
                        },
                        100
                    ]
                },
                "start_percentage": {
                    "$multiply": [
                        {
                            "$divide": [
                                "$StartCount",
                                "$Total"
                            ]
                        },
                        100
                    ]
                },
                "made_it_to_the_end": {
                    "$multiply": [
                        {
                            "$divide": [
                                "$EndCount",
                                "$StartCount"
                            ]
                        },
                        100
                    ]
                },
                "Total": "$Total"
            }
        },
        {"$group": {
            "_id": "$Start",
            "Start_perc": {"$addToSet": "$start_percentage"},
            "Made_it": {"$addToSet": "$made_it_to_the_end"},
            "End_change": {"$addToSet": {"Status": "$End", "Change": "$changed_percentage"}}
        }}
    ]):
        text += f"<code>Группа: </code><b>{result['_id']}</b>\n" \
                f"<code>В начале: </code><b>{round(result.get('Start_perc', [0])[0])}%</b>\n"
        text += f"<code>————————</code>\n" \
                f"<code>Дошли до конца: </code>{round(result['Made_it'][0])}%\n<code>Из них:</code>\n"
        group_txt, group_title_txt = str(), str()
        for ingroup in result.get('End_change', []):
            group_txt += f"<i>{ingroup['Status']}</i>: <b>{round(ingroup['Change'])}%</b>\n"
        text += group_title_txt
        text += group_txt
        text += "\n\n————————\n\n"

    return text
