#filename=config.py
from pydantic_settings import BaseSettings,SettingsConfigDict
USERNAME_REGEX=r"^[a-zA-Z0-9-]+$"
class Settings(BaseSettings):
    github_token:str | None=None
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")#'env_file' is the file path to load the enviroment file from
                                                                    # and the extra is to handling(in this case ignore) extra variables 
settings=Settings() 