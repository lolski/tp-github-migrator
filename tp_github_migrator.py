import github as gh
import csv
import requests
import json

# https://developer.github.com/v3/issues/#create-an-issue

#### helpers ####
def get_github_comments_from_tp_requirement(tp_requirement_id):
    tp_url = "https://work.grakn.ai/api/v1/assignables/{}/comments".format(tp_requirement_id)
    tp_querystring = {"format": "json"}
    tp_headers = {
        'Authorization': "Basic Z2FuZXNoOkRlNXYzcjFncg==",
        'Cache-Control': "no-cache",
        'Postman-Token': "5d9693d3-0177-405f-8080-ccbad8663b9f"
    }
    tp_response = requests.request("GET", tp_url, headers=tp_headers, params=tp_querystring)
    tp_response_json = json.loads(tp_response.text)

    github_comments = []
    for tp_comment in tp_response_json['Items']:
        tp_original_poster = tp_comment['Owner']['FirstName'] + ' ' + tp_comment['Owner']['LastName']
        gh_comment = '~This comment was originally posted by {} on {}~.\n\n{}'.format(tp_original_poster, tp_comment['CreateDate'], tp_comment['Description'])
        github_comments.append(gh_comment)
    return github_comments

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
            'comments': get_github_comments_from_tp_requirement(tp_req['ID'])
        }

        github_issues.append(gh_issue)

    return github_issues


#### main ####
# details of the migration source
tp_requirement_csv_path = './data/tp/Requirements Export - Edit v2.csv'
tp_user = 'ganesh'
tp_password = 'CPelZ1iGaUNPqMII7rGr'

# details of the migration target
github_user = 'lolski'
github_password = 'p4UbNNQO5ToEBDDJvptO'
github_organisation_name = 'graknlabs'

if __name__ == '__main__':
    tp_requirements = list(csv.DictReader(open(tp_requirement_csv_path)))[0:3]
    github_issues = tp_requirements_to_github_issues(tp_requirements)

    # ALWAYS pass in a user/pass instead of an OAuth credential.
    # As of PyGithub==1.43.2, there is a bug which will cause create_issue() to fail with 404 if an OAuth credential is used.
    github_connection = gh.Github(github_user, github_password)
    github_organisation = github_connection.get_organization(github_organisation_name)
    print('migrating the following TP tickets as Github issues:')
    for issue in github_issues:
        key = issue['repository']
        target_repo = github_organisation.get_repo(key)
        print('repository = {}, title = {}..., body = {}..., labels = {}, assignees = {}'.format(key, issue['title'][0:20], issue['body'][0:20], issue['labels'], issue['assignees']))
        for gh_comment in issue['comments']:
            print(' - comment: ...{}...'.format(gh_comment.replace('\n', '')[100:240]))
        # target_repo.create_issue(title=issue['title'], body=issue['body'], labels=issue['labels'], assignees=issue['assignees']) # TODO: repository

    print('done.')