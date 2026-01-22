# SET-Box-Timer
A streamlit WebApp to introduce gamification features to the SET-Box. For more details on the SET-Box see publication:

If you'd like to get in contact, you'll find an email address in the publication.

## Dependencies
The [streamlit](https://streamlit.io/) library is needed. If you like to save highscores online in a Google Spreadsheet use [gsheet-connections](https://github.com/streamlit/gsheets-connection).

## Your version the SET-Box Timer Webapp
There are two ways to run your own version of the WebApp with highscores from your institution: 
A) (easy, local) Download the repository and run a local server. This approach is recommended if you use a single device for teaching.
B) (advanced, online) Fork this project and set up an online version through the [streamlit Community Cloud](https://streamlit.io/cloud). This allows you to connect teh app to an online database or spreadsheet for highscores (see tutorial below). Choose this approach when you want to be device independent.

### Local streamlit server
1. Download and setup a python distribution. [Anaconda](https://www.anaconda.com/download) is one example.
2. Install dependencies, namely <code>pandas</code> and <code>streamlit</code>. A detailed setup guide is provided by [streamlit Docs](https://docs.streamlit.io/get-started/installation/anaconda-distribution).
3. Download this project to your hard drive.
4. Open the terminal and navigate to the project folder.
5. Run a local streamlit server in the terminal using <code>streamlit run setbox_main.py</code>. A detailed guide is provided [here](https://docs.streamlit.io/develop/concepts/architecture/run-your-app).

Note: For local sessions no secrets management and connection to a database is needed. Highscores are loaded from a local <code>JSON</code> file.

### Streamlit community cloud
If you plan to use the app in different settings and networks and on different devices, as well as collect highscores from multiple sites - this approach is for you. Aside from forking this repository, you will need a [streamlit Community Cloud](https://streamlit.io/cloud) account. Furthermore, you will need online data storage. This app was designed to work with Google Spreadsheets for which a Google service account is needed. However, a variety of data sources can be conneced ([Data Sources for streamlit Apps](https://docs.streamlit.io/develop/tutorials/databases)). Here, the setup with a Google Spreadsheet is explained:
1. Fork this project.
2. Setup an <code>streamlit Community Cloud</code>, connect it to your <code>GitHub Account</code> and create a new app. See [Prep and Deploy your App in the Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
3. Set up a Google service account to access a spreadsheet. Detailed instructions [Connect Streamlit to a private Google Sheet](https://docs.streamlit.io/develop/tutorials/databases/private-gsheet).
4. Set up a <code>secrets.toml</code> file and copy its contents in the secrets section of the settings. For an example see below. Detailed setup instructions can be found [here](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

### Localization / Language support
For now, German and English are supported. The language can be selected on startup. You can localize the app by copying and renaming a file in the <code>translations</code> folder to your language. In each language file (e.g. <code>de.json</code> each piece of text is represented by a key/value-pair in the form of <code>"[key]": "[value]",</code>. Example: <code>"puzzle_help_dialog_title": "Wie geht diese Aufgabe?",</code>. Just translate all the values to your language. If you complete a translation, please get in contact and share it.

### secrets.toml
Your secrets.toml should look like this. Note the worksheet is specified in this example as opposed to the example from the streamlit Docs. 
<code>[connections.gsheets]
spreadsheet = "xxx"
worksheet = "xxx"

type = "service_account"
project_id = "xxx"
private_key_id = "xxx"
private_key = "xxx"
client_email = "xxx"
client_id = "xxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "xxx"
universe_domain = "googleapis.com"
</code>
