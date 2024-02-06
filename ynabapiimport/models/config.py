from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Config:
    secret_id: str
    secret_key: str
    path: Path
    institution_id: str
    token: str
    budget_id: str
    account_id: str

    @classmethod
    def from_path(cls, path: Path):
        with path.open('r') as f:
            config_dict = yaml.safe_load(f)
            return cls(secret_id=config_dict['secret_id'],
                       secret_key=config_dict['secret_key'],
                       institution_id=config_dict['institution_id'],
                       token=config_dict['token'],
                       budget_id=config_dict['budget_id'],
                       account_id=config_dict['account_id'],
                       path=path)
