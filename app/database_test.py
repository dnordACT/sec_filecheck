from src.database_mgr import DatabaseManager  # Replace 'your_module' with the actual name of the module where DatabaseManager is defined.

database = DatabaseManager(companies_csv_path="data/company_list.csv")

def test_get_company_info():
    company_table = database.get_company_info()
    return company_table

print(test_get_company_info())