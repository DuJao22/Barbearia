# Sistema de Gestão para Barbearia Profissional

Sistema completo desenvolvido em Python com Flask para gerenciamento de barbearias, incluindo agendamentos, programa de fidelidade, controle de faturamento e muito mais.

## 🚀 Funcionalidades

### 👥 Sistema de Usuários
- **Clientes**: Cadastro com foto de perfil, CPF, telefone
- **Funcionários**: Cadastro de barbeiros com informações completas
- **Administradores**: Painel de controle completo

### 📅 Sistema de Agendamento
- Seleção de serviços e funcionários
- Controle de horários disponíveis
- Bloqueio automático de horários ocupados
- Status de agendamento (pendente, confirmado, finalizado, rejeitado)

### 💰 Sistema de Pagamento
- Cálculo automático de valores
- Garantia de 35% via PIX
- Controle de valores restantes
- Faturamento por funcionário

### 🎁 Programa de Fidelidade
- A cada 10 cortes, ganhe 1 grátis
- Barra de progresso visual
- Controle automático de acúmulo

### 📊 Dashboard Completo
- Faturamento total da barbearia
- Lucro individual por funcionário
- Estatísticas de agendamentos
- Notificações de pendências

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.x + Flask
- **Banco de Dados**: SQLite3
- **Frontend**: HTML5 + Tailwind CSS
- **Templates**: Jinja2
- **Segurança**: Werkzeug (hash de senhas)
- **Uploads**: Fotos de perfil

## 📋 Requisitos

- Python 3.7+
- Flask
- SQLite3
- Werkzeug

## 🚀 Instalação

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install flask werkzeug
   ```

3. Execute o sistema:
   ```bash
   python app.py
   ```

4. Acesse: `http://localhost:5000`

## 👤 Credenciais Padrão

**Administrador:**
- CPF: 000.000.000-00
- Senha: admin123

## 📁 Estrutura do Projeto

```
/barbearia
├── app.py              # Aplicação Flask principal
├── banco.py            # Operações do banco de dados
├── models.py           # Modelos de dados
├── templates/          # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── cadastrar_cliente.html
│   ├── agendamento.html
│   ├── dashboard_admin.html
│   ├── dashboard_cliente.html
│   └── dashboard_funcionario.html
├── static/
│   └── fotos/         # Fotos de perfil
├── barbearia.db       # Banco de dados SQLite
└── README.md
```

## 🎨 Design

- **Tema**: Escuro profissional
- **Cores**: Tailwind CSS com tons de slate e emerald
- **Responsivo**: Mobile-first design
- **Animações**: Transições suaves e hover effects

## 🔒 Segurança

- Senhas hasheadas com Werkzeug
- Sessões Flask para autenticação
- Validação de dados no backend
- Proteção contra duplicação de agendamentos

## 📱 Funcionalidades Principais

### Para Clientes:
- Criar conta com foto
- Fazer agendamentos
- Acompanhar programa de fidelidade
- Visualizar histórico

### Para Funcionários:
- Ver agendamentos do dia
- Finalizar atendimentos
- Acompanhar faturamento individual

### Para Administradores:
- Aprovar/rejeitar agendamentos
- Visualizar faturamento total
- Controlar funcionários
- Estatísticas completas

## 📞 Suporte

Sistema desenvolvido por **João Layon** ©

---

**Nota**: Este sistema foi desenvolvido exclusivamente em Python/Flask, sem uso de JavaScript ou Node.js, seguindo as melhores práticas de desenvolvimento web.