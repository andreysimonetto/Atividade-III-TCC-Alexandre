import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'beka_esporte.db'


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def criar_tabelas():
    conexao = conectar()
    conexao.executescript('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            preco_antigo REAL,
            descricao TEXT,
            avaliacao INTEGER DEFAULT 0,
            destaque TEXT,
            imagem TEXT,
            quantidade INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            data_pedido TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            subtotal REAL NOT NULL,
            frete REAL NOT NULL,
            desconto REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    ''')
    conexao.commit()
    conexao.close()


def inserir_produtos_iniciais():
    conexao = conectar()
    total = conexao.execute('SELECT COUNT(*) AS total FROM produtos').fetchone()['total']
    if total == 0:
        produtos = [
            ('Tênis Asics Gel-Nimbus', 'Calçados', 949.90, 1199.90, 'O máximo em amortecimento e conforto para sua corrida.', 5, 'Destaque', 'https://placehold.co/600x400?text=Asics+Gel-Nimbus', 20),
            ('Bola Mikasa V200W', 'Vôlei', 599.90, 699.90, 'Bola oficial para alto desempenho em quadra.', 5, 'Destaque', 'https://placehold.co/600x400?text=Mikasa+V200W', 15),
            ('Camiseta Brasil Amarela', 'Roupas', 129.90, 159.90, 'Camiseta esportiva inspirada na seleção brasileira.', 5, 'Novo', 'https://placehold.co/600x400?text=Camiseta+Brasil', 30),
            ('Manguito N1 Sport', 'Acessórios', 59.90, 79.90, 'Proteção e conforto para seus treinos.', 4, 'Novo', 'https://placehold.co/600x400?text=Manguito+N1', 40),
            ('Joelheira N1 Sport', 'Acessórios', 89.90, 109.90, 'Suporte e proteção para atividades esportivas.', 5, 'Destaque', 'https://placehold.co/600x400?text=Joelheira+N1', 25),
            ('Bola de Futebol', 'Futebol', 149.90, 189.90, 'Bola para partidas e treinamentos.', 5, 'Novo', 'https://placehold.co/600x400?text=Bola+Futebol', 35)
        ]
        conexao.executemany('''
            INSERT INTO produtos
            (nome, categoria, preco, preco_antigo, descricao, avaliacao, destaque, imagem, quantidade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', produtos)
        conexao.commit()
    conexao.close()


def listar_produtos():
    conexao = conectar()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id').fetchall()
    conexao.close()
    return [dict(produto) for produto in produtos]


def buscar_produto(produto_id):
    conexao = conectar()
    produto = conexao.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    conexao.close()
    return dict(produto) if produto else None


def cadastrar_produto(dados):
    conexao = conectar()
    cursor = conexao.execute('''
        INSERT INTO produtos
        (nome, categoria, preco, preco_antigo, descricao, avaliacao, destaque, imagem, quantidade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dados['nome'],
        dados['categoria'],
        dados['preco'],
        dados.get('preco_antigo'),
        dados.get('descricao', ''),
        dados.get('avaliacao', 0),
        dados.get('destaque', ''),
        dados.get('imagem', ''),
        dados.get('quantidade', 0)
    ))
    conexao.commit()
    produto_id = cursor.lastrowid
    conexao.close()
    return produto_id


def atualizar_produto(produto_id, dados):
    conexao = conectar()
    conexao.execute('''
        UPDATE produtos
        SET nome = ?, categoria = ?, preco = ?, preco_antigo = ?, descricao = ?,
            avaliacao = ?, destaque = ?, imagem = ?, quantidade = ?
        WHERE id = ?
    ''', (
        dados['nome'],
        dados['categoria'],
        dados['preco'],
        dados.get('preco_antigo'),
        dados.get('descricao', ''),
        dados.get('avaliacao', 0),
        dados.get('destaque', ''),
        dados.get('imagem', ''),
        dados.get('quantidade', 0),
        produto_id
    ))
    conexao.commit()
    alterado = conexao.total_changes > 0
    conexao.close()
    return alterado


def excluir_produto(produto_id):
    conexao = conectar()
    conexao.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
    conexao.commit()
    excluido = conexao.total_changes > 0
    conexao.close()
    return excluido


def cadastrar_usuario(nome, email, telefone, senha):
    conexao = conectar()
    try:
        cursor = conexao.execute('''
            INSERT INTO usuarios (nome, email, telefone, senha)
            VALUES (?, ?, ?, ?)
        ''', (nome, email.lower().strip(), telefone, generate_password_hash(senha)))
        conexao.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conexao.close()


def fazer_login(email, senha):
    conexao = conectar()
    usuario = conexao.execute(
        'SELECT id, nome, email, telefone, senha FROM usuarios WHERE email = ?',
        (email.lower().strip(),)
    ).fetchone()
    conexao.close()
    if usuario and check_password_hash(usuario['senha'], senha):
        return {
            'id': usuario['id'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'telefone': usuario['telefone']
        }
    return None


def criar_pedido(usuario_id, itens):
    conexao = conectar()
    try:
        subtotal = 0
        itens_validos = []

        for item in itens:
            produto = conexao.execute(
                'SELECT id, nome, preco, quantidade FROM produtos WHERE id = ?',
                (item['id'],)
            ).fetchone()
            quantidade = int(item['quantity'])
            if not produto or quantidade < 1 or produto['quantidade'] < quantidade:
                raise ValueError(f'Produto sem estoque suficiente: {item["id"]}')
            subtotal += produto['preco'] * quantidade
            itens_validos.append((produto['id'], quantidade, produto['preco']))

        frete = 0 if subtotal >= 100 else 15
        desconto = subtotal * 0.10 if subtotal >= 500 else 0
        total = subtotal + frete - desconto

        cursor = conexao.execute('''
            INSERT INTO pedidos (usuario_id, subtotal, frete, desconto, total)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, subtotal, frete, desconto, total))
        pedido_id = cursor.lastrowid

        for produto_id, quantidade, preco in itens_validos:
            conexao.execute('''
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco)
                VALUES (?, ?, ?, ?)
            ''', (pedido_id, produto_id, quantidade, preco))
            conexao.execute(
                'UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?',
                (quantidade, produto_id)
            )

        conexao.commit()
        return {
            'id': pedido_id,
            'subtotal': subtotal,
            'frete': frete,
            'desconto': desconto,
            'total': total
        }
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


criar_tabelas()
inserir_produtos_iniciais()