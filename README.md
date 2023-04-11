# Jugalbandi API : Factual Question & Answering over arbitrary number of documents

[Jugalbandi API](https://api.jugalbandi.ai/docs) is a system of APIs that allows users to build Q&A style applications on their private and public datasets. The system creates Open API 3.0 specification endpoints using FastAPI.


# 🔧 1. Installation

To use the code, you need to follow these steps:

1. Clone the repository from GitHub: 
    
    ```bash
    git clone git@github.com:OpenNyAI/jugalbandi-api.git
    ```

2. The code requires **Python 3.7 or higher** and some additional python packages. To install these packages, run the following command in your terminal:

    ```bash
    pip install requirements-dev.txt
    ```

3. You will need a GCP account to store the uploaded documents & indices in a bucket and to host a postgres connection to store the api logs.

4. Navigate to the repository directory. Create a file named **gcp_credentials.json** which will contain the service account credentials of your GCP account. The file will roughly have the same format mentioned below.

    ```bash
    {
      "type": "service_account",
      "project_id": "<your-project-id>",
      "private_key_id": "<your-private-key-id>",
      "private_key": "<your-private-key>",
      "client_email": "<your-client-email>",
      "client_id": "<your-client-id>",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "<your-client-cert-url>"
    }
    ```

5. In addition to creating gcp_credentials.json file, create another file **.env** which will hold the development credentials and add the following variables. Update the openai_api_key, path to gcp_credentials.json file, gcp_bucket_name and your db connections appropriately.

    ```bash
    OPENAI_API_KEY=<your_openai_api_key>
    GOOGLE_APPLICATION_CREDENTIALS=<path-to-gcp_credentials.json>
    BUCKET_NAME=<your_gcp_bucket_name>
    DATABASE_NAME=<your_db_name>
    DATABASE_USERNAME=<your_db_username>
    DATABASE_PASSWORD=<your_db_password>
    DATABASE_IP=<your_db_public_ip>
    DATABASE_PORT=5432
    ```

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in home directory of the repository in terminal

```bash
uvicorn main:app
```

# 🚀 3. Deployment

This repository comes with a Dockerfile. You can use this dockerfile to deploy your version of this application to Cloud Run.
Make the necessary changes to your dockerfile with respect to your new changes. (Note: The given Dockerfile will deploy the base code without any error, provided you added the required environment variables (mentioned in the .env file) to either the Dockerfile or the cloud run revision)

# 👩‍💻 4. Usage

To directly use the Jugalbandi APIs without cloning the repo, you can follow below steps to get you started:

1.  Visit [https://api.jugalbandi.ai/docs](https://api.jugalbandi.ai/docs).
2.  Scroll to the `/upload-files` endpoint to upload the documents.
3.  Once you have uploaded file(s) you should have received a `uuid number` for that document set. Please keep this number handy as it will be required for you to query the document set.
4.  Now that you have the `uuid number` you should scroll up to select the query endpoint you want to use. Currently, there are three different implementations we support i.e. `query-with-gptindex`, `query-with-langchain` (recommended), `query-using-voice` (recommended for voice interfaces). While you can use any of the query systems, we are constantly refining our langchain implementation.
5.  Use the `uuid number` and do the query.

## Feature request and contribution

*   We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
*   Kindly visit our project board to see what is it that we are prioritizing.

 
