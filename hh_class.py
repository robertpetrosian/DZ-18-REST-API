import requests

class Area():
    '''
    класс регионов
    '''

    def __init__(self):
        '''
        создание справочника регионов России
        '''
        hh_url= 'https://api.hh.ru/areas'
        result = requests.get((hh_url))
        if result.status_code != requests.codes.ok:
            self.areas = []
            return

        id_russia=result.json()[0]['id']
        russia = result.json()[0]['areas']
        lst_russia =[]
        for x in russia:
            if x['parent_id'] == id_russia:
                lst_russia.append((x['name'], x['id']))
        dict_russia= dict(lst_russia)
        self.areas = dict_russia

    def __call__(self, args):
        '''
        :param args: список , каждый элемент - часть имени желаемого региона
        :return: список, идентификаторов найденных регионов
        '''
        rez=[]
        for x in args:
            if not isinstance(x,str):
                continue
            for key,val in self.areas.items():
                if x.upper().strip() in key.upper():
                    rez.append(val)
        return rez

class Specialization():
    '''
    класс специализаций
    '''

    def __init__(self):
        '''
        создание справочника, состоящего из нижнего уровня элементов
        '''
        result = requests.get('https://api.hh.ru/specializations')
        if result.status_code != requests.codes.ok:
            self.specs = []
            return

        rez=[]
        response = result.json()
        for x in response:
            for y in x['specializations']:
                rez.append((y['name'], y['id']))
        self.specs=dict(rez)

    def __call__(self, args):
        '''
        :param args: список ,каждый элемент - часть имени специализации
        :return: список, идентификаторов найденных специализаций
        '''
        rez=[]
        for x in args:
            if not isinstance(x,str):
                continue
            for key,val in self.specs.items():
                if x.upper().strip() in key.upper():
                    rez.append(val)
        return rez

class Zapros():
    '''
    класс запросов
    '''
    def __init__(self, *args, **kwargs):
        '''
        создание запроса с параметрами params for requests.get
        '''
        self.params = kwargs
        self.params['per_page']=100
        self.params['page']=0


    def __call__(self):
        '''
        запрос вакансий , проход по всем страницам
        :return: возвращает список ИД вакансий
        '''
        url = 'https://api.hh.ru/vacancies'
        result = requests.get(url, params=self.params)
        rez = []
        while result.status_code == requests.codes.ok and \
                len(rez) < result.json()['found'] :
            response =result.json()
            for x in response['items']:
                rez.append(x['id'])
            self.params['page'] += 1
            result = requests.get(url, params=self.params)

        self.params['page'] = 0
        return rez

