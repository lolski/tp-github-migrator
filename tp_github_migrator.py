import github as gh
import csv


# https://developer.github.com/v3/issues/#create-an-issue

#### helpers ####
def tp_requirements_to_github_issues(tp_requirements):
    github_issues = []
    for req in tp_requirements:
        print("=====")
        print(req['Description'])
        print("=====")
        issue = {
            'repository': 'grakn-kgms' if req['Project'] == 'Grakn KGMS' else 'grakn-core',                         # grakn-core if project != 'Grakn KGMS', grakn-kgms otherwise
            'title': req['Name'],                                                                                   # name
            'body': req['Description'].replace('\n', '\n\n'),                                                                             # description
            'labels': [req['Project'], req['Request Type']] + (['in progress'] if req['Entity State'] == 'In Progress' else []),    # request type + state
            'assignees': ['lolski', 'haikalpribadi'],                                                                      # assignment TODO: parse and map
        }
        print("===")
        print(issue)
        github_issues.append(issue)

    return github_issues


#### main ####
# details of the migration source
tp_requirement_csv_path = '/Users/lolski/Playground/tp_github/data/tp/Requirements Export.csv'
# details of the migration target
github_user = 'lolski'
github_password = 'p4UbNNQO5ToEBDDJvptO'
github_organisation_name = 'graknlabs'
github_repository_name = 'fake-grakn'

if __name__ == '__main__':
    tp_requirements = list(csv.DictReader(open(tp_requirement_csv_path)))[0:1]
    github_issues = tp_requirements_to_github_issues(tp_requirements)

    print(github_issues)
    github_connection = gh.Github(github_user, github_password)
    github_organisation = github_connection.get_organization(github_organisation_name)
    github_repository = github_organisation.get_repo(github_repository_name)
    for issue in github_issues:
        github_repository.create_issue(title=issue['title'], body=issue['body'], labels=issue['labels'], assignees=issue['assignees'])