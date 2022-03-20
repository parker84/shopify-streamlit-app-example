
# A Simple Streamlit/Flask Shopify App

This repos is forked from [garettB/shopify-flask-example](https://github.com/garettB/shopify-flask-example) and adds a streamlit dashboard onto the Shopify App.

## What does this repo do?

This repo will create the server-side component for your Shopify app + the ability to pass a user to a streamlit dashboard for their shop and provide you some basic tools which you can build on to create a robust commercial application.

<img width="1449" alt="image" src="https://user-images.githubusercontent.com/12496987/159172778-ef01974f-fc60-49ee-bb0a-9e18b6105f26.png">


## Setup

### Step 1: Get the App Running Locally
(this section is the same as [garettB/shopify-flask-example](https://github.com/garettB/shopify-flask-example))

1. Install dependencies
```
pip3 install -r requirements.txt
```

2. Run the app locally. If you are located in the root directory:
```
python3 flask/server.py
```
Leave this running. If new changes fail to appear, restart the server.

3. Set up [ngrok](https://ngrok.com/) by installing it and running it locally.
```
ngrok http 5001
```
Throughout the development process, ngrok should be running in the background. You will not need to restart this, as you will generate a new URL.

4. Set up your Shopify app, following [these](https://github.com/garettB/shopify-flask-example#app-creation) steps.

5. Create a local `.env` file by copying over the template
```
cp ./flask/.env.template ./flask/.env
```

6. Fill out your `.env` file using your Shopify API key and Shopify secret key. Replace `your_server.hostname` with your ngrok base URL. Do not put quotations around the values.

7. Install the app onto a Shopify test store by following [these](https://github.com/garettB/shopify-flask-example#ready-to-test) steps. If you do not have one, create one.

8. You should be redirected to the admin dashboard of your test store. The url should be formatted as follows
```
https://{{store_name}}.myshopify.com/admin/apps/{{app_name}}/app_launched
```

### Step 2: Get the App Running On Heroku
Install the heroku command line: https://devcenter.heroku.com/categories/command-line

```sh
# Create a remote heroku repo
heroku git:remote -a shopify-streamlit
# Launch a free tier dyno
heroku ps:scale web=1
# Push your local main branch up to heroku
git push heroku main
# Or push a specific branch
git push heroku new/connecting_w_streamlit_dyno:main

# Add all your .env variables as environmental variables in heroku:
heroku config:set SHOPIFY_API_KEY=<your_api_key>
# repeating for the rest of the .env variables
```

### Step 3: Get your Streamlit Dashboard Running on Heroku
See details here: https://github.com/parker84/shopify-streamlit-dashboard
Once it's up and running be sure to add the url to that dashboard into your environmental variables for this app
```sh
# example:
heroku config:set DASHBOARD_REDIRECT_URL=https://shoplit-dash.herokuapp.com
```

## Understanding Each Component
For more details on each component see here: https://github.com/garettB/shopify-flask-example#serverpy

The only changes we make to these components are:
1. Rather than showing the index page for shops that have successfully installed the app, we redirect them to the streamlit dashboard.
2. We add a `dash_auth` function which uses [Cryptographic nonce](https://en.wikipedia.org/wiki/Cryptographic_nonce) to authenticate the user on the streamlit dashboard.
