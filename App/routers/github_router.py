from fastapi import APIRouter,Depends,Path
from App.Client.github import GithubClient
from App.Schemas.schema import GitHubUser
from App.Schemas.schema import Portfolio
from App.Services.profile  import ProfileService
from App.config import USERNAME_REGEX

router=APIRouter(
    prefix="/users",        #prefix is the common URL before every routes of router
    tags=["users"]                  #Metadata for Doumentation organization
    )
#DEPENDANCY INJECTION
#rather than hardcoding the object initiation in the get_user ,using dependancy injection will help us in several ways:Testing.resource management
def get_client()-> GithubClient:
    return GithubClient()# there should be parenthesis or then it will only return the class itself rather than instance of that class





# Dependency injection for ProfileService.
# Instead of creating a new GithubClient instance here, we reuse the one
# already created by get_client() (via Depends) — avoids duplicate instances
# and lets both routes share the same client.
def get_service(client_: GithubClient = Depends(get_client)) -> ProfileService:
    return ProfileService(client=client_)
#__________________________________________________________________________________________________________________________________________

@router.get("/{username}",response_model=GitHubUser)
async def get_user(
    username:str =Path(...,min_length=1,max_length=39,pattern=USERNAME_REGEX),
    client: GithubClient =Depends(get_client),
    ):
    data=await client.get_user(username)
    return GitHubUser(login=data.get("login"),
                      name=data.get("name"),
                      bio=data.get("bio"),
                      avatar_url=data.get("avatar_url"),
                      followers=data.get("followers",0),
                    following=data.get("following",0),
                    public_repos=data.get("public_repos",0)
                      )
#__________________________________________________________________________________________________________________________________________
@router.get("/{username}/portfolio",response_model=Portfolio)
async def portfolio(
    username: str = Path(..., min_length=1, max_length=39, pattern=USERNAME_REGEX),
    service: ProfileService = Depends(get_service)
    ):
        return await service.get_portfolio(username)