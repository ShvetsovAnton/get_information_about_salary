import requests
from dotenv import load_dotenv
import os
from terminaltables import SingleTable


def get_vacancy_form_sj(super_job_secret_key, language):
    page = 0
    pages_number = 5
    vacancies_on_page = 100
    profession_id = 48
    all_vacancies = list()
    while page < pages_number:
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {
            "count": vacancies_on_page, "keyword": language,
            "catalogues": profession_id, "page": page, "town": "Москва"
        }
        headers = {"X-Api-App-Id": super_job_secret_key}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        description_vacancies = response.json()
        if description_vacancies["objects"]:
            all_vacancies.append(description_vacancies)
        page += 1
    return all_vacancies


def take_vacancies_from_hh(language):
    page = 0
    pages_number = 1
    area_id = 1
    vacancies_on_page = 100
    all_vacancies = list()
    while page < pages_number:
        url = "https://api.hh.ru/vacancies/"
        params = {
            "text": language, "area": area_id,
            "page": page, "per_page": vacancies_on_page, "clusters": "true"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        description_vacancies = response.json()
        pages_number = description_vacancies["pages"]
        all_vacancies.append(description_vacancies)
        page += 1
    return all_vacancies


def predict_salary_sj(vacancy):
    if "rub" not in vacancy["currency"]:
        return
    salary_from = vacancy["payment_from"]
    salary_to = vacancy["payment_to"]
    return predict_salary(salary_from, salary_to)


def predict_salary_hh(vacancy):
    if not vacancy["salary"]:
        return
    if "RUR" not in vacancy["salary"]["currency"]:
        return
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


def build_columns_and_rows_for_tabel(information_about_salaries):
    tabel_columns_and_rows = list()
    columns_names = [
        "Язык программирования", "Вакансий найдено",
        "Вакансий обработано", "Средняя зарплата"
    ]
    tabel_columns_and_rows.append(columns_names)
    for it_language in information_about_salaries:
        tabel_columns_and_rows.append(
            [
                it_language,
                information_about_salaries[it_language]["vacancies_found"],
                information_about_salaries[it_language]["vacancies_processed"],
                information_about_salaries[it_language]["average_salary"]
            ]
        )
    return tabel_columns_and_rows


def creating_dictionary_with_average_salary_based_on_vacancy_from_sj(
        programming_languages, super_job_secret_key
):
    average_salaries_based_on_it_languages_from_sj = dict()
    average_salary_from_all_vacancies = 0
    vacancies_processed = 0
    for language in programming_languages:
        vacancies_descriptions = get_vacancy_form_sj(
            super_job_secret_key, language
        )
        vacancies_found = vacancies_descriptions[0]["total"]
        try:
            for vacancy_description in vacancies_descriptions:
                for vacancy in vacancy_description["objects"]:
                    average_salary = predict_salary_sj(vacancy)
                    if not average_salary:
                        continue
                    vacancies_processed += 1
                    average_salary_from_all_vacancies += int(average_salary)
                    average_salaries_based_on_it_languages_from_sj[language] =\
                        {
                            "vacancies_found": vacancies_found,
                            "vacancies_processed": vacancies_processed,
                            "average_salary": int(
                                average_salary_from_all_vacancies
                                / vacancies_processed
                            )
                        }
            vacancies_processed = 0
        except ZeroDivisionError:
            average_salaries_based_on_it_languages_from_sj[language] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": "Нет данных",
                "average_salary": "Нет данных"
            }
    return average_salaries_based_on_it_languages_from_sj


def take_general_average_salaries_based_on_it_languages_from_hh(
        programming_languages
):
    average_salaries_based_on_it_languages_from_hh = dict()
    average_salary_from_all_vacancies = 0
    vacancies_processed = 0
    for language in programming_languages:
        vacancies_descriptions = take_vacancies_from_hh(language)
        vacancies_found = \
            vacancies_descriptions[0]["clusters"][0]["items"][0]["count"]
        try:
            for vacancy_description in vacancies_descriptions:
                for vacancy in vacancy_description["items"]:
                    average_salary = predict_salary_hh(vacancy)
                    if not average_salary:
                        continue
                    vacancies_processed += 1
                    average_salary_from_all_vacancies += int(average_salary)
                    average_salaries_based_on_it_languages_from_hh[language] =\
                        {
                            "vacancies_found": vacancies_found,
                            "vacancies_processed": vacancies_processed,
                            "average_salary": int(
                                average_salary_from_all_vacancies /
                                vacancies_processed
                            )
                    }
            vacancies_processed = 0
        except ZeroDivisionError:
            average_salaries_based_on_it_languages_from_hh[language] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": "Нет данных",
                "average_salary": "Нет данных"
            }
    return average_salaries_based_on_it_languages_from_hh


def print_general_table(table, site_name):
    tabel = SingleTable(table)
    tabel.title = site_name
    print(tabel.table)


def main():
    load_dotenv()
    super_job_secret_key = os.environ["SUPER_JOB_KEY"]
    programming_languages = [
        "Python", "JavaScript", "Ruby",
        "PHP", "C", "C++", "Java"
    ]
    average_salaries_based_on_it_languages_from_hh = \
        take_general_average_salaries_based_on_it_languages_from_hh(
            programming_languages
        )
    average_salaries_based_on_it_languages_from_sj = \
        creating_dictionary_with_average_salary_based_on_vacancy_from_sj(
            programming_languages, super_job_secret_key
        )
    print(average_salaries_based_on_it_languages_from_sj)
    tabel_names_and_rows = {
        "HeadHunter Moscow": average_salaries_based_on_it_languages_from_hh,
        "SuperJob Moscow": average_salaries_based_on_it_languages_from_sj
    }
    for site_name, average_salary in \
            tabel_names_and_rows.items():
        table = build_columns_and_rows_for_tabel(average_salary)
        print_general_table(table, site_name)


if __name__ == "__main__":
    main()
