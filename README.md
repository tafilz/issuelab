# youtrack-to-gitlab
Migrate issues from YouTrack to Gitlab completly

# Requirements
## Python packages
* [requests](https://pypi.org/project/requests/)
* [python-gitlab](https://pypi.org/project/python-gitlab/)
* [youtrack](https://pypi.org/project/youtrack/)

## GitLab
### Member access level
All members have to be `owner` to map the issue id.
### Token
Generate a 'Access Token' for you project you want to migrate to.
* Scopes
  * `api`
  * `sudo` 

## YouTrack
Generate a permanent token.

# Preparation
1. Fill the environment.json
2. Fill the `user_map_id.json` with the YouTrack username and the GitLab user id  
```json
{
    "oliver": 0,
    "john": 1
}
```
3. Fill the `user_map_name.json` with `youtrack_user_name` and the GitLab user name
```json
{
    "oliver": "oliver.queen",
    "john": "john.diggle"
}
```

# Run
`./run.sh`


# TODO
- Better README
- More checks
- Better output (+log file)
- Support GitLab plans
  * Epic support
  * multi assignees
  * ...
