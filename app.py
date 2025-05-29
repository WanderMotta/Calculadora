from flask import Flask, request, render_template_string, flash
from dataclasses import dataclass
from typing import Optional, Tuple

app = Flask(__name__)
app.secret_key = 'calculadora_precificacao_2024'  # Para usar flash messages

@dataclass
class DadosEntrada:
    """Classe para organizar os dados de entrada da calculadora"""
    F_base: float  # Valor base
    N_emp: int     # Número de funcionários
    Rp1: float     # Tarifa até 100 funcionários
    Rp2: float     # Tarifa acima de 100 funcionários
    N_loc: int     # Número de postos
    R_loc: float   # Tarifa por posto
    Aud_incl: int  # Audiências incluídas
    N_aud: int     # Número total de audiências
    R_aud: float   # Tarifa por audiência extra
    m: float       # Margem de lucro

@dataclass
class ResultadoCalculo:
    """Classe para organizar os resultados dos cálculos"""
    C_emp: float        # Custo por funcionários
    C_loc: float        # Custo por postos
    C_aud: float        # Custo por audiências extras
    Custo_bruto: float  # Custo bruto total
    Preco: float        # Preço final com margem

def validar_dados_entrada(form_data) -> Tuple[bool, str]:
    """Valida os dados de entrada e retorna (é_válido, mensagem_erro)"""
    try:
        # Validações básicas de tipo e valor
        F_base = float(form_data.get('F_base', 0))
        N_emp = int(form_data.get('N_emp', 0))
        Rp1 = float(form_data.get('Rp1', 0))
        Rp2 = float(form_data.get('Rp2', 0))
        N_loc = int(form_data.get('N_loc', 0))
        R_loc = float(form_data.get('R_loc', 0))
        Aud_incl = int(form_data.get('Aud_incl', 0))
        N_aud = int(form_data.get('N_aud', 0))
        R_aud = float(form_data.get('R_aud', 0))
        m = float(form_data.get('m', 0))
        
        # Validações de negócio
        if F_base < 0:
            return False, "O valor base deve ser positivo"
        
        if N_emp < 0:
            return False, "O número de funcionários deve ser positivo"
        
        if Rp1 < 0 or Rp2 < 0:
            return False, "As tarifas de funcionários devem ser positivas"
        
        if N_loc < 0:
            return False, "O número de postos deve ser positivo"
        
        if R_loc < 0:
            return False, "A tarifa por posto deve ser positiva"
        
        if Aud_incl < 0 or N_aud < 0:
            return False, "O número de audiências deve ser positivo"
        
        if N_aud < Aud_incl:
            return False, "O número total de audiências deve ser maior ou igual às audiências incluídas"
        
        if R_aud < 0:
            return False, "A tarifa por audiência extra deve ser positiva"
        
        if m < 0:
            return False, "A margem de lucro deve ser positiva (ex: 0.20 para 20%)"
        
        if m > 10:
            return False, "A margem de lucro parece muito alta. Use valores decimais (ex: 0.20 para 20%)"
        
        return True, ""
        
    except ValueError as e:
        return False, "Erro nos dados informados. Verifique se todos os campos estão preenchidos corretamente"
    except Exception as e:
        return False, f"Erro inesperado na validação: {str(e)}"

def processar_dados_formulario(form_data) -> Optional[DadosEntrada]:
    """Processa os dados do formulário e retorna uma instância de DadosEntrada ou None se inválido"""
    try:
        return DadosEntrada(
            F_base=float(form_data['F_base']),
            N_emp=int(form_data['N_emp']),
            Rp1=float(form_data['Rp1']),
            Rp2=float(form_data['Rp2']),
            N_loc=int(form_data['N_loc']),
            R_loc=float(form_data['R_loc']),
            Aud_incl=int(form_data['Aud_incl']),
            N_aud=int(form_data['N_aud']),
            R_aud=float(form_data['R_aud']),
            m=float(form_data['m'])
        )
    except (ValueError, KeyError) as e:
        return None

def calcular_custo_funcionarios(n_emp: int, rp1: float, rp2: float) -> float:
    """Calcula o custo baseado no número de funcionários com tarifas escalonadas"""
    return min(n_emp, 100) * rp1 + max(0, n_emp - 100) * rp2

def calcular_custo_postos(n_loc: int, r_loc: float) -> float:
    """Calcula o custo baseado no número de postos"""
    return n_loc * r_loc

def calcular_custo_audiencias_extras(n_aud: int, aud_incl: int, r_aud: float) -> float:
    """Calcula o custo das audiências extras (acima das incluídas)"""
    return max(0, n_aud - aud_incl) * r_aud

def calcular_precificacao(dados: DadosEntrada) -> ResultadoCalculo:
    """Função principal que executa todos os cálculos de precificação"""
    # Cálculos individuais
    C_emp = calcular_custo_funcionarios(dados.N_emp, dados.Rp1, dados.Rp2)
    C_loc = calcular_custo_postos(dados.N_loc, dados.R_loc)
    C_aud = calcular_custo_audiencias_extras(dados.N_aud, dados.Aud_incl, dados.R_aud)
    
    # Cálculos finais
    Custo_bruto = dados.F_base + C_emp + C_loc + C_aud
    Preco = Custo_bruto * (1 + dados.m)
    
    return ResultadoCalculo(
        C_emp=C_emp,
        C_loc=C_loc,
        C_aud=C_aud,
        Custo_bruto=Custo_bruto,
        Preco=Preco
    )

HTML = '''
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Precificação</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      
      body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem;
      }
      
      .container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        overflow: hidden;
      }
      
      .header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        text-align: center;
      }
      
      .header h1 {
        font-size: 2.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
      }
      
      .header p {
        opacity: 0.9;
        font-size: 1.1rem;
      }
      
      .form-container {
        padding: 2rem;
      }
      
      .messages {
        margin-bottom: 2rem;
      }
      
      .message {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
      
      .message.success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border-left: 4px solid #28a745;
      }
      
      .message.error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border-left: 4px solid #dc3545;
      }
      
      .message::before {
        content: "✓";
        font-weight: bold;
        font-size: 1.2rem;
      }
      
      .message.error::before {
        content: "⚠";
      }
      
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
      }
      
      .form-group {
        position: relative;
      }
      
      .form-group label {
        display: block;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
      }
      
      .form-group input {
        width: 100%;
        padding: 1rem;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f8f9fa;
      }
      
      .form-group input:focus {
        outline: none;
        border-color: #4facfe;
        background: white;
        box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
      }
      
      .btn-calcular {
        width: 100%;
        padding: 1.2rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
      
      .btn-calcular:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
      }
      
      .resultado {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        border-left: 5px solid #4facfe;
      }
      
      .resultado h2 {
        color: #333;
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        text-align: center;
      }
      
      .resultado-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
      }
      
      .resultado-item {
        background: rgba(255, 255, 255, 0.7);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
      }
      
      .resultado-item .label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
      }
      
      .resultado-item .valor {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
      }
      
      .resultado-final {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 1rem;
      }
      
      .resultado-final .label {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
      }
      
      .resultado-final .valor {
        font-size: 2rem;
        font-weight: 700;
      }
      
      @media (max-width: 768px) {
        body {
          padding: 1rem;
        }
        
        .header h1 {
          font-size: 2rem;
        }
        
        .form-grid {
          grid-template-columns: 1fr;
        }
        
        .resultado-grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Calculadora de Precificação</h1>
        <p>Sistema profissional para cálculo de custos e precificação</p>
      </div>
      
      <div class="form-container">
        <form method="post">
          <div class="messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="message {{ category }}">
                    {{ message }}
                  </div>
                {% endfor %}
              {% endif %}
            {% endwith %}
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label>Valor Base (F_base)</label>
              <input type="number" step="0.01" name="F_base" required placeholder="Ex: 1000.00">
            </div>
            
            <div class="form-group">
              <label>Nº Funcionários (N_emp)</label>
              <input type="number" name="N_emp" required placeholder="Ex: 50">
            </div>
            
            <div class="form-group">
              <label>Tarifa até 100 (Rp1)</label>
              <input type="number" step="0.01" name="Rp1" required placeholder="Ex: 25.00">
            </div>
            
            <div class="form-group">
              <label>Tarifa acima de 100 (Rp2)</label>
              <input type="number" step="0.01" name="Rp2" required placeholder="Ex: 30.00">
            </div>
            
            <div class="form-group">
              <label>Nº Postos (N_loc)</label>
              <input type="number" name="N_loc" required placeholder="Ex: 5">
            </div>
            
            <div class="form-group">
              <label>Tarifa por posto (R_loc)</label>
              <input type="number" step="0.01" name="R_loc" required placeholder="Ex: 200.00">
            </div>
            
            <div class="form-group">
              <label>Audiências incluídas (Aud_incl)</label>
              <input type="number" name="Aud_incl" required placeholder="Ex: 3">
            </div>
            
            <div class="form-group">
              <label>Nº Audiências (N_aud)</label>
              <input type="number" name="N_aud" required placeholder="Ex: 8">
            </div>
            
            <div class="form-group">
              <label>Tarifa por audiência extra (R_aud)</label>
              <input type="number" step="0.01" name="R_aud" required placeholder="Ex: 150.00">
            </div>
            
            <div class="form-group">
              <label>Margem de lucro (m)</label>
              <input type="number" step="0.01" name="m" required placeholder="Ex: 0.20 (20%)">
            </div>
          </div>
          
          <button type="submit" class="btn-calcular">Calcular Precificação</button>
        </form>
        
        {% if resultado %}
        <div class="resultado">
          <h2>Resultado da Precificação</h2>
          
          <div class="resultado-grid">
            <div class="resultado-item">
              <div class="label">Custo por funcionários</div>
              <div class="valor">R$ {{ "%.2f"|format(resultado.C_emp) }}</div>
            </div>
            
            <div class="resultado-item">
              <div class="label">Custo por postos</div>
              <div class="valor">R$ {{ "%.2f"|format(resultado.C_loc) }}</div>
            </div>
            
            <div class="resultado-item">
              <div class="label">Custo por audiências extras</div>
              <div class="valor">R$ {{ "%.2f"|format(resultado.C_aud) }}</div>
            </div>
            
            <div class="resultado-item">
              <div class="label">Custo Bruto</div>
              <div class="valor">R$ {{ "%.2f"|format(resultado.Custo_bruto) }}</div>
            </div>
          </div>
          
          <div class="resultado-final">
            <div class="label">Preço Final</div>
            <div class="valor">R$ {{ "%.2f"|format(resultado.Preco) }}</div>
          </div>
        </div>
        {% endif %}
      </div>
    </div>
  </body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        # Validar dados antes de processar
        valido, mensagem_erro = validar_dados_entrada(request.form)
        
        if not valido:
            flash(mensagem_erro, 'error')
        else:
            try:
                dados = processar_dados_formulario(request.form)
                if dados:
                    resultado = calcular_precificacao(dados)
                    flash('Cálculo realizado com sucesso!', 'success')
                else:
                    flash('Erro ao processar os dados. Verifique os valores informados.', 'error')
            except Exception as e:
                flash(f'Erro inesperado no cálculo: {str(e)}', 'error')
    
    return render_template_string(HTML, resultado=resultado)

if __name__ == '__main__':
    # Rodar sem debug para evitar erro de _multiprocessing
    app.run(debug=False)
