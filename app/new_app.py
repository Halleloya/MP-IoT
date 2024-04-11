from flask import Flask
from views.policy_api import policy_api
from views.dashboard import dashboard
from config import config_dict

def main(init_db=True, debug=True, host='localhost'):
    app = Flask(__name__)
    app.register_blueprint(dashboard, url_prefix = '/')
    app.register_blueprint(policy_api, url_prefix = '/policy_api')
    app.config.update(**config_dict)
    print(app.config)
    app.run(debug = True, host= host, port= app.config["server_port"])

if __name__ == "__main__":
    main()

