from project_manager import (
    create_projects_table,
    create_project,
    get_projects
)


create_projects_table()


create_project(
    "jeremiah",
    "Sales Analysis"
)


projects = get_projects(
    "jeremiah"
)


for project in projects:

    print(project)