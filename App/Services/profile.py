from collections import Counter
from App.Schemas.schema import Portfolio,GitHubUser,Repo,Language_stat
from App.Services.math_functions import _fix_rounding




def compute_portfolio(user_raw: dict,repo_raw: list[dict])-> Portfolio:

    Lang_count=Counter(r["languages"] for r in repo_raw if r.get("languages"))

    
    total=sum (Lang_count.values()) or 1
    #stat return type is:
    # stats
    #     └── list
    #         ├── dict
    #         │    ├── name       → str
    #         │    └── percentage → int
    #         ├── dict
    #         └── ...
    # for example:
    # [
    # {"name": "Python", "percentage": 47},
    # {"name": "C++", "percentage": 24},
    # {"name": "C", "percentage": 18},
    # {"name": "JavaScript", "percentage": 12}
    #  ]
    stats = [{"name": l, "percentage": round(c / total * 100.0)} for l, c in Lang_count.most_common()]
    _fix_rounding(stats) # makes them sum to 100 (see 4.3)

    repos = [Repo(name=r["name"],
                  stars=r.get("stargazers_count", 0),
                  forks=r.get("forks_count", 0),
                  language=r.get("language"),
                  is_fork=r.get("fork", False))
             for r in repo_raw]
    repos.sort(key=lambda r: r.stars, reverse=True)

    return Portfolio(
        user=GitHubUser(username=user_raw["login"],
                        name=user_raw.get("name"),
                        avatar_url=user_raw["avatar_url"],
                        followers=user_raw.get("followers", 0)),
        total_repos=len(repo_raw),
        total_stars=sum(r.stars for r in repos),
        top_languages=[Language_stat(**s) for s in stats[:5]],
        repositories=repos[:20],             # cap for a readable portfolio
    )
#class to fetch portoflio info from github servers and return the json in Portfolio structure
class ProfileService:
    def __init__(self, client):
        self.client = client

    async def get_portfolio(self, username: str) -> Portfolio:
        #get_user method is inherited by GithubClient from App.Client.github, it will be inherited during the dependancy injection in routing process
        user_raw = await self.client.get_user(username)
        #get_respositories method is inherited by GtihubClient from App.Client.github , it will be inherited dependancy injection in routing process
        repos_raw = await self.client.get_repositories(username)
        return compute_portfolio(user_raw, repos_raw)