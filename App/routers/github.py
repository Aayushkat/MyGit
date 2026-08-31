from fastapi import APIRouter,Depends,Path
from App.Client.github import GithubClient
from App.Schemas.schema import GitHubUser

router=APIRouter(
    prefix="/users",        #prefix is the common URL before every routes of router
    tags=["users"]                  #Metadata for Doumentation organization
    )
#rather than hardcoding the object initiation in the get_user ,using dependancy injection will help us in several ways:Testing.resource management
def get_client()-> GithubClient:
    return GithubClient()# there should be parenthesis or then it will only return the class itlself rather than instance of that class

@router.get("/{username}",response_model=GitHubUser)
async def get_user(
    username:str =Path(...,min_length=1,max_length=39,pattern=r"^[a-zA-Z0-9-]+$"),
    client: GithubClient =Depends(get_client),
    ):
    data=await client.get_user(username)
    return GitHubUser(username=data["login"],
                      name=data.get("name"),
                      bio=data.get("bio"),
                      avatar_url=data.get("avatar_url"),
                      followers=data.get("followers",0),
                    following=data.get("following",0),
                    public_repos=data.get("public_repos",0)
                      )