from bata import all_data
from log import logg


async def day_count(get_count=False, count_delete=False):
    try:
        check_day_count = all_data().get_data_red().get('count: day_count:')
        if str(check_day_count) == "None":
            all_data().get_data_red().set('count: day_count:', '1')
        if count_delete:
            all_data().get_data_red().set('count: day_count:', '1')
        day_count_r = all_data().get_data_red().get('count: day_count:')
        if not get_count:
            try:
                all_data().get_data_red().set('count: day_count:', f'{int(day_count_r) + 1}')
            except Exception as er:
                await logg.get_error(er)
        elif get_count is True:
            return day_count_r
        else:
            await logg.get_error('Неправильно поставлен запрос')

    except Exception as er:
        await logg.get_error(er)
