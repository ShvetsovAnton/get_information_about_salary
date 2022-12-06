import requests
from dotenv import load_dotenv
import os
from terminaltables import SingleTable


def get_a_vacancy_form_sj(super_job_secret_key, language):
    page = 0
    pages_number = 5
    all_vacancies = []
    while page < pages_number:
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {
            "count": 100, "keyword": language,
            "catalogues": 48, "page": page, "town": "Москва"
        }
        headers = {"X-Api-App-Id": super_job_secret_key}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        if response.json()["objects"]:
            all_vacancies.append(response.json())
        page += 1
    return all_vacancies


def take_vacancies_from_hh(language):
    page = 0
    pages_number = 1
    all_vacancies = []
    while page < pages_number:
        url = "https://api.hh.ru/vacancies/"
        params = {
            "text": language, "area": 1,
            "page": page, "per_page": 100, "clusters": "true"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        pages_number = response.json()["pages"]
        all_vacancies.append(response.json())
        page += 1
    return all_vacancies


def predict_salary_sj(vacancy):
    if "rub" in vacancy["currency"]:
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]
        return predict_salary(salary_from, salary_to)


def predict_salary_hh(vacancy):
    if vacancy["salary"]:
        if "RUR" in vacancy["salary"]["currency"]:
            salary_from = vacancy["salary"]["from"]
            salary_to = vacancy["salary"]["to"]
            return predict_salary(salary_from, salary_to)


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    elif salary_from and salary_to == 0:
        return None
    else:
        return None


def collect_information_about_vacancies(
        vacancies_found, average_salary_from_all_vacancies,
        vacancies_processed, language, general_information
):
    general_information[language] = {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": int(
            average_salary_from_all_vacancies / vacancies_processed
        )
    }
    return general_information


def preparing_information_for_the_table(general_information):
    language_columns = list()
    information_for_tables = list()
    information_for_tables.append(
        ["Язык программирования", "Вакансий найдено",
         "Вакансий обработано", "Средняя зарплата"]
    )
    for language in general_information:
        language_columns.append(language)
        information_for_tables.append(
            [
                language, general_information[language]["vacancies_found"],
                general_information[language]["vacancies_processed"],
                general_information[language]["average_salary"]
            ]
        )
    return information_for_tables


def get_general_information_from_sj(
        programming_languages, super_job_secret_key,vacancies_processed,
        average_salary_from_all_vacancies, general_information
):
    for language in programming_languages:
        vacancies_descriptions = get_a_vacancy_form_sj(
            super_job_secret_key, language
        )
        vacancies_found = vacancies_descriptions[0]["total"]
        for vacancy_description in vacancies_descriptions:
            for vacancy in vacancy_description["objects"]:
                average_salary = predict_salary_sj(vacancy)
                if average_salary:
                    vacancies_processed += 1
                    average_salary_from_all_vacancies += int(average_salary)
                    general_information = collect_information_about_vacancies(
                        vacancies_found, average_salary_from_all_vacancies,
                        vacancies_processed, language, general_information)
        vacancies_processed = 0

    return general_information


def get_general_information_from_hh(
        programming_languages, vacancies_processed,
        average_salary_from_all_vacancies, general_information
):
    for language in programming_languages:
        vacancies_descriptions = take_vacancies_from_hh(language)
        vacancies_found = \
            vacancies_descriptions[0]["clusters"][0]["items"][0]["count"]
        for vacancy_description in vacancies_descriptions:
            for vacancy in vacancy_description["items"]:
                average_salary = predict_salary_hh(vacancy)
                if average_salary:
                    vacancies_processed += 1
                    average_salary_from_all_vacancies += int(average_salary)
                    general_information = collect_information_about_vacancies(
                        vacancies_found, average_salary_from_all_vacancies,
                        vacancies_processed, language, general_information
                    )
        vacancies_processed = 0
    return general_information


def print_general_table(general_information, title):
    table = preparing_information_for_the_table(general_information)
    draw_tabel = SingleTable(table)
    draw_tabel.title = title
    print(draw_tabel.table)


def main():
    information_for_tables = list()
    general_information_hh = dict()
    general_information_sj = dict()
    average_salary_from_all_vacancies = 0
    vacancies_processed = 0
    load_dotenv()
    super_job_secret_key = os.environ["SUPER_JOB_KEY"]
    programming_languages = [
        "Python", "JavaScript", "Ruby",
        "PHP", "C", "C++", "Java"
    ]
    information_for_tables.append(
        [
            [
            "HeadHunter Moscow",
            get_general_information_from_hh(
                programming_languages, vacancies_processed,
                average_salary_from_all_vacancies, general_information_hh
            )
            ],
            [
            "SuperJob Moscow",
            get_general_information_from_sj(
                programming_languages, super_job_secret_key,
                vacancies_processed, average_salary_from_all_vacancies,
                general_information_sj
            )
            ]
        ]

    )

    for information_for_table in information_for_tables[0]:
        title = information_for_table[0]
        general_information = information_for_table[1]
        print_general_table(general_information, title)


if __name__ == "__main__":
    main()
