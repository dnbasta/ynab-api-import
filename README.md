# ynab-api-import

[![GitHub Release](https://img.shields.io/github/release/dnbasta/ynab-api-import?style=flat)]() 
[![Github Release](https://img.shields.io/maintenance/yes/2100)]()

This library enables importing YNAB transactions via the 
[Gocardless Bank Account Data API (formerly Nordigen)](https://gocardless.com/bank-account-data/). 
It can be helpful for cases in which your bank is not covered by YNABs native import functionality.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/dnbasta)

## Preparations
### Gocardless Bank Account API (formerly Nordigen)
1. [Check](https://gocardless.com/bank-account-data/coverage/) if your bank is supported by the API.
2. Create an account with Gocardless for the Bank Account Data API (They have a separate Login for it which you can 
   get to by clicking on 'Get API Keys' or clicking the link at the bottom of their standard login page)
3. Go to Developers -> User Secrets and create a new pair of secret_id and secret_key
### YNAB
1. Create a personal access token for YNAB as described [here](https://api.ynab.com/)

## Basic Usage
### 1. Install library from PyPI

```bash
pip install ynab-api-import
```
### 2. Initiate Library
Provide a unique reference (e.g. `'mycheckingaccount'`)  per bank connection to identify the grant later on. 
You can find the IDs of your budget and the account if you go to https://app.ynab.com/ and open the target account 
by clicking on the name on the left hand side menu. The URL does now contain both IDs `https://app.ynab.
com/<budget_id>/accounts/<account_id>`
```py
from ynabapiimport import YnabApiImport
ynab_api_import = YnabApiImport(secret_id='<secret_id>', 
                                secret_key='<secret_key>',
                                reference='<reference>',
                                token='<ynab_token>',
                                budget_id='<budget_id>',
                                account_id='<account_id>')
```
Optionally you can initiate an object from a `config.yaml` file. To do that create a YAML file with the following 
content:
```yaml
secret_id: <secret_id>
secret_key: <secret_key>
reference: <reference>
token: <ynab_token>
budget_id: <budget_id>
account_id: <account_id>
```
Save the file and provide the path to the library when initializing
```py
ynab_api_import = YnabApiImport.from_yaml('path/to/config.yaml')
```
### 2. Find the institution_id of your bank
Countrycode is ISO 3166 two-character country code. 
```py

ynab_api_import.fetch_institutions(countrycode='<countrycode>')
```
You get back a dictionary with all available banks in that country and their institution_ids.
Find and save the institution_id of your bank.
```py
[{'name': '<name>', 'institution_id': '<institution_id>'}]
```

### 3. Create Auth Link and authenticate with your bank
Provide the institution_id. You get back a link which you need to copy to your browser and go through authentication 
flow with your bank
```py
ynab_api_import.create_auth_link(institution_id='<institution_id>')
```

### 4. Run import with your reference and YNAB identifiers
Optionally you can provide a `startdate` argument in form of a `datetime.date` object to only import transactions 
from a specific date onwards. Equally optionally you can provide a `memo_regex` argument in from of a regex string 
to the call to clean the memo string before importing into YNAB. A good helper to write your regex is  
https://regex101.com  
```py
ynab_api_import.import_transactions()
```
## Advanced Usage
### Handling of multiple accounts in your bank connection (`MultipleAccountsError`)
The library assumes that you have one active account in your bank connection. It will raise an error if there are no 
accounts in your connection or more than one. In the latter case you need to provide the correct `resource_id` when 
initializing the library. You can find the `resource_id` by looking into the available options in the error message.
```py
from ynabapiimport import YnabApiImport
ynab_api_import = YnabApiImport(resource_id='<resource_id>',
                                secret_id='<secret_id>', 
                                secret_key='<secret_key>',
                                reference='<reference>',
                                token='<ynab_token>',
                                budget_id='<budget_id>',
                                account_id='<account_id>')
```
### Delete current bank authorization
By default you can create only one bank authorization per reference. If you need to replace the authorization under your 
current reference you can explicitly do that by calling the following function.
```py
ynab_api_import.delete_currrent_auth()
```
### Show Logs
The library logs information about the result of the methods on the 'INFO' level. If you want to see these logs 
import the logging module and set it to the level `INFO`. You can also access the logger for advanced configuration 
via the `logger` attribute of your `YnabApiImport`instance.
```py
import logging

logging.basicConfig(level='INFO')
```
### Testing your `memo_regex`
You can test your `memo_regex` with a call to `test_memo_regex()`. The function will fetch transactions from your 
bank account, apply the regex and output the old and new memo strings in a dict for inspection
```py
ynab_api_import.test_memo_regex(memo_regex=r'<memo_regex')
```
returns a list of `dict` with following content
```
[{original_memo: cleaned_memo}]
```


