class Cliente:
    def __init__(self, nome, telefone, cpf, senha, foto_perfil=''):
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.senha = senha
        self.foto_perfil = foto_perfil

class Funcionario:
    def __init__(self, nome, telefone, cpf, senha, foto_perfil='', eh_dono=False):
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.senha = senha
        self.foto_perfil = foto_perfil
        self.eh_dono = eh_dono

class Administrador:
    def __init__(self, nome, cpf, senha):
        self.nome = nome
        self.cpf = cpf
        self.senha = senha

class Servico:
    def __init__(self, nome, preco, duracao, descricao=''):
        self.nome = nome
        self.preco = preco
        self.duracao = duracao
        self.descricao = descricao

class Agendamento:
    def __init__(self, cliente_id, funcionario_id, servico_id, data_agendamento, horario, status='pendente'):
        self.cliente_id = cliente_id
        self.funcionario_id = funcionario_id
        self.servico_id = servico_id
        self.data_agendamento = data_agendamento
        self.horario = horario
        self.status = status

class ProgramaFidelidade:
    def __init__(self, cliente_id, cortes_acumulados=0, cortes_gratuitos=0):
        self.cliente_id = cliente_id
        self.cortes_acumulados = cortes_acumulados
        self.cortes_gratuitos = cortes_gratuitos