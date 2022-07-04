from datetime import datetime
from log import logg
from bata import all_data


async def day_count(get_count=False):
    try:
        current_datetime = datetime.now()
        ch = current_datetime.hour
        mn = current_datetime.minute
        check_day_count = all_data().get_data_red().get('count: day_count:')
        if str(check_day_count) == "None":
            all_data().get_data_red().set('count: day_count:', '1')
        if 300 <= int(f'{ch}{mn}') <= 359:
            print("Удаление")
            all_data().get_data_red().set('count: day_count:', '1')

        day_count = all_data().get_data_red().get('count: day_count:')
        if get_count == False:
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




