import requests
from dotenv import load_dotenv
import os
from terminaltables import SingleTable


def get_a_vacancy_form_sj(super_job_secret_key, language):
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


def build_columns_names_and_rows_value_for_tabel(information_about_salaries):
    tabel_columns_names_and_rows_value = list()
    columns_names = [
        "Язык программирования", "Вакансий найдено",
        "Вакансий обработано", "Средняя зарплата"
    ]
    tabel_columns_names_and_rows_value.append(columns_names)
    for it_language in information_about_salaries:
        tabel_columns_names_and_rows_value.append(
            [
                it_language,
                information_about_salaries[it_language]["vacancies_found"],
                information_about_salaries[it_language]["vacancies_processed"],
                information_about_salaries[it_language]["average_salary"]
            ]
        )
    return tabel_columns_names_and_rows_value


def take_general_information_about_salaries_from_sj(
        programming_languages, super_job_secret_key, vacancies_processed,
        average_salary_from_all_vacancies, information_about_salaries_from_sj
):
    for language in programming_languages:
        vacancies_descriptions = get_a_vacancy_form_sj(
            super_job_secret_key, language
        )
        vacancies_found = vacancies_descriptions[0]["total"]
        for vacancy_description in vacancies_descriptions:
            for vacancy in vacancy_description["objects"]:
                average_salary = predict_salary_sj(vacancy)
                if not average_salary:
                    continue
                vacancies_processed += 1
                average_salary_from_all_vacancies += int(average_salary)
                information_about_salaries_from_sj[language] = {
                    "vacancies_found": vacancies_found,
                    "vacancies_processed": vacancies_processed,
                    "average_salary": int(
                            average_salary_from_all_vacancies /
                            vacancies_processed
                        )
                }
        vacancies_processed = 0

    return information_about_salaries_from_sj


def take_general_information_about_salaries_from_hh(
        programming_languages, vacancies_processed,
        average_salary_from_all_vacancies, information_about_salaries_from_hh
):
    for language in programming_languages:
        vacancies_descriptions = take_vacancies_from_hh(language)
        vacancies_found = \
            vacancies_descriptions[0]["clusters"][0]["items"][0]["count"]
        for vacancy_description in vacancies_descriptions:
            for vacancy in vacancy_description["items"]:
                average_salary = predict_salary_hh(vacancy)
                if not average_salary:
                    continue
                vacancies_processed += 1
                average_salary_from_all_vacancies += int(average_salary)
                information_about_salaries_from_hh[language] = {
                    "vacancies_found": vacancies_found,
                    "vacancies_processed": vacancies_processed,
                    "average_salary": int(
                        average_salary_from_all_vacancies /
                        vacancies_processed
                    )
                }
        vacancies_processed = 0
    return information_about_salaries_from_hh


def print_general_table(table, site_name):
    tabel = SingleTable(table)
    tabel.title = site_name
    print(tabel.table)


def main():
    information_about_salaries_from_hh = dict()
    information_about_salaries_from_sj = dict()
    average_salary_from_all_vacancies = 0
    vacancies_processed = 0
    load_dotenv()
    super_job_secret_key = os.environ["SUPER_JOB_KEY"]
    programming_languages = [
        "Python", "JavaScript", "Ruby",
        "PHP", "C", "C++", "Java"
    ]
    information_about_salaries_from_hh = \
        take_general_information_about_salaries_from_hh(
                programming_languages, vacancies_processed,
                average_salary_from_all_vacancies,
                information_about_salaries_from_hh
            )
    information_about_salaries_from_sj = \
        take_general_information_about_salaries_from_sj(
                programming_languages, super_job_secret_key,
                vacancies_processed, average_salary_from_all_vacancies,
                information_about_salaries_from_sj
            )
    tabel_names_and_rows_values = {
            "HeadHunter Moscow": information_about_salaries_from_hh,
            "SuperJob Moscow": information_about_salaries_from_sj
        }
    for sites_names, data_about_salary in \
            tabel_names_and_rows_values.items():
        site_name = sites_names
        table = build_columns_names_and_rows_value_for_tabel(data_about_salary)
        print_general_table(table, site_name)


if __name__ == "__main__":
    main()
