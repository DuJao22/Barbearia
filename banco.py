import sqlite3
import os
from datetime import datetime, timedelta
import models

DATABASE = 'barbearia.db'

def conectar_banco():
    return sqlite3.connect(DATABASE)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            foto_perfil TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de funcionários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            foto_perfil TEXT,
            eh_dono BOOLEAN DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de serviços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            duracao INTEGER NOT NULL,
            descricao TEXT
        )
    ''')
    
    # Tabela de agendamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            funcionario_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            data_agendamento DATE NOT NULL,
            horario TIME NOT NULL,
            status TEXT DEFAULT 'pendente',
            valor_total REAL,
            valor_garantia REAL,
            valor_restante REAL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios (id),
            FOREIGN KEY (servico_id) REFERENCES servicos (id)
        )
    ''')
    
    # Tabela de programa de fidelidade
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fidelidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            cortes_acumulados INTEGER DEFAULT 0,
            cortes_gratuitos INTEGER DEFAULT 0,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    # Inserir dados iniciais
    cursor.execute("SELECT COUNT(*) FROM administradores")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO administradores (nome, cpf, senha)
            VALUES ('Administrador', '000.000.000-00', 'pbkdf2:sha256:600000$abcdefgh$1234567890abcdef')
        ''')
    
    cursor.execute("SELECT COUNT(*) FROM servicos")
    if cursor.fetchone()[0] == 0:
        servicos_iniciais = [
            ('Corte Masculino', 25.00, 30, 'Corte masculino tradicional'),
            ('Barba', 15.00, 20, 'Aparar e modelar barba'),
            ('Corte + Barba', 35.00, 45, 'Corte masculino + barba'),
            ('Corte Infantil', 20.00, 25, 'Corte para crianças até 12 anos'),
            ('Sobrancelha', 10.00, 15, 'Design de sobrancelha masculina')
        ]
        cursor.executemany('''
            INSERT INTO servicos (nome, preco, duracao, descricao)
            VALUES (?, ?, ?, ?)
        ''', servicos_iniciais)
    
    conn.commit()
    conn.close()

def buscar_usuario_por_cpf(cpf, tipo_usuario):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    if tipo_usuario == 'cliente':
        cursor.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
    elif tipo_usuario == 'funcionario':
        cursor.execute("SELECT * FROM funcionarios WHERE cpf = ?", (cpf,))
    elif tipo_usuario == 'admin':
        cursor.execute("SELECT * FROM administradores WHERE cpf = ?", (cpf,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        colunas = [desc[0] for desc in cursor.description]
        return dict(zip(colunas, row))
    return None

def inserir_cliente(cliente):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, telefone, cpf, senha, foto_perfil)
            VALUES (?, ?, ?, ?, ?)
        ''', (cliente.nome, cliente.telefone, cliente.cpf, cliente.senha, cliente.foto_perfil))
        
        cliente_id = cursor.lastrowid
        
        # Criar registro de fidelidade
        cursor.execute('''
            INSERT INTO fidelidade (cliente_id, cortes_acumulados, cortes_gratuitos)
            VALUES (?, 0, 0)
        ''', (cliente_id,))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def buscar_todos_servicos():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM servicos")
    rows = cursor.fetchall()
    conn.close()
    
    servicos = []
    for row in rows:
        servicos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2],
            'duracao': row[3],
            'descricao': row[4]
        })
    
    return servicos

def buscar_todos_funcionarios():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, foto_perfil FROM funcionarios")
    rows = cursor.fetchall()
    conn.close()
    
    funcionarios = []
    for row in rows:
        funcionarios.append({
            'id': row[0],
            'nome': row[1],
            'foto_perfil': row[2]
        })
    
    return funcionarios

def verificar_horario_disponivel(funcionario_id, data_agendamento, horario):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM agendamentos
        WHERE funcionario_id = ? AND data_agendamento = ? AND horario = ?
        AND status IN ('pendente', 'confirmado')
    ''', (funcionario_id, data_agendamento, horario))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count == 0

def inserir_agendamento(agendamento):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Buscar preço do serviço
        cursor.execute("SELECT preco FROM servicos WHERE id = ?", (agendamento.servico_id,))
        preco = cursor.fetchone()[0]
        
        valor_total = preco
        valor_garantia = preco * 0.35
        valor_restante = preco - valor_garantia
        
        cursor.execute('''
            INSERT INTO agendamentos (cliente_id, funcionario_id, servico_id, data_agendamento, horario, status, valor_total, valor_garantia, valor_restante)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (agendamento.cliente_id, agendamento.funcionario_id, agendamento.servico_id,
              agendamento.data_agendamento, agendamento.horario, agendamento.status,
              valor_total, valor_garantia, valor_restante))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inserir agendamento: {e}")
        return False
    finally:
        conn.close()

def buscar_agendamentos_pendentes():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, c.nome as cliente_nome, f.nome as funcionario_nome, s.nome as servico_nome,
               a.data_agendamento, a.horario, a.valor_total, c.foto_perfil as cliente_foto
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN funcionarios f ON a.funcionario_id = f.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.status = 'pendente'
        ORDER BY a.data_agendamento, a.horario
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    agendamentos = []
    for row in rows:
        agendamentos.append({
            'id': row[0],
            'cliente_nome': row[1],
            'funcionario_nome': row[2],
            'servico_nome': row[3],
            'data_agendamento': row[4],
            'horario': row[5],
            'valor_total': row[6],
            'cliente_foto': row[7]
        })
    
    return agendamentos

def confirmar_agendamento(agendamento_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE agendamentos SET status = 'confirmado'
            WHERE id = ?
        ''', (agendamento_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao confirmar agendamento: {e}")
        return False
    finally:
        conn.close()

def rejeitar_agendamento(agendamento_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE agendamentos SET status = 'rejeitado'
            WHERE id = ?
        ''', (agendamento_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao rejeitar agendamento: {e}")
        return False
    finally:
        conn.close()

def finalizar_agendamento(agendamento_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE agendamentos SET status = 'finalizado'
            WHERE id = ?
        ''', (agendamento_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao finalizar agendamento: {e}")
        return False
    finally:
        conn.close()

def buscar_agendamento_por_id(agendamento_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM agendamentos WHERE id = ?", (agendamento_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'cliente_id': row[1],
            'funcionario_id': row[2],
            'servico_id': row[3],
            'data_agendamento': row[4],
            'horario': row[5],
            'status': row[6],
            'valor_total': row[7]
        }
    return None

def atualizar_fidelidade(cliente_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE fidelidade SET cortes_acumulados = cortes_acumulados + 1
            WHERE cliente_id = ?
        ''', (cliente_id,))
        
        # Verificar se completou 10 cortes
        cursor.execute("SELECT cortes_acumulados FROM fidelidade WHERE cliente_id = ?", (cliente_id,))
        cortes = cursor.fetchone()[0]
        
        if cortes >= 10:
            cursor.execute('''
                UPDATE fidelidade SET cortes_acumulados = 0, cortes_gratuitos = cortes_gratuitos + 1
                WHERE cliente_id = ?
            ''', (cliente_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar fidelidade: {e}")
        return False
    finally:
        conn.close()

def buscar_fidelidade_cliente(cliente_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM fidelidade WHERE cliente_id = ?", (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'cortes_acumulados': row[2],
            'cortes_gratuitos': row[3],
            'progresso': (row[2] / 10) * 100
        }
    return {'cortes_acumulados': 0, 'cortes_gratuitos': 0, 'progresso': 0}

def calcular_faturamento_total():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COALESCE(SUM(valor_total), 0) FROM agendamentos
        WHERE status = 'finalizado'
    ''')
    
    total = cursor.fetchone()[0]
    conn.close()
    
    return total

def calcular_faturamento_por_funcionario():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.nome, COALESCE(SUM(a.valor_total), 0) as faturamento
        FROM funcionarios f
        LEFT JOIN agendamentos a ON f.id = a.funcionario_id AND a.status = 'finalizado'
        GROUP BY f.id, f.nome
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    faturamento = []
    for row in rows:
        faturamento.append({
            'nome': row[0],
            'faturamento': row[1]
        })
    
    return faturamento

def calcular_lucro_barbearia():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COALESCE(SUM(a.valor_total), 0) as lucro
        FROM agendamentos a
        JOIN funcionarios f ON a.funcionario_id = f.id
        WHERE a.status = 'finalizado' AND f.eh_dono = 1
    ''')
    
    lucro = cursor.fetchone()[0]
    conn.close()
    
    return lucro

def buscar_agendamentos_cliente(cliente_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, f.nome as funcionario_nome, s.nome as servico_nome,
               a.data_agendamento, a.horario, a.status, a.valor_total
        FROM agendamentos a
        JOIN funcionarios f ON a.funcionario_id = f.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.cliente_id = ?
        ORDER BY a.data_agendamento DESC, a.horario DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    agendamentos = []
    for row in rows:
        agendamentos.append({
            'id': row[0],
            'funcionario_nome': row[1],
            'servico_nome': row[2],
            'data_agendamento': row[3],
            'horario': row[4],
            'status': row[5],
            'valor_total': row[6]
        })
    
    return agendamentos

def buscar_agendamentos_funcionario(funcionario_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, c.nome as cliente_nome, s.nome as servico_nome,
               a.data_agendamento, a.horario, a.status, a.valor_total
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.funcionario_id = ?
        ORDER BY a.data_agendamento DESC, a.horario DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    agendamentos = []
    for row in rows:
        agendamentos.append({
            'id': row[0],
            'cliente_nome': row[1],
            'servico_nome': row[2],
            'data_agendamento': row[3],
            'horario': row[4],
            'status': row[5],
            'valor_total': row[6]
        })
    
    return agendamentos

def calcular_faturamento_funcionario(funcionario_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COALESCE(SUM(valor_total), 0) FROM agendamentos
        WHERE funcionario_id = ? AND status = 'finalizado'
    ''', (funcionario_id,))
    
    faturamento = cursor.fetchone()[0]
    conn.close()
    
    return faturamento