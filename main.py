import json
import seq_crawler
import async_crawler
import export
import time

def print_result(result):

    try:
        for menuName, catData in result.items():
            for catName, catInfo in catData.items():
                print('{}/{}:'.format(menuName, catName))
                products = catInfo['products']
                for product in products:
                    name = product[0]
                    price = product[1]
                    print('{} : {}'.format(name, price))
    except Exception as e:
        print('Invaild result.')
        print('{}: {}'.format(type(e), str(e)))
        print('.\n.\n.')

def export_result(result):

    while True:
        print('What kind of file would you like to export the result?')
        x = input('[1].json [2].csv [3].xlsx [4] Above all (Enter r to return): ')
        if x == '1':
            filename = input('Please enter the filename: ')
            export.to_json(result, filename)
            break
        elif x == '2':
            filename = input('Please enter the filename: ')
            export.to_csv(result, filename)
            break
        elif x == '3':
            filename = input('Please enter the filename: ')
            export.to_excel(result, filename)
            break
        elif x == '4':
            filename = input('Please enter the filename: ')
            export.to_json(result, filename)
            export.to_csv(result, filename)
            export.to_excel(result, filename)
            break
        elif x == 'r':
            print('Return to Start Menu.')
            print('.\n.\n.')
            return
        else:
            print('Wrong Input.')
            print('.\n.\n.')

def start_menu():

    result = None
    while True:
        print('Which command would you like to do?')
        print('[a] Parse new Best-Selling Products', end='\t')
        print('[b] Load a local JSON file', end='\t')
        print('[c] Print result')
        print('[d] Export result to a local file', end='\t')
        print('[q] Quit')
        ans = input(':')
        
        if ans == 'a':
            start = time.time()
            asyncCrawler = async_crawler.yCrawler('https://tw.buy.yahoo.com/', 50)
            asyncCrawler.parse_main()
            print('Start parsing {} category URLs'.format(len(asyncCrawler.catMap)))
            asyncCrawler.parse_products()
            end = time.time()
            print('Crawling time: {:.2f} secs'.format(end-start))

            if len(asyncCrawler.result) > 0:
                result = asyncCrawler.result
                print('Result is stored in memory!')
                print('.\n.\n.')
        elif ans == 'b':
            filename = ''
            while not filename.endswith('.json'):
                filename = input('Please enter a JSON filename: ')

            try:
                with open(filename) as f:
                    result = json.load(f)
                    print('Result is loaded.')
            except Exception as e:
                print('{}: {}'.format(type(e), str(e)))            
            print('.\n.\n.')
        elif ans == 'c':
            if result:
                print_result(result)
            else:
                print('No result yet...')
                print('.\n.\n.')
        elif ans == 'd':
            if result:
                print('.\n.\n.')
                export_result(result)
            else:
                print('No result yet...')
                print('.\n.\n.')
        elif ans == 's':
            start = time.time()
            seqCrawler = seq_crawler.yCrawler('https://tw.buy.yahoo.com/')
            seqCrawler.parse_main()
            end = time.time()
            print('Crawling time: {:.2f} secs'.format(end-start))
            
            if len(seqCrawler.result) > 0:
                result = seqCrawler.result
                print('Result is stored in memory! \n')
                print('.\n.\n.')
        elif ans == 'q':
            return
        else:
            print('Wrong Input.')
            print('.\n.\n.')

if __name__ == '__main__':
    print('')
    print('============================================================================')
    print('Welcome to the awesome crawler!!!')
    print('We can help you find out the Best-Selling Products on Yahoo Shopping Mall!!!')
    print('============================================================================')
    start_menu()

    