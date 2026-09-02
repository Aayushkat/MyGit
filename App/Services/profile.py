from collections import counter 
from App.Schemas.schema import Portfolio,GitHubUser,Repo,Language_stat

def computer_portfolio(user_raw: dict,repo_raw: list[dict])-> Portfolio:
    Lang_count=counter(r["laguages"] for r in repo_raw if r.get("languages"))
    total=sum (Lang_count.values()) or 1

    stats = [{"name": l, "percentage": round(c / total * 100.0)} for l, c in Lang_count.most_common()]
#________________________ have to write the rounding functions afterwards

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