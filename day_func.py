from datetime import datetime
from log import logg
from bata import all_data


async def day_count(get_count=False, count_delete=False):
    try:
        current_datetime = datetime.now()
        ch = current_datetime.hour
        mn = current_datetime.minute
        check_day_count = all_data().get_data_red().get('count: day_count:')
        if str(check_day_count) == "None":
            all_data().get_data_red().set('count: day_count:', '1')
        if count_delete:
            all_data().get_data_red().set('count: day_count:', '1')

        day_count = all_data().get_data_red().get('count: day_count:')
        if not get_count:
            try:
                all_data().get_data_red().set('count: day_count:', f'{int(day_count) + 1}')
            except Exception as er:
                await logg.get_error(er)
        elif get_count == True:
            return day_count
        else:
            await logg.get_error('Неправильно поставлен запрос')

    except Exception as er:
        await logg.get_error(er)
