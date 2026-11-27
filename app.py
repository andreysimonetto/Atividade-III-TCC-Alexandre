from flask import Flask, jsonify, render_template, request
from database import (
    cadastrar_produto,
    cadastrar_usuario,
    criar_pedido,
    excluir_produto,
    fazer_login,
    listar_produtos,
    atualizar_produto,
)

app = Flask(__name__, template_folder='templates')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/produtos')
def api_listar_produtos():
    return jsonify(listar_produtos())


@app.post('/api/produtos')
def api_cadastrar_produto():
    dados = request.get_json() or {}
    campos_obrigatorios = ['nome', 'categoria', 'preco']
    if any(campo not in dados for campo in campos_obrigatorios):
        return jsonify({'erro': 'Preencha nome, categoria e preco.'}), 400
    produto_id = cadastrar_produto(dados)
    return jsonify({'id': produto_id}), 201


@app.put('/api/produtos/<int:produto_id>')
def api_atualizar_produto(produto_id):
    dados = request.get_json() or {}
    if any(campo not in dados for campo in ['nome', 'categoria', 'preco']):
        return jsonify({'erro': 'Preencha nome, categoria e preco.'}), 400
    if not atualizar_produto(produto_id, dados):
        return jsonify({'erro': 'Produto não encontrado.'}), 404
    return jsonify({'mensagem': 'Produto atualizado com sucesso.'})


@app.delete('/api/produtos/<int:produto_id>')
def api_excluir_produto(produto_id):
    if not excluir_produto(produto_id):
        return jsonify({'erro': 'Produto não encontrado.'}), 404
    return jsonify({'mensagem': 'Produto excluído com sucesso.'})


@app.post('/api/cadastro')
def api_cadastro():
    dados = request.get_json() or {}
    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip()
    telefone = dados.get('telefone', '').strip()
    senha = dados.get('senha', '')

    if not nome or not email or not telefone or not senha:
        return jsonify({'erro': 'Preencha todos os campos.'}), 400

    usuario_id = cadastrar_usuario(nome, email, telefone, senha)
    if usuario_id is None:
        return jsonify({'erro': 'Este email já está cadastrado.'}), 409

    return jsonify({'id': usuario_id, 'mensagem': 'Conta criada com sucesso.'}), 201


@app.post('/api/login')
def api_login():
    dados = request.get_json() or {}
    email = dados.get('email', '').strip()
    senha = dados.get('senha', '')

    usuario = fazer_login(email, senha)
    if usuario is None:
        return jsonify({'erro': 'Email ou senha inválidos.'}), 401

    return jsonify(usuario)


@app.post('/api/checkout')
def api_checkout():
    dados = request.get_json() or {}
    usuario_id = dados.get('usuario_id')
    itens = dados.get('itens', [])

    if not usuario_id:
        return jsonify({'erro': 'Faça login para finalizar a compra.'}), 401
    if not itens:
        return jsonify({'erro': 'Seu carrinho está vazio.'}), 400

    try:
        pedido = criar_pedido(int(usuario_id), itens)
        return jsonify(pedido), 201
    except ValueError as erro:
        return jsonify({'erro': str(erro)}), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)