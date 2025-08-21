from flask import Flask, render_template_string, request, redirect, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# ========================
# CREAR BASE DE DATOS
# ========================
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()

    # Eliminar tablas existentes para recrearlas correctamente
    cursor.executescript("""
    DROP TABLE IF EXISTS Costos;
    DROP TABLE IF EXISTS Logistica;
    DROP TABLE IF EXISTS Equipos;
    DROP TABLE IF EXISTS TallasRopa;
    
    CREATE TABLE IF NOT EXISTS Brigadas (
        ID_Brigada INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre_Brigada TEXT NOT NULL,
        Cant_Bomberos INTEGER,
        Cel_Comandante TEXT,
        Encargado_Logistica TEXT,
        Cel_Logistica TEXT,
        Nro_Emergencia TEXT
    );

    CREATE TABLE IF NOT EXISTS TallasRopa (
        ID_Talla INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Tipo_Ropa TEXT NOT NULL,
        Talla_XS INTEGER DEFAULT 0,
        Talla_S INTEGER DEFAULT 0,
        Talla_M INTEGER DEFAULT 0,
        Talla_L INTEGER DEFAULT 0,
        Talla_XL INTEGER DEFAULT 0,
        Observaciones TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );

    CREATE TABLE IF NOT EXISTS Equipos (
        ID_Equipo INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Categoria_Equipo TEXT NOT NULL,
        Nombre_Articulo TEXT NOT NULL,
        Cantidad INTEGER DEFAULT 0,
        Observacion TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );

    CREATE TABLE IF NOT EXISTS Logistica (
        ID_Logistica INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Nombre TEXT NOT NULL,
        Costo_Unitario REAL DEFAULT 0,
        Observaciones TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ========================
# PÁGINA PRINCIPAL - LISTADO DE BRIGADAS
# ========================
@app.route("/")
def index():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Brigadas ORDER BY ID_Brigada DESC")
    brigadas = cursor.fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Brigadas Profesional</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c2 100%);
                min-height: 100vh;
                color: #5d4e37;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                padding: 40px 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #d2691e 0%, #a0522d 100%);
                color: white;
                text-align: center;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(210, 105, 30, 0.3);
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .header h1 { 
                font-size: 2.5rem;
                font-weight: 300;
                letter-spacing: 2px;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }
            
            .header .subtitle {
                font-size: 1.1rem;
                opacity: 0.9;
                font-weight: 300;
                position: relative;
                z-index: 1;
            }
            
            .card {
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(139, 69, 19, 0.15);
                margin-bottom: 30px;
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 50px rgba(139, 69, 19, 0.25);
            }
            
            .card-header {
                background: linear-gradient(135deg, #cd853f 0%, #daa520 100%);
                color: white;
                padding: 20px 30px;
                border-bottom: 3px solid #b8860b;
            }
            
            .card-header h2 {
                font-size: 1.5rem;
                font-weight: 400;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .card-body {
                padding: 30px;
            }
            
            .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 25px;
            }
            
            .form-group {
                display: flex;
                flex-direction: column;
            }
            
            .form-group label {
                font-weight: 600;
                color: #8b4513;
                margin-bottom: 8px;
                font-size: 0.95rem;
                letter-spacing: 0.5px;
            }
            
            input[type="text"], 
            input[type="number"], 
            select {
                padding: 12px 16px;
                border: 2px solid #e6d7c5;
                border-radius: 8px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: #fefefe;
            }
            
            input[type="text"]:focus, 
            input[type="number"]:focus, 
            select:focus {
                outline: none;
                border-color: #cd853f;
                box-shadow: 0 0 0 4px rgba(205, 133, 63, 0.1);
                transform: translateY(-2px);
            }
            
            .btn {
                padding: 14px 28px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
                letter-spacing: 0.5px;
                position: relative;
                overflow: hidden;
            }
            
            .btn::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }
            
            .btn:hover::before {
                width: 300px;
                height: 300px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #d2691e 0%, #ff7f50 100%);
                color: white;
                box-shadow: 0 6px 20px rgba(210, 105, 30, 0.3);
            }
            
            .btn-primary:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(210, 105, 30, 0.4);
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #cd853f 0%, #daa520 100%);
                color: white;
                box-shadow: 0 6px 20px rgba(205, 133, 63, 0.3);
            }
            
            .btn-secondary:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(205, 133, 63, 0.4);
            }
            
            .btn-action {
                background: linear-gradient(135deg, #ff8c00 0%, #ffa500 100%);
                color: white;
                padding: 8px 16px;
                font-size: 0.9rem;
                border-radius: 6px;
            }
            
            .btn-action:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 140, 0, 0.4);
            }
            
            table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(139, 69, 19, 0.1);
            }
            
            th {
                background: linear-gradient(135deg, #8b4513 0%, #a0522d 100%);
                color: white;
                padding: 18px 15px;
                text-align: left;
                font-weight: 600;
                font-size: 0.95rem;
                letter-spacing: 0.5px;
            }
            
            td {
                padding: 16px 15px;
                border-bottom: 1px solid #f0e6d6;
                background: white;
                transition: background-color 0.3s ease;
            }
            
            tr:hover td {
                background: #faf5f0;
            }
            
            tr:last-child td {
                border-bottom: none;
            }
            
            .success-message {
                background: linear-gradient(135deg, #228b22 0%, #32cd32 100%);
                color: white;
                padding: 16px 24px;
                border-radius: 10px;
                margin: 20px 0;
                box-shadow: 0 4px 15px rgba(34, 139, 34, 0.3);
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 500;
            }
            
            .nav-section {
                text-align: center;
                margin: 40px 0;
            }
            
            .nav-section .btn {
                margin: 0 10px;
                min-width: 200px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 6px 25px rgba(139, 69, 19, 0.1);
                border-left: 4px solid #d2691e;
            }
            
            .stat-number {
                font-size: 2.5rem;
                font-weight: bold;
                color: #d2691e;
                margin-bottom: 8px;
            }
            
            .stat-label {
                color: #8b4513;
                font-weight: 500;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 1px;
            }
            
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #8b4513;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(139, 69, 19, 0.1);
            }
            
            .empty-state .icon {
                font-size: 4rem;
                margin-bottom: 20px;
                opacity: 0.5;
            }
            
            .form-submit {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e6d7c5;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 20px 15px;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .form-grid {
                    grid-template-columns: 1fr;
                }
                
                table {
                    font-size: 0.9rem;
                }
                
                th, td {
                    padding: 12px 8px;
                }
                
                .btn {
                    padding: 12px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚒 Sistema de Gestión de Brigadas</h1>
                <div class="subtitle">Gestión Profesional de Equipos de Emergencia</div>
            </div>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="success-message">
                            <span style="font-size: 1.2rem;">✅</span>
                            <span>{{ message }}</span>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="card">
                <div class="card-header">
                    <h2>
                        <span style="font-size: 1.3rem;">➕</span>
                        Registrar Nueva Brigada
                    </h2>
                </div>
                <div class="card-body">
                    <form method="POST" action="/crear_brigada">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Nombre de la Brigada</label>
                                <input type="text" name="nombre_brigada" required placeholder="Ingrese el nombre de la brigada">
                            </div>
                            <div class="form-group">
                                <label>Cantidad de Bomberos</label>
                                <input type="number" name="cant_bomberos" placeholder="Número de efectivos">
                            </div>
                            <div class="form-group">
                                <label>Celular del Comandante</label>
                                <input type="text" name="cel_comandante" placeholder="Número de contacto">
                            </div>
                            <div class="form-group">
                                <label>Encargado de Logística</label>
                                <input type="text" name="encargado_logistica" placeholder="Nombre completo">
                            </div>
                            <div class="form-group">
                                <label>Celular de Logística</label>
                                <input type="text" name="cel_logistica" placeholder="Número de contacto">
                            </div>
                            <div class="form-group">
                                <label>Número de Emergencia</label>
                                <input type="text" name="nro_emergencia" placeholder="Línea de emergencia">
                            </div>
                        </div>
                        <div class="form-submit">
                            <button type="submit" class="btn btn-primary">
                                <span style="position: relative; z-index: 1;">🆕 Crear Nueva Brigada</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div class="nav-section">
                <a href="/ver_todas" class="btn btn-secondary">
                    <span style="position: relative; z-index: 1;">📋 Ver Todas las Brigadas con Artículos</span>
                </a>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2>
                        <span style="font-size: 1.3rem;">📋</span>
                        Registro de Brigadas Activas
                    </h2>
                </div>
                <div class="card-body">
                    {% if brigadas %}
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nombre de Brigada</th>
                                    <th>N° Bomberos</th>
                                    <th>Cel. Comandante</th>
                                    <th>Encargado Logística</th>
                                    <th>Cel. Logística</th>
                                    <th>N° Emergencia</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for brigada in brigadas %}
                                <tr>
                                    <td><strong style="color: #d2691e;">#{{ brigada[0] }}</strong></td>
                                    <td><strong>{{ brigada[1] }}</strong></td>
                                    <td>{{ brigada[2] or 'N/A' }}</td>
                                    <td>{{ brigada[3] or 'N/A' }}</td>
                                    <td>{{ brigada[4] or 'N/A' }}</td>
                                    <td>{{ brigada[5] or 'N/A' }}</td>
                                    <td>{{ brigada[6] or 'N/A' }}</td>
                                    <td>
                                        <a href="/brigada/{{ brigada[0] }}" class="btn btn-action">
                                            <span style="position: relative; z-index: 1;">⚙️ Gestionar</span>
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">🚒</div>
                            <h3>No hay brigadas registradas</h3>
                            <p>Comience creando su primera brigada utilizando el formulario superior.</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </body>
    </html>
    """, brigadas=brigadas)

# ========================
# CREAR BRIGADA
# ========================
@app.route("/crear_brigada", methods=["POST"])
def crear_brigada():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Brigadas (Nombre_Brigada, Cant_Bomberos, Cel_Comandante, Encargado_Logistica, Cel_Logistica, Nro_Emergencia)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form['nombre_brigada'],
        request.form['cant_bomberos'],
        request.form['cel_comandante'],
        request.form['encargado_logistica'],
        request.form['cel_logistica'],
        request.form['nro_emergencia']
    ))
    conn.commit()
    conn.close()
    flash('Brigada creada exitosamente!')
    return redirect("/")

# ========================
# GESTIÓN DE BRIGADA INDIVIDUAL
# ========================
@app.route("/brigada/<int:brigada_id>")
def gestionar_brigada(brigada_id):
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    
    # Obtener datos de la brigada
    cursor.execute("SELECT * FROM Brigadas WHERE ID_Brigada = ?", (brigada_id,))
    brigada = cursor.fetchone()
    
    # Obtener tallas
    cursor.execute("SELECT * FROM TallasRopa WHERE ID_Brigada = ?", (brigada_id,))
    tallas = cursor.fetchall()
    
    # Obtener equipos
    cursor.execute("SELECT * FROM Equipos WHERE ID_Brigada = ?", (brigada_id,))
    equipos = cursor.fetchall()
    
    # Obtener logística
    cursor.execute("SELECT * FROM Logistica WHERE ID_Brigada = ?", (brigada_id,))
    logistica = cursor.fetchall()
    
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestionar Brigada - {{ brigada[1] }}</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c2 100%);
                min-height: 100vh;
                color: #5d4e37;
                line-height: 1.5;
            }
            
            .container { 
                max-width: 1500px; 
                margin: 0 auto; 
                padding: 20px;
            }
            
            .header-section {
                background: linear-gradient(135deg, #d2691e 0%, #a0522d 100%);
                color: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(210, 105, 30, 0.3);
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }
            
            .header-section::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .back-btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 500;
                transition: all 0.3s ease;
                margin-bottom: 15px;
                backdrop-filter: blur(10px);
                position: relative;
                z-index: 1;
            }
            
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateX(-5px);
            }
            
            .brigade-title {
                font-size: 2rem;
                font-weight: 300;
                letter-spacing: 1px;
                position: relative;
                z-index: 1;
            }
            
            .section-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(139, 69, 19, 0.12);
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(139, 69, 19, 0.18);
            }
            
            .card-header {
                background: linear-gradient(135deg, #cd853f 0%, #daa520 100%);
                color: white;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.2rem;
                font-weight: 500;
            }
            
            .card-body {
                padding: 25px;
            }
            
            .form-section {
                background: #fefcf7;
                border: 2px solid #f4e8d0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 25px;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 15px;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .form-row:last-child {
                margin-bottom: 0;
            }
            
            .form-label {
                font-weight: 600;
                color: #8b4513;
                min-width: 140px;
                font-size: 0.95rem;
            }
            
            .size-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 15px;
            }
            
            .size-item {
                display: flex;
                align-items: center;
                gap: 8px;
                background: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #e6d7c5;
            }
            
            .size-label {
                font-weight: bold;
                color: #d2691e;
                min-width: 25px;
            }
            
            input[type="text"], 
            input[type="number"], 
            select {
                padding: 12px;
                border: 2px solid #e6d7c5;
                border-radius: 8px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: white;
            }
            
            .size-item input {
                padding: 8px;
                font-size: 0.9rem;
            }
            
            input[type="text"]:focus, 
            input[type="number"]:focus, 
            select:focus {
                outline: none;
                border-color: #cd853f;
                box-shadow: 0 0 0 4px rgba(205, 133, 63, 0.1);
            }
            
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .btn::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }
            
            .btn:hover::before {
                width: 300px;
                height: 300px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #d2691e 0%, #ff7f50 100%);
                color: white;
                box-shadow: 0 6px 20px rgba(210, 105, 30, 0.3);
                width: 100%;
                justify-content: center;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(210, 105, 30, 0.4);
            }
            
            .btn span {
                position: relative;
                z-index: 1;
            }
            
            .data-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(139, 69, 19, 0.1);
                margin-top: 15px;
            }
            
            .data-table th {
                background: linear-gradient(135deg, #8b4513 0%, #a0522d 100%);
                color: white;
                padding: 12px 10px;
                text-align: left;
                font-weight: 600;
                font-size: 0.9rem;
                letter-spacing: 0.5px;
            }
            
            .data-table td {
                padding: 12px 10px;
                border-bottom: 1px solid #f0e6d6;
                background: white;
                font-size: 0.9rem;
            }
            
            .data-table tr:hover td {
                background: #faf5f0;
            }
            
            .data-table tr:last-child td {
                border-bottom: none;
            }
            
            .tag {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                text-align: center;
            }
            
            .tag-category {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                color: #1565c0;
                border: 1px solid #90caf9;
            }
            
            .tag-quantity {
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                color: #2e7d32;
                border: 1px solid #81c784;
            }
            
            .tag-cost {
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                color: #ef6c00;
                border: 1px solid #ffb74d;
            }
            
            .section-title {
                color: #8b4513;
                font-size: 1.1rem;
                font-weight: 600;
                margin: 20px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #e6d7c5;
            }
            
            .full-width-card {
                grid-column: 1 / -1;
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #8b4513;
                opacity: 0.7;
            }
            
            .empty-state .icon {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            select option {
                padding: 8px;
            }
            
            @media (max-width: 768px) {
                .section-grid {
                    grid-template-columns: 1fr;
                }
                
                .size-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .form-row {
                    grid-template-columns: 1fr;
                }
                
                .form-label {
                    min-width: auto;
                }
                
                .data-table {
                    font-size: 0.8rem;
                }
                
                .data-table th,
                .data-table td {
                    padding: 8px 6px;
                }
            }
            
            @media (max-width: 480px) {
                .size-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        <script>
            function agregarTalla() {
                var form = document.getElementById('form-talla');
                var formData = new FormData(form);
                
                fetch('/agregar_talla', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar talla');
                    }
                });
            }
            
            function agregarEquipo() {
                var form = document.getElementById('form-equipo');
                var formData = new FormData(form);
                
                fetch('/agregar_equipo', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar equipo');
                    }
                });
            }
            
            function agregarLogistica() {
                var form = document.getElementById('form-logistica');
                var formData = new FormData(form);
                
                fetch('/agregar_logistica', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar logística');
                    }
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <a href="/" class="back-btn">
                    <span>🔙</span>
                    <span>Volver a Brigadas</span>
                </a>
                <h1 class="brigade-title">⚙️ Gestionar: {{ brigada[1] }}</h1>
            </div>
            
            <div class="section-grid">
                <!-- SECCIÓN TALLAS -->
                <div class="card">
                    <div class="card-header">
                        <span>👕</span>
                        <span>Gestión de Tallas de Ropa</span>
                    </div>
                    <div class="card-body">
                        <div class="form-section">
                            <form id="form-talla" onsubmit="event.preventDefault(); agregarTalla();">
                                <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                                
                                <div class="form-row">
                                    <div class="form-label">Tipo de Ropa:</div>
                                    <input type="text" name="tipo_ropa" required placeholder="Ej: Camiseta, Pantalón, Chaqueta">
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Tallas:</div>
                                    <div class="size-grid">
                                        <div class="size-item">
                                            <div class="size-label">XS:</div>
                                            <input type="number" name="talla_xs" value="0" min="0">
                                        </div>
                                        <div class="size-item">
                                            <div class="size-label">S:</div>
                                            <input type="number" name="talla_s" value="0" min="0">
                                        </div>
                                        <div class="size-item">
                                            <div class="size-label">M:</div>
                                            <input type="number" name="talla_m" value="0" min="0">
                                        </div>
                                        <div class="size-item">
                                            <div class="size-label">L:</div>
                                            <input type="number" name="talla_l" value="0" min="0">
                                        </div>
                                        <div class="size-item">
                                            <div class="size-label">XL:</div>
                                            <input type="number" name="talla_xl" value="0" min="0">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Observaciones:</div>
                                    <input type="text" name="observaciones" placeholder="Detalles adicionales (opcional)">
                                </div>
                                
                                <button type="submit" class="btn btn-primary">
                                    <span>➕ Agregar Tallas</span>
                                </button>
                            </form>
                        </div>

                        <div class="section-title">📋 Tallas Registradas</div>
                        {% if tallas %}
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>ID</th><th>Tipo de Ropa</th><th>XS</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>Observaciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for talla in tallas %}
                                    <tr>
                                        <td><strong>{{ talla[0] }}</strong></td>
                                        <td><strong>{{ talla[2] }}</strong></td>
                                        <td>{{ talla[3] }}</td>
                                        <td>{{ talla[4] }}</td>
                                        <td>{{ talla[5] }}</td>
                                        <td>{{ talla[6] }}</td>
                                        <td>{{ talla[7] }}</td>
                                        <td>{{ talla[8] or 'N/A' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        {% else %}
                            <div class="empty-state">
                                <div class="icon">👕</div>
                                <p>No hay tallas registradas</p>
                            </div>
                        {% endif %}
                    </div>
                </div>

                <!-- SECCIÓN EQUIPOS -->
                <div class="card">
                    <div class="card-header">
                        <span>🛠️</span>
                        <span>Gestión de Equipos y Artículos</span>
                    </div>
                    <div class="card-body">
                        <div class="form-section">
                            <form id="form-equipo" onsubmit="event.preventDefault(); agregarEquipo();">
                                <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                                
                                <div class="form-row">
                                    <div class="form-label">Categoría:</div>
                                    <select name="categoria_equipo" required>
                                        <option value="">-- Seleccione Categoría --</option>
                                        <option value="EQUIPAMIENTO EPP">EQUIPAMIENTO EPP</option>
                                        <option value="HERRAMIENTAS">HERRAMIENTAS</option>
                                        <option value="ALIMENTACION Y BEBIDAS">ALIMENTACIÓN Y BEBIDAS</option>
                                        <option value="LOGISTICA Y EQUIPO DE CAMPO">LOGÍSTICA Y EQUIPO DE CAMPO</option>
                                        <option value="LIMPIEZA PERSONAL">LIMPIEZA PERSONAL</option>
                                        <option value="LIMPIEZA GENERAL">LIMPIEZA GENERAL</option>
                                        <option value="MEDICAMENTOS">MEDICAMENTOS</option>
                                        <option value="RESCATE ANIMAL">RESCATE ANIMAL</option>
                                    </select>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Nombre del Artículo:</div>
                                    <input type="text" name="nombre_articulo" required placeholder="Ej: Casco, Guantes, Botiquín">
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Cantidad:</div>
                                    <input type="number" name="cantidad" value="1" min="0">
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Observaciones:</div>
                                    <input type="text" name="observacion" placeholder="Detalles adicionales (opcional)">
                                </div>
                                
                                <button type="submit" class="btn btn-primary">
                                    <span>➕ Agregar Equipo</span>
                                </button>
                            </form>
                        </div>

                        <div class="section-title">📋 Equipos Registrados</div>
                        {% if equipos %}
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>ID</th><th>Categoría</th><th>Artículo</th><th>Cantidad</th><th>Observación</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for equipo in equipos %}
                                    <tr>
                                        <td><strong>{{ equipo[0] }}</strong></td>
                                        <td><span class="tag tag-category">{{ equipo[2] }}</span></td>
                                        <td><strong>{{ equipo[3] }}</strong></td>
                                        <td><span class="tag tag-quantity">{{ equipo[4] }}</span></td>
                                        <td>{{ equipo[5] or 'N/A' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        {% else %}
                            <div class="empty-state">
                                <div class="icon">🛠️</div>
                                <p>No hay equipos registrados</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- SECCIÓN LOGÍSTICA -->
            <div class="card full-width-card">
                <div class="card-header">
                    <span>📦</span>
                    <span>Gestión de Logística</span>
                </div>
                <div class="card-body">
                    <div class="form-section">
                        <form id="form-logistica" onsubmit="event.preventDefault(); agregarLogistica();">
                            <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                            
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                                <div class="form-row">
                                    <div class="form-label">Nombre del Item:</div>
                                    <input type="text" name="nombre" required placeholder="Nombre del item logístico">
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Costo Unitario ($):</div>
                                    <input type="number" step="0.01" name="costo_unitario" value="0" min="0" placeholder="0.00">
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-label">Observaciones:</div>
                                    <input type="text" name="observaciones" placeholder="Detalles adicionales (opcional)">
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary" style="margin-top: 20px;">
                                <span>➕ Agregar Logística</span>
                            </button>
                        </form>
                    </div>

                    <div class="section-title">📋 Logística Registrada</div>
                    {% if logistica %}
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th><th>Nombre del Item</th><th>Costo Unitario</th><th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in logistica %}
                                <tr>
                                    <td><strong>{{ item[0] }}</strong></td>
                                    <td><strong>{{ item[2] }}</strong></td>
                                    <td><span class="tag tag-cost">${{ "%.2f"|format(item[3] or 0) }}</span></td>
                                    <td>{{ item[4] or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">📦</div>
                            <p>No hay items de logística registrados</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </body>
    </html>
    """, brigada=brigada, tallas=tallas, equipos=equipos, logistica=logistica)

# ========================
# AGREGAR TALLA (AJAX)
# ========================
@app.route("/agregar_talla", methods=["POST"])
def agregar_talla():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TallasRopa (ID_Brigada, Tipo_Ropa, Talla_XS, Talla_S, Talla_M, Talla_L, Talla_XL, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['tipo_ropa'],
            request.form['talla_xs'] or 0,
            request.form['talla_s'] or 0,
            request.form['talla_m'] or 0,
            request.form['talla_l'] or 0,
            request.form['talla_xl'] or 0,
            request.form['observaciones']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# AGREGAR EQUIPO (AJAX)
# ========================
@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Equipos (ID_Brigada, Categoria_Equipo, Nombre_Articulo, Cantidad, Observacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['categoria_equipo'],
            request.form['nombre_articulo'],
            request.form['cantidad'] or 0,
            request.form['observacion']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# AGREGAR LOGÍSTICA (AJAX)
# ========================
@app.route("/agregar_logistica", methods=["POST"])
def agregar_logistica():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Logistica (ID_Brigada, Nombre, Costo_Unitario, Observaciones)
            VALUES (?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['nombre'],
            request.form['costo_unitario'] or 0,
            request.form['observaciones']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# VER TODAS LAS BRIGADAS CON SUS ARTÍCULOS
# ========================
@app.route("/ver_todas")
def ver_todas():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Brigadas")
    brigadas = cursor.fetchall()

    cursor.execute("""
        SELECT t.*, b.Nombre_Brigada
        FROM TallasRopa t
        JOIN Brigadas b ON t.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, t.Tipo_Ropa
    """)
    tallas = cursor.fetchall()

    cursor.execute("""
        SELECT e.*, b.Nombre_Brigada
        FROM Equipos e
        JOIN Brigadas b ON e.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, e.Categoria_Equipo, e.Nombre_Articulo
    """)
    equipos = cursor.fetchall()

    cursor.execute("""
        SELECT l.*, b.Nombre_Brigada
        FROM Logistica l
        JOIN Brigadas b ON l.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, l.Nombre
    """)
    logistica = cursor.fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte Completo - Todas las Brigadas</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c2 100%);
                min-height: 100vh;
                color: #5d4e37;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 1500px; 
                margin: 0 auto; 
                padding: 30px 20px;
            }
            
            .header-section {
                background: linear-gradient(135deg, #d2691e 0%, #a0522d 100%);
                color: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 12px 40px rgba(210, 105, 30, 0.3);
                margin-bottom: 40px;
                position: relative;
                overflow: hidden;
            }
            
            .header-section::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .header-controls {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
            }
            
            .control-btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 500;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            .control-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            }
            
            .control-btn.print-btn {
                background: rgba(76, 175, 80, 0.2);
                border-color: rgba(76, 175, 80, 0.5);
            }
            
            .control-btn.print-btn:hover {
                background: rgba(76, 175, 80, 0.3);
            }
            
            .report-title {
                font-size: 2.5rem;
                font-weight: 300;
                letter-spacing: 2px;
                text-align: center;
                position: relative;
                z-index: 1;
                margin-bottom: 10px;
            }
            
            .report-subtitle {
                text-align: center;
                font-size: 1.1rem;
                opacity: 0.9;
                font-weight: 300;
                position: relative;
                z-index: 1;
            }
            
            .report-section {
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(139, 69, 19, 0.12);
                margin-bottom: 30px;
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .report-section:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 40px rgba(139, 69, 19, 0.18);
            }
            
            .section-header {
                background: linear-gradient(135deg, #cd853f 0%, #daa520 100%);
                color: white;
                padding: 25px 30px;
                display: flex;
                align-items: center;
                gap: 15px;
                font-size: 1.4rem;
                font-weight: 500;
                letter-spacing: 1px;
            }
            
            .section-body {
                padding: 30px;
            }
            
            .data-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 6px 25px rgba(139, 69, 19, 0.1);
                margin: 0;
            }
            
            .data-table th {
                background: linear-gradient(135deg, #8b4513 0%, #a0522d 100%);
                color: white;
                padding: 16px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 0.95rem;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            
            .data-table td {
                padding: 14px 12px;
                border-bottom: 1px solid #f0e6d6;
                background: white;
                font-size: 0.95rem;
                transition: background-color 0.3s ease;
            }
            
            .data-table tr:hover td {
                background: #faf5f0;
            }
            
            .data-table tr:last-child td {
                border-bottom: none;
            }
            
            .data-table tr:nth-child(even) td {
                background: #fefcf9;
            }
            
            .data-table tr:nth-child(even):hover td {
                background: #faf5f0;
            }
            
            .tag {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 0.85rem;
                font-weight: 600;
                text-align: center;
                letter-spacing: 0.5px;
            }
            
            .tag-brigade {
                background: linear-gradient(135deg, #ff8a50 0%, #ff7043 100%);
                color: white;
                box-shadow: 0 3px 10px rgba(255, 112, 67, 0.3);
            }
            
            .tag-category {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                color: #1565c0;
                border: 1px solid #90caf9;
            }
            
            .tag-quantity {
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                color: #2e7d32;
                border: 1px solid #81c784;
            }
            
            .tag-cost {
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                color: #ef6c00;
                border: 1px solid #ffb74d;
            }
            
            .tag-total {
                background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                color: #7b1fa2;
                border: 1px solid #ba68c8;
            }
            
            .highlight-cell {
                font-weight: bold;
                color: #d2691e;
            }
            
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #8b4513;
                opacity: 0.7;
            }
            
            .empty-state .icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            .footer-section {
                text-align: center;
                margin-top: 50px;
                padding: 30px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(139, 69, 19, 0.1);
            }
            
            .footer-section p {
                color: #8b4513;
                font-style: italic;
                font-size: 1.1rem;
            }
            
            .stats-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 6px 25px rgba(139, 69, 19, 0.1);
                border-left: 4px solid #d2691e;
            }
            
            .stat-number {
                font-size: 2.5rem;
                font-weight: bold;
                color: #d2691e;
                margin-bottom: 8px;
            }
            
            .stat-label {
                color: #8b4513;
                font-weight: 500;
                text-transform: uppercase;
                font-size: 0.9rem;
                letter-spacing: 1px;
            }
            
            @media print {
                body {
                    background: white;
                    color: #000;
                }
                
                .no-print {
                    display: none !important;
                }
                
                .header-section {
                    background: #d2691e;
                    box-shadow: none;
                    page-break-inside: avoid;
                }
                
                .report-section {
                    page-break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid #ddd;
                    margin-bottom: 20px;
                }
                
                .section-header {
                    background: #cd853f;
                }
                
                .data-table th {
                    background: #8b4513;
                }
                
                .control-btn {
                    display: none;
                }
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 20px 15px;
                }
                
                .report-title {
                    font-size: 2rem;
                }
                
                .header-controls {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .control-btn {
                    justify-content: center;
                }
                
                .data-table {
                    font-size: 0.85rem;
                }
                
                .data-table th,
                .data-table td {
                    padding: 10px 8px;
                }
                
                .stats-summary {
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                }
                
                .stat-number {
                    font-size: 2rem;
                }
            }
            
            @media (max-width: 480px) {
                .data-table th,
                .data-table td {
                    padding: 8px 6px;
                    font-size: 0.8rem;
                }
                
                .tag {
                    font-size: 0.75rem;
                    padding: 4px 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <div class="header-controls no-print">
                    <a href="/" class="control-btn">
                        <span>🔙</span>
                        <span>Volver a Brigadas</span>
                    </a>
                    <a href="javascript:window.print()" class="control-btn print-btn">
                        <span>🖨️</span>
                        <span>Imprimir Reporte</span>
                    </a>
                </div>
                
                <h1 class="report-title">📋 Reporte Integral de Brigadas</h1>
                <div class="report-subtitle">Inventario Completo y Estado Operativo</div>
            </div>

            <!-- Sección de Estadísticas Generales -->
            <div class="stats-summary no-print">
                <div class="stat-card">
                    <div class="stat-number">{{ brigadas|length }}</div>
                    <div class="stat-label">Brigadas Activas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ tallas|length }}</div>
                    <div class="stat-label">Items de Ropa</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ equipos|length }}</div>
                    <div class="stat-label">Equipos Registrados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ logistica|length }}</div>
                    <div class="stat-label">Items Logísticos</div>
                </div>
            </div>

            <!-- Información General de Brigadas -->
            <div class="report-section">
                <div class="section-header">
                    <span>🚒</span>
                    <span>Información General de Brigadas</span>
                </div>
                <div class="section-body">
                    {% if brigadas %}
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nombre Brigada</th>
                                    <th>N° Bomberos</th>
                                    <th>Cel. Comandante</th>
                                    <th>Encargado Logística</th>
                                    <th>Cel. Logística</th>
                                    <th>N° Emergencia</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for brigada in brigadas %}
                                <tr>
                                    <td class="highlight-cell">#{{ brigada[0] }}</td>
                                    <td><span class="tag tag-brigade">{{ brigada[1] }}</span></td>
                                    <td>{{ brigada[2] or 'N/A' }}</td>
                                    <td>{{ brigada[3] or 'N/A' }}</td>
                                    <td>{{ brigada[4] or 'N/A' }}</td>
                                    <td>{{ brigada[5] or 'N/A' }}</td>
                                    <td>{{ brigada[6] or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">🚒</div>
                            <p>No hay brigadas registradas en el sistema</p>
                        </div>
                    {% endif %}
                </div>
            </div>

            <!-- Inventario de Tallas -->
            <div class="report-section">
                <div class="section-header">
                    <span>👕</span>
                    <span>Inventario de Tallas por Brigada</span>
                </div>
                <div class="section-body">
                    {% if tallas %}
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Brigada</th>
                                    <th>Tipo de Ropa</th>
                                    <th>XS</th>
                                    <th>S</th>
                                    <th>M</th>
                                    <th>L</th>
                                    <th>XL</th>
                                    <th>Total</th>
                                    <th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for talla in tallas %}
                                <tr>
                                    <td><span class="tag tag-brigade">{{ talla[9] }}</span></td>
                                    <td class="highlight-cell">{{ talla[2] }}</td>
                                    <td>{{ talla[3] }}</td>
                                    <td>{{ talla[4] }}</td>
                                    <td>{{ talla[5] }}</td>
                                    <td>{{ talla[6] }}</td>
                                    <td>{{ talla[7] }}</td>
                                    <td><span class="tag tag-total">{{ talla[3] + talla[4] + talla[5] + talla[6] + talla[7] }}</span></td>
                                    <td>{{ talla[8] or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">👕</div>
                            <p>No hay tallas registradas en el sistema</p>
                        </div>
                    {% endif %}
                </div>
            </div>

            <!-- Inventario de Equipos -->
            <div class="report-section">
                <div class="section-header">
                    <span>🛠️</span>
                    <span>Inventario de Equipos y Artículos por Brigada</span>
                </div>
                <div class="section-body">
                    {% if equipos %}
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Brigada</th>
                                    <th>Categoría</th>
                                    <th>Nombre del Artículo</th>
                                    <th>Cantidad</th>
                                    <th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for equipo in equipos %}
                                <tr>
                                    <td><span class="tag tag-brigade">{{ equipo[6] }}</span></td>
                                    <td><span class="tag tag-category">{{ equipo[2] }}</span></td>
                                    <td class="highlight-cell">{{ equipo[3] }}</td>
                                    <td><span class="tag tag-quantity">{{ equipo[4] }}</span></td>
                                    <td>{{ equipo[5] or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">🛠️</div>
                            <p>No hay equipos registrados en el sistema</p>
                        </div>
                    {% endif %}
                </div>
            </div>

            <!-- Inventario de Logística -->
            <div class="report-section">
                <div class="section-header">
                    <span>📦</span>
                    <span>Inventario de Logística por Brigada</span>
                </div>
                <div class="section-body">
                    {% if logistica %}
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Brigada</th>
                                    <th>Nombre del Item</th>
                                    <th>Costo Unitario</th>
                                    <th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in logistica %}
                                <tr>
                                    <td><span class="tag tag-brigade">{{ item[5] }}</span></td>
                                    <td class="highlight-cell">{{ item[2] }}</td>
                                    <td><span class="tag tag-cost">${{ "%.2f"|format(item[3] or 0) }}</span></td>
                                    <td>{{ item[4] or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="empty-state">
                            <div class="icon">📦</div>
                            <p>No hay items de logística registrados en el sistema</p>
                        </div>
                    {% endif %}
                </div>
            </div>

            <div class="footer-section no-print">
                <p>Reporte generado automáticamente por el Sistema Profesional de Gestión de Brigadas</p>
            </div>
        </div>
    </body>
    </html>
    """, brigadas=brigadas, tallas=tallas, equipos=equipos, logistica=logistica)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)