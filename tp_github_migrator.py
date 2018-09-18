import github as gh
import csv
import requests
import json
import base64
import html
import bs4
# https://developer.github.com/v3/issues/#create-an-issue


#### helpers ####
def get_github_comments_from_tp_requirement(tp_user, tp_password, tp_requirement_id):
    def str_replace_tp_mention_to_github_mention(original_string):
        map = {
            '@user:ganesh[Ganeshwara Hananda]': '@lolski',
            '@user:ganesh[Ganeshwara Herawan Hananda]': '@lolski',
            '@user:haikal[Haikal Pribadi]': '@haikalpribadi',
            '@user:haikal@grakn.ai[Haikal Pribadi]': '@haikalpribadi',
            '@user:marco[Marco Scoppetta]': '@marco-scoppetta',
            '@user:kasper[Kasper Piskorski]': '@kasper-piskorski',
            '@user:syed[Syed Irtaza Raza]': '@Irtazaraza',
            '@user:joshua[Joshua Send]': '@flyingsilverfin',
            '@user:jyothish[Jyothish Soman]': '@jyosoman',
            'Soroush Saffari': '@sorsaffari',
            '@user:james[James Fletcher]': '@jmsfltchr',
            '@user:tomas[Tomas Sabat]': '@tomassabat',
        }

        replaced_string = original_string
        for key in map:
            replaced_string = replaced_string.replace(key, map[key])
        return replaced_string

    tp_url = "https://work.grakn.ai/api/v1/assignables/{}/comments".format(tp_requirement_id)
    tp_querystring = {"format": "json"}
    basic_auth = base64.b64encode(bytes("{}:{}".format(tp_user, tp_password), 'utf-8')).decode()
    tp_headers = { 'Authorization': "Basic {}".format(basic_auth) }
    tp_response = requests.request("GET", tp_url, headers=tp_headers, params=tp_querystring)
    tp_response_json = json.loads(tp_response.text)

    github_comments = []
    for tp_comment in tp_response_json['Items']:
        tp_original_poster = tp_comment['Owner']['FirstName'] + ' ' + tp_comment['Owner']['LastName']
        gh_comment_raw = '_This comment was originally posted by {} on {}_.\n\n{}'.format(tp_original_poster, tp_comment['CreateDate'], tp_comment['Description'])
        gh_comment_unescape = html.unescape(gh_comment_raw)
        gh_comment_stripped = bs4.BeautifulSoup(gh_comment_unescape, 'html.parser').get_text()
        gh_comment_mention = str_replace_tp_mention_to_github_mention(gh_comment_stripped)
        github_comments.append(gh_comment_mention)
    return github_comments


def tp_requirements_to_github_issues(tp_user, tp_password, tp_requirements):
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
            'comments': get_github_comments_from_tp_requirement(tp_user, tp_password, tp_req['ID'])
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

migrate_from_inclusive = 0
migrate_to_exclusive = 3

if __name__ == '__main__':
    tp_requirements = list(csv.DictReader(open(tp_requirement_csv_path)))[migrate_from_inclusive:migrate_to_exclusive]
    github_issues = tp_requirements_to_github_issues(tp_user, tp_password, tp_requirements)

    # ALWAYS pass in a user/pass instead of an OAuth credential.
    # As of PyGithub==1.43.2, there is a bug which will cause create_issue() to fail with 404 if an OAuth credential is used.
    github_connection = gh.Github(github_user, github_password)
    github_organisation = github_connection.get_organization(github_organisation_name)

    print('migrating the following TP tickets as Github issues:')
    count = migrate_from_inclusive
    for issue in github_issues:
        key = issue['repository']
        target_repo = github_organisation.get_repo(key)
        print('{}. repository = {}, title = {}..., body = {}..., labels = {}, assignees = {}'.format(count, key, issue['title'][0:20], issue['body'][0:20], issue['labels'], issue['assignees']))
        created_issue = target_repo.create_issue(title=issue['title'], body=issue['body'], labels=issue['labels'], assignees=issue['assignees']) # TODO: repository
        for gh_comment in issue['comments']:
            print(' - comment: ...{}...'.format(gh_comment.replace('\n', '')[100:240]))
            created_issue.create_comment(gh_comment)

        count += 1

    print('issue no. {} to {} has been migrated. you can continue from issue no. {}'.format(migrate_from_inclusive, migrate_to_exclusive-1, migrate_to_exclusive))