from flask import Flask

app = Flask(__name__)

from routes import *

        
if __name__ == "__main__": #inicializa o servidor ai é só ar play, nao precisa usar o comando do flask no terminal
        app.run(host='0.0.0.0', port=5000, debug=True)  # mas precisa instalar né, garoutos com pip install requirements.txt em um ambiente novo