from fastapi import APIRouter,Depends,Path
from fastapi.responses import HTMLResponse
from App.Client.github import GithubClient
from App.Schemas.schema import GitHubUser

router=APIRouter(
    prefix="/users",        #prefix is the common URL before every routes of router
    tags=["users"]                  #Metadata for Doumentation organization
    )
#rather than hardcoding the object initiation in the get_user ,using dependancy injection will help us in several ways:Testing.resource management
def get_client()-> GithubClient:
    return GithubClient()# there should be parenthesis or then it will only return the class itlself rather than instance of that class

@router.post("/{username}",response_class=HTMLResponse)
async def get_user(
    username:str =Path(...,min_length=1,max_length=39,pattern=r"^[a-zA-Z0-9-]+$"),
    client: GithubClient =Depends(get_client),
    ):
    data=await client.get_user(username)
    return f"""

<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">


<title>{data.get("login", "GitHub User")} | GitHub Profile</title>

<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;

        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI",
            Helvetica, Arial, sans-serif;

        background: #0d1117;
        color: #f0f6fc;

        padding: 30px;
    }}

    .profile-card {{
        width: 100%;
        max-width: 700px;

        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 18px;

        padding: 40px;

        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.4);

        text-align: center;
    }}

    /* Avatar */

    .avatar {{
        width: 150px;
        height: 150px;

        border-radius: 50%;

        border: 4px solid #30363d;

        object-fit: cover;

        margin-bottom: 20px;

        box-shadow:
            0 0 0 6px rgba(88, 166, 255, 0.08);
    }}

    /* Username */

    .username {{
        font-size: 30px;
        font-weight: 700;

        margin-bottom: 5px;
    }}

    .login {{
        color: #8b949e;
        font-size: 17px;

        margin-bottom: 20px;
    }}

    /* Bio */

    .bio {{
        color: #c9d1d9;

        font-size: 16px;
        line-height: 1.6;

        max-width: 550px;

        margin: 0 auto 30px;
    }}

    .no-bio {{
        color: #6e7681;
        font-style: italic;
    }}

    /* Statistics */

    .stats {{
        display: grid;

        grid-template-columns:
            repeat(3, 1fr);

        gap: 15px;

        margin-top: 25px;
    }}

    .stat {{
        background: #0d1117;

        border: 1px solid #30363d;

        border-radius: 12px;

        padding: 20px 10px;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }}

    .stat:hover {{
        transform: translateY(-4px);

        border-color: #58a6ff;
    }}

    .stat-number {{
        display: block;

        font-size: 25px;
        font-weight: 700;

        color: #f0f6fc;

        margin-bottom: 5px;
    }}

    .stat-label {{
        color: #8b949e;

        font-size: 13px;
    }}

    /* Follow information */

    .follow-info {{
        display: flex;

        justify-content: center;

        gap: 35px;

        margin-top: 25px;

        color: #8b949e;

        font-size: 14px;
    }}

    .follow-info strong {{
        color: #f0f6fc;
    }}

    /* GitHub button */

    .github-link {{
        display: inline-block;

        margin-top: 30px;

        padding: 11px 22px;

        background: #238636;

        color: white;

        text-decoration: none;

        font-weight: 600;

        border-radius: 8px;

        transition:
            background 0.2s ease,
            transform 0.1s ease;
    }}

    .github-link:hover {{
        background: #2ea043;

        transform: translateY(-2px);
    }}

    /* Mobile */

    @media (max-width: 600px) {{

        body {{
            padding: 15px;
        }}

        .profile-card {{
            padding: 25px 18px;
        }}

        .avatar {{
            width: 120px;
            height: 120px;
        }}

        .username {{
            font-size: 24px;
        }}

        .stats {{
            grid-template-columns: 1fr;
        }}

        .follow-info {{
            gap: 20px;
        }}
    }}
</style>


</head>

<body>


<main class="profile-card">

    <img
        class="avatar"
        src="{data.get("avatar_url", "")}"
        alt="{data.get("login", "GitHub")} avatar"
    >

    <h1 class="username">
        {data.get("name") or data.get("login", "Unknown User")}
    </h1>

    <p class="login">
        @{data.get("login", "unknown")}
    </p>

    <p class="bio">
        {data.get("bio") or '<span class="no-bio">No bio available</span>'}
    </p>

    <section class="stats">

        <div class="stat">
            <span class="stat-number">
                {data.get("followers", 0)}
            </span>

            <span class="stat-label">
                Followers
            </span>
        </div>

        <div class="stat">
            <span class="stat-number">
                {data.get("following", 0)}
            </span>

            <span class="stat-label">
                Following
            </span>
        </div>

        <div class="stat">
            <span class="stat-number">
                {data.get("public_repos", 0)}
            </span>

            <span class="stat-label">
                Public Repositories
            </span>
        </div>

    </section>

    <div class="follow-info">

        <span>
            <strong>{data.get("followers", 0)}</strong>
            followers
        </span>

        <span>
            <strong>{data.get("following", 0)}</strong>
            following
        </span>

    </div>

    <a
        class="github-link"
        href="{data.get("html_url", "#")}"
        target="_blank"
        rel="noopener noreferrer"
    >
        View on GitHub
    </a>

</main>


</body>
</html>
"""

    
    ''' return GitHubUser(login=data.get("login"),
                      name=data.get("name"),
                      bio=data.get("bio"),
                      avatar_url=data.get("avatar_url"),
                      followers=data.get("followers",0),
                      following=data.get("following",0),
                      public_repos=data.get("public_repos",0))'''
