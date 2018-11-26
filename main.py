import argparse
from ets.ets_xml_worker import *
from ets.ets_mysql_lib import MysqlConnection as Mc
from config import *
from queries import *


PROGNAME = 'New 223 auction publication script'
DESCRIPTION = '''Скрипт для публикации закупок новой секции 223'''
VERSION = '1.1'
AUTHOR = 'Belim S.'
RELEASE_DATE = '2018-09-11'

version_info = ''' Новое:
[x] При публикации изменения извещения не обязательно указывать тип процедуры
[x] Для отмены не нужно указывать тип закупки
[x] Возможно отменять закупки на статусе отличающемся от приема заявок
[x] Возможность смены GUID-a пакета
'''


def show_version():
    print(PROGNAME, VERSION, '\n', DESCRIPTION, '\nAuthor:', AUTHOR, '\nRelease date:', RELEASE_DATE, '\n',
          version_info)


# обработчик параметров командной строки
def create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--version', action='store_true',
                        help="Показать версию программы")

    parser.add_argument('-p', '--publish_auction', action='store_const', const=True,
                        help="Режим публикации аукциона")

    parser.add_argument('-c', '--cancel_auction', action='store_const', const=True,
                        help="Режим отмены аукциона")

    parser.add_argument('-a', '--auction', type=str, default='',
                        help="Установить номер закупки")

    parser.add_argument('-t', '--type', type=str, choices=NEW_223_IMPORT_URLS.keys(), default='',
                        help="Установить тип закупки")

    parser.add_argument('-e', '--examination_datetime', type=str, default='',
                        help="Установить дату рассмотрения заявок")

    parser.add_argument('-e', '--set_random_guid', action='store_true',
                        help="Установить рандомный GUID пакета")

    return parser


def string_decorator(f):
    def wrapper(*args, **kwargs):
        print('----------------------------------------------------')
        ret = f(*args, **kwargs)
        print('----------------------------------------------------')
        return ret
    return wrapper


@string_decorator
def auction_publication(auction, **kwargs):
    database = kwargs.get('type', None)
    """Функция публикации процедуры с необходимыми корректировками"""
    if not database:
        auction_info = found_procedure_223_db(auction, get_id=True)
        if auction_info:
            database = auction_info['db']
            print('БД процедуры: %s' % database)
        else:
            print('Для извещения необходимо указать тип процедуры')
            return 1

    xml_file, find_error = new_223_auction_finder(auction, out_dir)
    if find_error:
        print(find_error)
        if input('Продолжить? Y/n: ') not in 'YН':
            return 1

    correction_status, correction_error = new_223_xml_corrector(xml_file, **kwargs)
    if correction_status:
        print('Пакет валиден')
    else:
        print('Пакет не валиден: ', correction_error)
    if input('Опубликовать аукцион? Y/n: ') not in 'YН':
        return 1

#    imp_status, imp_info = new_223_import_xml(xml_file, database)
#    if imp_status:
#        print(imp_info)
#        return 0
#    else:
#        print('Пакет импортирован с ошибкой: %s' % imp_info)
#        return 1


@string_decorator
def auction_cancel(auction):
    """Функция отмены процедуры"""
    auction_info = found_procedure_223_db(auction, get_id=True)
    print('БД процедуры: %s' % auction_info['db'])

    if input('Установить процедуре статус "Прием заявок"? Y/n: ') in 'YН':
        cn = Mc(connection=auction_info['connection'])
        cn.execute_query(procedure_published_update_query % auction_info['id'])
        cn.execute_query(lot_published_update_query % auction_info['id'])
        print('''Установлен статус "Прием заявок"''')

    xml_file, find_error = new_223_auction_cancel_finder(auction, out_dir)
    if find_error:
        print(find_error)
        if input('Продолжить? Y/n: ') not in 'YН':
            return 1

    correction_status, correction_error = new_223_xml_corrector(xml_file)
    if correction_status:
        print('Пакет валиден')
    else:
        print('Пакет не валиден: ', correction_error)
    if input('Опубликовать отмену аукциона? Y/n: ') not in 'YН':
        return 1

    imp_status, imp_info = new_223_import_xml(xml_file, auction_info['db'])
    if imp_status:
        print(imp_info)
        return 0
    else:
        print('Пакет импортирован с ошибкой: %s' % imp_info)
        return 1

if __name__ == '__main__':
        # парсим аргументы командной строки
        my_parser = create_parser()
        namespace = my_parser.parse_args()

        if namespace.version:
            show_version()
            exit(0)

        if (namespace.publish_auction or namespace.cancel_auction) and not namespace.auction:
            print('Не установлен обязательный параметр --auction')
            exit(1)

        if namespace.publish_auction:
            auction_publication(namespace.auction,
                                type=namespace.type,
                                examinationDateTime=namespace.examination_datetime)

        elif namespace.cancel_auction:
            auction_cancel(namespace.auction)

        else:
            show_version()
            print('For more information run use --help')

exit(0)

