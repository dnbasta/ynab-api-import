# ynab-import

[![GitHub Release](https://img.shields.io/github/release/dnbasta/ynab-import?style=flat)]() 

This library enables importing YNAB transactions via the 
[Gocardless Bank Account Data API (formerly Nordigen)](https://gocardless.com/bank-account-data/).

## Preparations
1. Create an account with Gocardless for the Bank Account Data API (They have a separate Login for it which you can 
get to by clicking on 'Get API Keys' or clicking the link at the bottom of their standard login page)
2. Create a personal access token for YNAB as described [here](https://api.ynab.com/)

## Install library from PyPI

```bash
pip install ynab-import
```

## Create `config.yaml`
Create a file with below content. 

You can find the ID of the budget and of the account if you go to https://app.ynab.com/ and open the target account by
clicking on the name on the left hand side menu. The URL does now contain both IDs 
`https://app.ynab.com/<budget_id>/accounts/<account_id>`

Save the file at a convenient place and provide the path to the library when initializing
```yaml
secret_id: <secret_id>
secret_key: <secret_key>
institution_id: <institution_id>
token: <ynab_token>
budget_id: <budget_id>
account_id: <account_id>
```

## Usage
### 1. Create a transaction

```py
from ynabimport import YnabImport

ynab_import = YnabImport('path/to/config.yaml')
ynab_import.run()
```
## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
