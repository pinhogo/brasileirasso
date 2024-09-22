from main import app
from flask import Response, jsonify, request, render_template
from functools import wraps
import json
from dotmap import DotMap
from collections import OrderedDict
from security import require_api_key 

dados = 'brasileirasso.json'
with open(dados, 'r', encoding='utf-8') as f:
    dados_json = json.load(f)
brasileirasso = DotMap(dados_json)

@app.route('/', methods=['GET']) #rota de acesso a famosa home
def start():
    return render_template('index.html')

@app.route('/<string:year>', methods=['GET', 'POST', 'DELETE'])
@require_api_key(['POST'])
def tableyear(year):
        if request.method == 'GET':
            for yearjs, data_year in brasileirasso.items():
                if yearjs == year:
                    response = Response(json.dumps(data_year.toDict(), ensure_ascii=False), content_type='application/json; charset=utf-8')
                    return response
        elif request.method == 'POST':
            max_year = max(int(y) for y in brasileirasso.keys())
            if int(year) == max_year + 1:
                last_year_data = brasileirasso[str(max_year)]
                new_year_data = {team: {
                    'position': None,
                    'points': None,
                    'games': None,
                    'wins': None,
                    'draws': None,
                    'losses': None,
                    'goals_sc': None,
                    'goals_ag': None,
                    'goals_diff': None,
                    'perc_points': None
            } for team in last_year_data.keys()}
            brasileirasso[str(year)] = new_year_data
            with open(dados, 'w', encoding='utf-8') as f:
                json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)
            return jsonify({"message": f"Year {year} added successfully"}), 201
        
        elif request.method == 'DELETE':
        # Implementar a lógica para deletar o ano, se for o mais antigo
        if not brasileirasso:
            return jsonify({"error": "No years available to delete"}), 400

        # Encontrar o ano mais antigo
        oldest_year = min(int(y) for y in brasileirasso.keys())
        oldest_year_str = str(oldest_year)

        if year != oldest_year_str:
            return jsonify({"error": f"Only the oldest year ({oldest_year_str}) can be deleted"}), 403

        # Deletar o ano
        del brasileirasso[year]

        # Salvar as alterações no arquivo JSON
        with open(dados, 'w', encoding='utf-8') as f:
            json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)

        return jsonify({"message": f"Year {year} deleted successfully"}), 200
    else:
        return jsonify({"error": "Invalid method"}), 400

        else:
            return jsonify({"error": "Year must be one greater than the last year"}), 400
        
@app.route('/<string:year>/<string:team>', methods=['GET'])
def get_time(year, team):
    if year in brasileirasso and team in brasileirasso[year]:
        team_data = brasileirasso[year][team].toDict()
        return Response(json.dumps(team_data, ensure_ascii=False), content_type='application/json; charset=utf-8')
    else:
        return jsonify({"error": "Ano ou time não encontrado"}), 404
    
@app.route('/<string:year>/<string:team>', methods=['PATCH'])
@require_api_key(['PATCH'])
def update_data(year, team):
    put_json = request.get_json()
    print(put_json)

    # Verificar se 'year' existe em 'brasileirasso', caso contrário, inicializar
    if year not in brasileirasso:
        brasileirasso[year] = {}
    
    # Verificar se 'team' existe em 'brasileirasso[year]', caso contrário, inicializar
    if team not in brasileirasso[year]:
        brasileirasso[year][team] = {}

    # Atualizar os dados com valores recebidos ou manter os atuais
    for key in ['position', 'points', 'games', 'wins', 'draws', 'losses', 'goals_sc', 'goals_ag', 'goals_diff', 'perc_points']:
        if key in put_json:
            brasileirasso[year][team][key] = put_json[key]

    with open(dados, 'w', encoding='utf-8') as f:
        json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)
        return "Sucess", 200
    
@app.route('/<string:year>/<string:team>/<string:var>', methods=['PUT'])
@require_api_key(['PUT'])
def append_data(year, team, var):
    put_json = request.get_json()
    print(put_json)

    # Verificar se 'year' existe em 'brasileirasso', caso contrário, inicializar
    if year not in brasileirasso:
        brasileirasso[year] = {}
    
    # Verificar se 'team' existe em 'brasileirasso[year]', caso contrário, inicializar
    if team not in brasileirasso[year]:
        brasileirasso[year][team] = {}
    
    if var not in brasileirasso[year]:
        brasileirasso[year][team][var] = put_json.get(var, '')
        
    with open(dados, 'w', encoding='utf-8') as f:
        json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)
    return "Sucess", 200

@app.route('/<string:year>/<string:atribute>', methods=['POST'])
@require_api_key(['POST'])
def insert_atribute(year, atribute):
    put_json = request.get_json()
    print(put_json)
    
    if year in brasileirasso:
        for team, data in brasileirasso[year].items():
            data[atribute] = put_json.get(atribute, None)
    else:
        return "Ano não encontrado", 404
    
    with open(dados, 'w', encoding='utf-8') as f:
        json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)
    return "Sucess", 200

@app.route('/<string:year>/<string:team>/<string:atribute>', methods=['DELETE'])
@require_api_key(['DELETE'])
def delete_atribute(year, team, atribute):

    if year in brasileirasso:

        if team in brasileirasso[year]:
            
            if atribute in brasileirasso[year][team]:
                del brasileirasso[year][team][atribute]
            else:
                return f"Atributo '{atribute}' não encontrado para o time '{team}'", 404
        else:
            return f"Time '{team}' não encontrado para o ano '{year}'", 404
    else:
        return f"Ano '{year}' não encontrado", 404
    
    with open(dados, 'w', encoding='utf-8') as f:
        json.dump(brasileirasso.toDict(), f, ensure_ascii=False, indent=4)
    return "Sucess", 200