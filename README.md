# MP-IoT (ATTN: PRE-RELEASE)

The Management Plane for IoT encompasses a policy server, a policy database, and a device directory. Centered around the policy server, the policy database stores policies, and the device directory provides contexts, which are necessary for the policy evaluation.

Please cite the following paper if you find this project helpful to your work.

> (TBA) (TBA)

## Setup the Policy Server
You will need MongoDB and Python3 (tested in Python3.10). The virtual environment of Python3 is recommended. 

### Create your MongoDB database

We use MongoDB Atlas as the online database. You can [create an account and deploy a cluster](https://www.mongodb.com/docs/atlas/getting-started/). Then, get the PyMongo connection link to this DB by clicking 'Connect' on the DB deployment and choosing the connection as MongoDB Drivers -> Python 3.6.

Helpful Tip: When adding IP address to trusted list for the cluster, add 0.0.0.0/0 to allow access from any IP address (ONLY FOR TESTING). 

Once the above setup is done, go to `app/mongo_service.py` and change the atlas connection URI.

      atlas_uri = "xxxxxxx"
      db_name = 'xxxxxx'

`db_name` can be randomly picked and when the app is running it would create db with this name and 'things' and 'policies' collections once you register a thing or policy.

### Install dependencies and run the server
Now you can create a virtual environment (e.g., python3 venv or similar) to install dependencies and run the flask server.

Install dependencies by running `pip install -r requirements.txt` under app directory.

Start the app by running `python3 new_app.py`.

#### Potential Issues
You may need to rollback the setuptools version `pip install setuptools==58`

If you face issues with building wheel for cryptography due to open ssl issue then set these flags and retry the installation (might be an issue only in Apple Silicon)

  `export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib"`

  `export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include"`


If you face issues with certificate verification, you may set `tlsAllowInvalidCertificates=True` in `MongoClient` for testing purpose, or you may [install `certifi`](https://stackoverflow.com/questions/68123923/pymongo-ssl-certificate-verify-failed-certificate-verify-failed-unable-to-ge).

## Run Examples
Install [Postman](https://www.postman.com/downloads/) (recommended). The Postman [configuration](https://www.postman.com/red-zodiac-323402/workspace/policy-server-api/collection/14424610-a5cbcbd4-e3e4-4e0c-8e03-4262c53f3a56?action=share&creator=14424610).

Example things, policies, and commands are in the `example` folder. You are supposed to register all of the things and polices, followed by testing each command.

1. Register a thing. 
- **Endpoint**: `http://127.0.0.1:5000/policy_api/register2`
- **Method**: POST
- **Headers**:
  - `Content-Type`: application/json
- **Request Body**:
  - Required:
    - `td` (json): the thing profile.
  - Example:
    ```json
    {
        "td": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "id": "urn:dev:wot:com:smartphone:1",
            "title": "smartphone",
            "@type": "smartphone",
            "links": [
                {
                    "href": "urn:dev:wot:com:noniot:zone:2",
                    "rel": "feeds",
                    "mediaType": "application/td"
                }
            ]
        }
    }
    ```

2. Register a policy. 
- **Endpoint**: `http://127.0.0.1:5000/policy_api/policy/v2`
- **Method**: POST
- **Headers**:
  - `Content-Type`: multipart/form-data
- **Request Body**:
  - Required:
    - `file` (file): The file to be uploaded.
  - Example:
    - the policyX.py file in the `example/policies` folder.

3. Send a command to be evaluated against policies.
- **Endpoint**: `http://127.0.0.1:5000/policy_api/command`
- **Method**: POST
- **Headers**:
  - `Content-Type`: application/json
- **Request Body**:
  - Required:
    - `td` (json): the command.
  - Example:
    ```json
    {
        "objectDevice": {
            "type": "ac",
            "id": "urn:dev:wot:com:ac:1"
        },
        "action": {
            "type": "set",
            "temperature": 55
        }
    }
    ```
    
## Note

1. Front-end is deprecated (though it may still partially work). Please use Postman for demo purposes. 
2. Python3.10 or higher may be required. 

## Acknowledgement
We would like to thank Deepak, Suchit, Yixuan, Shuo for their valuable inputs and contributions on the implementation of this prototype.