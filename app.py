from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta
import banco
import models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['UPLOAD_FOLDER'] = 'static/fotos/'

# Criar pasta para uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario')
        
        usuario = banco.buscar_usuario_por_cpf(cpf, tipo_usuario)
        
        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario_id'] = usuario['id']
            session['nome_usuario'] = usuario['nome']
            session['tipo_usuario'] = tipo_usuario
            session['foto_perfil'] = usuario.get('foto_perfil', '')
            
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('CPF ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações
        if not all([nome, telefone, cpf, senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('cadastrar_cliente.html')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('cadastrar_cliente.html')
        
        # Verificar se CPF já existe
        if banco.buscar_usuario_por_cpf(cpf, 'cliente'):
            flash('CPF já cadastrado.', 'danger')
            return render_template('cadastrar_cliente.html')
        
        # Processar foto de perfil
        foto_perfil = ''
        if 'foto_perfil' in request.files:
            arquivo = request.files['foto_perfil']
            if arquivo and arquivo.filename:
                filename = secure_filename(arquivo.filename)
                foto_perfil = f'fotos/{filename}'
                arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Criar cliente
        cliente = models.Cliente(
            nome=nome,
            telefone=telefone,
            cpf=cpf,
            senha=generate_password_hash(senha),
            foto_perfil=foto_perfil
        )
        
        if banco.inserir_cliente(cliente):
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao cadastrar cliente.', 'danger')
    
    return render_template('cadastrar_cliente.html')

@app.route('/dashboard')
@login_requerido
def dashboard():
    tipo_usuario = session.get('tipo_usuario')
    
    if tipo_usuario == 'admin':
        return redirect(url_for('dashboard_admin'))
    elif tipo_usuario == 'funcionario':
        return redirect(url_for('dashboard_funcionario'))
    else:
        return redirect(url_for('dashboard_cliente'))

@app.route('/dashboard_admin')
@admin_requerido
def dashboard_admin():
    # Buscar dados para o dashboard
    agendamentos_pendentes = banco.buscar_agendamentos_pendentes()
    total_faturamento = banco.calcular_faturamento_total()
    faturamento_funcionarios = banco.calcular_faturamento_por_funcionario()
    lucro_barbearia = banco.calcular_lucro_barbearia()
    
    return render_template('dashboard_admin.html',
                         agendamentos_pendentes=agendamentos_pendentes,
                         total_faturamento=total_faturamento,
                         faturamento_funcionarios=faturamento_funcionarios,
                         lucro_barbearia=lucro_barbearia)

@app.route('/dashboard_funcionario')
@login_requerido
def dashboard_funcionario():
    funcionario_id = session.get('usuario_id')
    agendamentos = banco.buscar_agendamentos_funcionario(funcionario_id)
    faturamento = banco.calcular_faturamento_funcionario(funcionario_id)
    
    return render_template('dashboard_funcionario.html',
                         agendamentos=agendamentos,
                         faturamento=faturamento)

@app.route('/dashboard_cliente')
@login_requerido
def dashboard_cliente():
    cliente_id = session.get('usuario_id')
    agendamentos = banco.buscar_agendamentos_cliente(cliente_id)
    fidelidade = banco.buscar_fidelidade_cliente(cliente_id)
    
    return render_template('dashboard_cliente.html',
                         agendamentos=agendamentos,
                         fidelidade=fidelidade)

@app.route('/agendamento', methods=['GET', 'POST'])
@login_requerido
def agendamento():
    if session.get('tipo_usuario') != 'cliente':
        flash('Apenas clientes podem fazer agendamentos.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        funcionario_id = request.form.get('funcionario_id')
        data_agendamento = request.form.get('data_agendamento')
        horario = request.form.get('horario')
        
        # Validações
        if not all([servico_id, funcionario_id, data_agendamento, horario]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('agendamento'))
        
        # Verificar se horário está disponível
        if not banco.verificar_horario_disponivel(funcionario_id, data_agendamento, horario):
            flash('Horário não disponível.', 'danger')
            return redirect(url_for('agendamento'))
        
        # Criar agendamento
        agendamento_obj = models.Agendamento(
            cliente_id=session.get('usuario_id'),
            funcionario_id=funcionario_id,
            servico_id=servico_id,
            data_agendamento=data_agendamento,
            horario=horario,
            status='pendente'
        )
        
        if banco.inserir_agendamento(agendamento_obj):
            flash('Agendamento realizado com sucesso! Aguarde confirmação.', 'success')
            return redirect(url_for('dashboard_cliente'))
        else:
            flash('Erro ao realizar agendamento.', 'danger')
    
    servicos = banco.buscar_todos_servicos()
    funcionarios = banco.buscar_todos_funcionarios()
    
    return render_template('agendamento.html',
                         servicos=servicos,
                         funcionarios=funcionarios)

@app.route('/confirmar_agendamento/<int:agendamento_id>')
@admin_requerido
def confirmar_agendamento(agendamento_id):
    if banco.confirmar_agendamento(agendamento_id):
        flash('Agendamento confirmado com sucesso!', 'success')
    else:
        flash('Erro ao confirmar agendamento.', 'danger')
    
    return redirect(url_for('dashboard_admin'))

@app.route('/rejeitar_agendamento/<int:agendamento_id>')
@admin_requerido
def rejeitar_agendamento(agendamento_id):
    if banco.rejeitar_agendamento(agendamento_id):
        flash('Agendamento rejeitado.', 'info')
    else:
        flash('Erro ao rejeitar agendamento.', 'danger')
    
    return redirect(url_for('dashboard_admin'))

@app.route('/finalizar_agendamento/<int:agendamento_id>')
@login_requerido
def finalizar_agendamento(agendamento_id):
    if banco.finalizar_agendamento(agendamento_id):
        # Atualizar programa de fidelidade
        agendamento = banco.buscar_agendamento_por_id(agendamento_id)
        banco.atualizar_fidelidade(agendamento['cliente_id'])
        flash('Agendamento finalizado com sucesso!', 'success')
    else:
        flash('Erro ao finalizar agendamento.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    banco.inicializar_banco()
    app.run(debug=True)