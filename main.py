import argparse
from ets.ets_xml_worker import *
from config import *

PROGNAME = 'New 223 auction publication script'
DESCRIPTION = '''Скрипт для публикации закупок новой секции 223'''
VERSION = '1.0'
AUTHOR = 'Belim S.'
RELEASE_DATE = '2018-09-11'


def show_version():
    print(PROGNAME, VERSION, '\n', DESCRIPTION, '\nAuthor:', AUTHOR, '\nRelease date:', RELEASE_DATE)


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

    parser.add_argument('-t', '--type', type=str, choices=NEW_223_IMPORT_URLS.keys(), default='ea2',
                        help="Установить тип закупки")

    parser.add_argument('-e', '--examinationDateTime', type=str, default='',
                        help="Установить дату рассмотрения заявок")

    return parser


def auction_publication(auction, database, **kwargs):
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

    imp_status, imp_info = new_223_import_xml(xml_file, database)
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
            auction_publication(namespace.auction, namespace.type, examinationDateTime=namespace.examinationDateTime)

        elif namespace.cancel_auction:
            print('Здесь будет функция отмены аукциона, если она понадобится')

        else:
            show_version()
            print('For more information run use --help')

exit(0)

