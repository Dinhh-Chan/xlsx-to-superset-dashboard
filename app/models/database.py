from pydantic import BaseModel, Field, validator
from typing import Optional

class EngineInformation(BaseModel):
    disable_ssh_tunneling: bool = Field(..., example=True)
    supports_file_upload: bool = Field(..., example=True)

class DatabaseParameters(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin")
    host: str = Field(..., example="172.17.0.1")
    port: str = Field(..., example="5435")
    database: str = Field(..., example="superset_test")

class SshTunnel(BaseModel):
    id: Optional[int] = Field(None, example=1)
    password: Optional[str] = Field(None, example="your_ssh_password")
    private_key: Optional[str] = Field(None, example="path_to_your_private_key")
    private_key_password: Optional[str] = Field(None, example="your_private_key_password")
    server_address: Optional[str] = Field(None, example="ssh_server_address")
    server_port: Optional[int] = Field(None, example=22)
    username: Optional[str] = Field(None, example="ssh_username")

class DatabaseRequest(BaseModel):
    database_name: str = Field(..., example="abc")
    engine: str = Field(..., example="postgresql")
    configuration_method: str = Field(..., example="dynamic_form")
    engine_information: EngineInformation = Field(..., example={"disable_ssh_tunneling": True, "supports_file_upload": True})
    driver: str = Field(..., example="psycopg2")
    sqlalchemy_uri_placeholder: str = Field(..., example="postgresql://user:password@host:port/dbname[?key=value&key=value...]")
    extra: str = Field(..., example='{"allows_virtual_table_explore":true}')
    expose_in_sqllab: bool = Field(..., example=True)
    parameters: DatabaseParameters = Field(..., example={
        "username": "admin",
        "password": "admin",
        "host": "172.17.0.1",
        "port": "5435",
        "database": "superset_test"
    })
    masked_encrypted_extra: str = Field(..., example="{}")
    ssh_tunnel: Optional[SshTunnel] = Field(None)  # Định nghĩa ssh_tunnel là Optional
    
    @validator('sqlalchemy_uri_placeholder')
    def validate_sqlalchemy_uri_placeholder(cls, v):
        if not (v.startswith("postgresql://") or v.startswith("postgresql+psycopg2://")):
            raise ValueError("sqlalchemy_uri_placeholder phải bắt đầu bằng 'postgresql://' hoặc 'postgresql+psycopg2://'")
        return v
