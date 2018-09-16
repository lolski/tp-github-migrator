import github as gh

#### settings ####
# migrate TP ticket to Github
organisation_name = 'graknlabs'
repository_name = 'grakn'
# github credential
github_access_token = '4bf38e29e5daf7bde851d93df5150024a4efeab8'

connection = gh.Github(github_access_token)
organisation = connection.get_organization(organisation_name)
repository = organisation.get_repo(repository_name)

for issue in repository.get_issues(state='open'):
    print(issue)