# the data shapes we send/receive (Pydantic).
from pydantic import BaseModel


class GitHubUser(BaseModel):  # GitHubuser class is inheritng from BaseModel class
    login: str
    name: str
    bio: str | None = None
    avatar_url: str
    following: int=0    
    followers: int = 0
    public_repos: int=0



class Repo(BaseModel):
    name:str
    stars:    int = 0
    forks:    int= 0
    language: str | None=None
    is_fork: bool =False

class Language_stat(BaseModel):
    Name:str 
    percentage: int=0
    
























































# IMPORTANT CONCEPT:
#
# There are TWO separate HTTP conversations in this feature:
#
# 1. Client/Browser -> Our FastAPI server
# 2. Our FastAPI server -> GitHub server
#
# Our FastAPI server is a SERVER when talking to the browser,
# but it becomes a CLIENT when talking to GitHub.
#
#
# FIRST CONVERSATION:
#
# Browser
#    |
#    | GET /users/torvalds
#    v
# Our FastAPI server
#
#
# SECOND CONVERSATION:
#
# Our FastAPI server
#    |
#    | GET https://api.github.com/users/torvalds
#    v
# GitHub server
#
# GitHub then sends its response back to our FastAPI server.
# This response contains GitHub's raw JSON data, potentially
# containing many fields:
#
# {
#     "login": "torvalds",
#     "id": 1024025,
#     "name": "Linus Torvalds",
#     "company": "Linux Foundation",
#     "followers": 200000,
#     "following": 5,
#     "public_repos": 700,
#     ...
# }
#
#
# Our server receives ALL of this GitHub data.
#
# The response_model is NOT used to control what GitHub sends to us.
#
# Instead, the response_model defines what OUR server sends back
# to the original client/browser.
#
#
# We can define our own model:
#
# class GitHubUser(BaseModel):
#     login: str
#     name: str | None = None
#     bio: str | None = None
#     avatar_url: str
#     followers: int = 0
#
#
# This model represents the data that OUR API wants to expose.
#
# So the flow is:
#
# GitHub's raw JSON
#        |
#        | receive
#        v
# Our FastAPI server
#        |
#        | select/map the fields we want
#        v
# GitHubUser (our Pydantic model)
#        |
#        | response_model validates/serializes it
#        v
# Browser/client receives OUR API's JSON
#
#
# Therefore:
#
# GitHub response = data our server RECEIVES
#
# response_model = defines the data our server SENDS BACK
#
#
# The response model is useful because:
#
# 1. CONTRACT:
#    It defines exactly what fields and types clients of OUR API
#    can expect.
#
# 2. CONTROL:
#    We decide which GitHub fields become part of OUR API.
#
# 3. VALIDATION:
#    Pydantic checks that the returned data matches the model.
#
# 4. STABILITY:
#    If GitHub adds many new fields to its API, our API does not
#    automatically expose or depend on all of them.
#
# 5. SAFETY:
#    We avoid accidentally exposing fields that our API did not
#    intend to expose.
#
# IMPORTANT:
#
# We are NOT necessarily "hiding secret GitHub data".
# We are designing our OWN API instead of simply passing
# GitHub's entire response directly to the client.
#
# In short:
#
# GitHub API
#     -> sends raw data to our server
#
# Our server
#     -> transforms/selects the data
#
# response_model
#     -> defines and validates the shape of OUR response
#
# Client
#     -> receives OUR API's clean JSON