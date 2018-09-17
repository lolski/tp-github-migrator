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

    def determine_github_repository(project):
        if project == 'Grakn KGMS':
            return 'fake-grakn-kgms'
        elif project == 'Examples':
            return 'fake-examples'
        elif project == 'Benchmark':
            return 'fake-benchmark'
        elif project == 'Research':
            return 'fake-research'
        elif project == 'POC':
            return 'fake-poc'
        else: # Grakn Core, CI/CD, Clients (Java, Python, Node.js), Workbase
            return 'fake-grakn'

    github_issues = []
    for tp_req in tp_requirements:
        gh_repository = determine_github_repository(tp_req['Project'])
        gh_project = [tp_req['Project'].lower()]
        gh_request_type = [tp_req['Request Type'].lower()]
        gh_state = ['in progress'] if tp_req['Entity State'] == 'In Progress' else []

        gh_issue = {
            'repository': gh_repository,
            'title': tp_req['Name'],
            'body': tp_req['Description'].replace('\n', '\n\n'),
            'labels': gh_project + gh_request_type + gh_state,
            'assignees': tp_users_to_github_users(tp_req['Assignments']),
        }

        github_issues.append(gh_issue)

    return github_issues


#### main ####
# details of the migration source
tp_requirement_csv_path = './data/tp/Requirements Export - Edit v2.csv'
# details of the migration target
github_user = 'lolski'
github_password = 'p4UbNNQO5ToEBDDJvptO'
github_organisation_name = 'graknlabs'

if __name__ == '__main__':
    tp_requirements = list(csv.DictReader(open(tp_requirement_csv_path)))[0:3]
    github_issues = tp_requirements_to_github_issues(tp_requirements)

    github_connection = gh.Github(github_user, github_password)
    github_organisation = github_connection.get_organization(github_organisation_name)
    print('migrating the following TP tickets as Github issues:')
    for issue in github_issues:
        key = issue['repository']
        target_repo = github_organisation.get_repo(key)
        print('repository = {}, title = {}, body = {}, labels = {}, assignees = {}'.format(key, issue['title'][0:20] + '...', issue['body'][0:20] + '...', issue['labels'], issue['assignees']))
        # target_repo.create_issue(title=issue['title'], body=issue['body'], labels=issue['labels'], assignees=issue['assignees']) # TODO: repository

    print('done.')