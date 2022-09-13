import pprint
import requests
import hh_class
import statistics
import json

reg_word =['ростов','краснодар']
spec_word =['Разработ','developer','тестиров']
text_word = ['Python','Django', 'sql']

# регионы поиска
reg=hh_class.Area()
areas = reg(reg_word)

# специализация
spec = hh_class.Specialization()
specialization = spec(spec_word)

text_search = 'NAME:('+' OR '.join(text_word)+')'
# экземпляр списка вакансий
vac=hh_class.Zapros(area = areas,
                    specialization = specialization ,
                    text = text_search)

# список ИД вакансий
vacancies = vac()
if not vacancies:
    print('Вакансии не найдены')
    exit()

lst_key_skills = [] # список навыков избранных вакансий
lst_salary = []     # список зарплат
for v in vacancies:
    # получение списков
    result = requests.get(f'https://api.hh.ru/vacancies/{v}')
    if result.status_code != requests.codes.ok:
        continue

    response = result.json()
    lst_key_skills.extend(response['key_skills'])
    lst_salary.append(response['salary'])

# вычисляем диапазон зарплат -ОТ минимальное медианное значение ДО максимальное медианное значение
# учитываем НДФЛ = 13%
salary_from=[]
salary_to=[]
for x in lst_salary:
    # коэффициент сколько остается "на руки" зависит от gross , если True то минус НДФЛ
    # указана зарплата ОТ/ДО применяем коэфф
    # если не указано ОТ / ДО , устанваливаем минимум в 15 000 и максимум в 500 000
    if not x:   # если вообще ничего не указано
        salary_from.append(15000)
        salary_to.append(5*10**5)
        continue

    if x['from'] and x['gross']:
        # указано и ОТ и ДО ВЫЧЕТА НДФЛ
        salary_from.append(x['from']*0.87)
    elif x['from'] and not x['gross']:
        # указано и ОТ и ПОСЛЕ ВЫЧЕТА НДФЛ
        salary_from.append(x['from'])
    elif not x['from'] :
        # не указано  ОТ
        salary_from.append(15000)

    if x['to'] and x['gross']:
        # указано и ДО и ДО ВЫЧЕТА НДФЛ
        salary_to.append(x['to']*0.87)
    elif x['to'] and not x['gross']:
        # указано и ОТ и ДО ВЫЧЕТА НДФЛ
        salary_to.append(x['to'])
    elif not x['to'] :
        salary_to.append(5*10**5)

salary_bottom = round(statistics.median(salary_from),-2)
salary_top = round(statistics.median(salary_to), -2)

# подсчет количества и процентов ключевых навыков
lst_skills = [x['name'] for x in lst_key_skills] # список имен навыков
uniq_skills = list(set(lst_skills)) # список униикальных имен
skills = {'keywords': f'Регионы {reg_word}, Специализация {spec_word}, Текст {text_word}',
          'count' : f'{len(vacancies)}',
          'salary from' : salary_bottom,
          'salary to' : salary_top,
          'requirements': []}

# подготовка и сортировка списка словарей требований к вакансии
lst_requirments=[]
lst_key_requirments=[] # список ключей для сортировки счетчик*10**6 + номер строки *10**6

for x in uniq_skills:
    tek_skill = {}
    tek_skill['name'] = x
    tek_skill['count'] = lst_skills.count(x)
    tek_skill['percent'] = int(tek_skill['count'] / len(vacancies)*100)
    lst_requirments.append(tek_skill)
    key1='000000'+str(tek_skill['count'])
    key2='000000'+str(uniq_skills.index(x))
    lst_key_requirments.append(key1[-6:] + key2[-6:])

lst_key_requirments.sort(reverse=True) # сортировка ключей в обратном порядке

for x in lst_key_requirments:
    #   выбираем из клюа номер строки и добавляем эту строку в skills['requirment']
    skills['requirements'].append(lst_requirments[int(x[-6:])])

print('Результат выбора')
print(f'Количество вакансий {skills["count"]}')
print(f'Медианные зарплаты от {salary_bottom} до {salary_top}')

with open('report.json','w') as f:
    json.dump(skills,fp=f, ensure_ascii=False)
