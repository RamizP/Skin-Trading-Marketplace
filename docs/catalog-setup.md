# Setting up the catalog

The app includes demo items and accounts on the first startup of an empty database. These steps are optional if you want to add your own catalog items and case rewards.

Start the backend and frontend using the [README](../README.md), then register an account. To start without demo data, set `DEMO_DATA=false` in `src/.env` before the first startup.

## Make your account an admin

Open another terminal at the project root and start Python:

```powershell
cd src/v1
..\..\venv\Scripts\python.exe
```

Paste this into the Python prompt, replacing `your_username`. Enter a blank line after the `with` block:

```python
from auth.models import User, UserRole
from database import SessionLocal

with SessionLocal.begin() as db:
    user = db.query(User).filter(User.username == "your_username").one()
    user.role = UserRole.admin

exit()
```

Sign out and back in so the frontend picks up the new role.

## Create categories and items

Log in through the API and use the returned token in an `Authentication` header. For example, in PowerShell:

```powershell
$credential = Get-Credential -Message "Enter your app username and password"
$loginBody = @{
    username = $credential.UserName
    password = $credential.GetNetworkCredential().Password
} | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/login -ContentType application/json -Body $loginBody
$headers = @{ Authentication = $session.token }
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/category -Headers $headers -ContentType application/json -Body '{"name":"case"}'
```

Use lowercase `case` for the case category. Create another category, such as `rifle`, for reward items. Each response contains the new category ID.

You can now add items through the frontend's admin form or `POST /entities`. For example:

```json
{
  "name": "Starter Case",
  "symbol": "STARTER-CASE",
  "entity_rarity": "uncommon",
  "category_id": 1,
  "image_url": null
}
```

Replace `category_id` with your case category ID. Names and symbols must be unique. Create a reward item in the other category too. Use `GET /entities` to find their IDs.

## Add case drops

Send this to `POST /cases/drops` with your admin token:

```json
{
  "case_entity_id": 1,
  "reward_entity_id": 2,
  "weight": 100
}
```

Replace the IDs with your case and reward IDs. Weights are relative: two rewards with weights `80` and `20` have 80% and 20% chances. A reward cannot be the case itself or another case.

The free-case button needs at least one case in the catalog. Opening a case also needs a configured drop table. Market listings appear when users list their inventory items for sale.
