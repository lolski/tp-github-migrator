import github as gh
import csv


# https://developer.github.com/v3/issues/#create-an-issue

#### helpers ####
def tp_requirements_to_github_issues(tp_requirements):
    def tp_users_to_github_users(tp_users):
        github_users = []
        map = {
            '': '',
            'Ganeshwara Hananda': 'lolski',
            'Haikal Pribadi': 'haikalpribadi',
            'Marco Scoppetta': 'marco-scoppetta',
            'Kasper Piskorski': 'kasper-piskorski',
            'Syed Irtaza Raza': 'Irtazaraza',
            'Joshua Send': 'flyingsilverfin',
            'Jyothish Soman': 'jyosoman',
            'Soroush Saffari': 'sorsaffari',
            'James Fletcher': 'jmsfltchr',
            'Tomas Sabat': 'tomassabat',
        }

        tp_users_as_list = [] if tp_users == '' else tp_users.split(', ')
        for tp_user in tp_users_as_list:
            key = tp_user.replace('(Developer) ', '')
            github_user = map[key]
            github_users.append(github_user)

        return github_users

    github_issues = []
    for req in tp_requirements:
        repository = 'grakn-kgms' if req['Project'] == 'Grakn KGMS' else 'grakn-core'
        project = [req['Project'].lower()]
        request_type = [req['Request Type'].lower()]
        state = ['in progress'] if req['Entity State'] == 'In Progress' else []

        issue = {
            'repository': repository,
            'title': req['Name'],
            'body': req['Description'].replace('\n', '\n\n'),
            'labels': project + request_type + state,
            'assignees': tp_users_to_github_users(req['Assignments']),
        }

        print("=====")
        print(req['Description'])
        print("=====")
        print(issue)
        print("===")

        github_issues.append(issue)

    return github_issues


#### main ####
# details of the migration source
tp_requirement_csv_path = './data/tp/Requirements Export - Edit v2.csv'
# details of the migration target
github_user = 'lolski'
github_password = 'p4UbNNQO5ToEBDDJvptO'
github_organisation_name = 'graknlabs'
github_grakn_core_repository_name = 'fake-grakn'
github_grakn_kgms_repository_name = 'fake-grakn-kgms' # TODO: use

if __name__ == '__main__':
    tp_requirements = list(csv.DictReader(open(tp_requirement_csv_path)))[0:3]
    github_issues = tp_requirements_to_github_issues(tp_requirements)

    print(github_issues)
    github_connection = gh.Github(github_user, github_password)
    github_organisation = github_connection.get_organization(github_organisation_name)
    github_repository = github_organisation.get_repo(github_grakn_core_repository_name)
    for issue in github_issues:
        github_repository.create_issue(title=issue['title'], body=issue['body'], labels=issue['labels'], assignees=issue['assignees']) # TODO: repository