from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__, template_folder="./templates")
app.secret_key = 'secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['LaboratorioDoofenshmirtz']

exams_collection = db['exams']
categories_collection = db['categories']
indications_collection = db['indications']
users_collection = db['users']

# Validar sesión de usuario
def validar_sesion():
    if 'username' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('login'))

# Ruta de inicio para usuarios no logeados
@app.route('/')
def home_no_logeado():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('home_no_logeado.html')

# Rutas para la autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        if user and user['password'] == password:
            session['username'] = username
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('render_layout'))  # Redirige al layout después de iniciar sesión
        else:
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            existing_user = users_collection.find_one({"username": username})
            if existing_user:
                flash('El nombre de usuario ya está en uso. Por favor, elige otro.', 'error')
            else:
                new_user = {"username": username, "password": password}
                users_collection.insert_one(new_user)
                flash('Registro exitoso. Por favor, inicia sesión.', 'success')
                return redirect(url_for('login'))
        else:
            flash('Las contraseñas no coinciden. Por favor, inténtalo de nuevo.', 'error')
    return render_template('register.html')

# Función para renderizar el layout
@app.route('/render_layout')
def render_layout():
    validar_sesion()
    return render_template('layout.html')

# Ruta de inicio para usuarios logeados
@app.route('/home', methods=['GET', 'POST'])
def home_logeado():
    validar_sesion()
    return redirect(url_for('render_layout'))  # Redirige al layout después de iniciar sesión

# Rutas para CRUD de exámenes
@app.route('/crear_examen', methods=['GET', 'POST'])
def crear_examen():
    validar_sesion()
    if request.method == 'POST':
        codigo = request.form['codigo']
        categoria = request.form['categoria']
        tipo_muestra = request.form['tipo_muestra']
        precio = request.form['precio']
        indicaciones = request.form.getlist('indicaciones')

        examen = {
            "codigo": codigo,
            "categoria": categoria,
            "tipo_muestra": tipo_muestra,
            "precio": precio,
            "indicaciones": indicaciones
        }

        exams_collection.insert_one(examen)
        flash('Examen creado correctamente', 'success')
        return redirect(url_for('catalogo'))
    
    categorias = categories_collection.find()
    indicaciones = indications_collection.find()
    return render_template('crear_examen.html', categorias=categorias, indicaciones=indicaciones)

@app.route('/editar_examen/<examen_id>', methods=['GET', 'POST'])
def editar_examen(examen_id):
    validar_sesion()
    examen = exams_collection.find_one({"_id": ObjectId(examen_id)})
    if request.method == 'POST':
        codigo = request.form['codigo']
        categoria = request.form['categoria']
        tipo_muestra = request.form['tipo_muestra']
        precio = request.form['precio']
        indicaciones = request.form.getlist('indicaciones')

        exams_collection.update_one({"_id": ObjectId(examen_id)}, {"$set": {
            "codigo": codigo,
            "categoria": categoria,
            "tipo_muestra": tipo_muestra,
            "precio": precio,
            "indicaciones": indicaciones
        }})
        flash('Examen actualizado correctamente', 'success')
        return redirect(url_for('catalogo'))
    
    categorias = categories_collection.find()
    indicaciones = indications_collection.find()
    return render_template('editar_examen.html', examen=examen, categorias=categorias, indicaciones=indicaciones)

@app.route('/eliminar_examen/<examen_id>', methods=['POST'])
def eliminar_examen(examen_id):
    validar_sesion()
    exams_collection.delete_one({"_id": ObjectId(examen_id)})
    flash('Examen eliminado correctamente', 'success')
    return redirect(url_for('catalogo'))

# Ruta para ver exámenes en forma de tabla
@app.route('/ver_examenes', methods=['GET'])
def ver_examenes():
    validar_sesion()
    exams = exams_collection.find()
    return render_template('ver_examenes.html', exams=exams)

# Rutas para CRUD de categorías
@app.route('/crear_categoria', methods=['GET', 'POST'])
def crear_categoria():
    validar_sesion()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        categoria = {"nombre": nombre, "descripcion": descripcion}
        categories_collection.insert_one(categoria)
        flash('Categoría creada correctamente', 'success')
        return redirect(url_for('ver_categorias'))
    
    return render_template('crear_categoria.html')

@app.route('/editar_categoria/<categoria_id>', methods=['GET', 'POST'])
def editar_categoria(categoria_id):
    validar_sesion()
    categoria = categories_collection.find_one({"_id": ObjectId(categoria_id)})
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        categories_collection.update_one({"_id": ObjectId(categoria_id)}, {"$set": {
            "nombre": nombre,
            "descripcion": descripcion
        }})
        flash('Categoría actualizada correctamente', 'success')
        return redirect(url_for('ver_categorias'))
    
    return render_template('editar_categoria.html', categoria=categoria)

@app.route('/eliminar_categoria/<categoria_id>', methods=['POST'])
def eliminar_categoria(categoria_id):
    validar_sesion()
    categories_collection.delete_one({"_id": ObjectId(categoria_id)})
    flash('Categoría eliminada correctamente', 'success')
    return redirect(url_for('ver_categorias'))

# Ruta para ver categorías en forma de tabla
@app.route('/ver_categorias', methods=['GET'])
def ver_categorias():
    validar_sesion()
    categorias = categories_collection.find()
    return render_template('ver_categorias.html', categorias=categorias)

# Rutas para CRUD de indicaciones
@app.route('/crear_indicacion', methods=['GET', 'POST'])
def crear_indicacion():
    validar_sesion()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        indicacion = {"nombre": nombre, "descripcion": descripcion}
        indications_collection.insert_one(indicacion)
        flash('Indicación creada correctamente', 'success')
        return redirect(url_for('ver_indicaciones'))
    
    return render_template('crear_indicacion.html')

@app.route('/editar_indicacion/<indicacion_id>', methods=['GET', 'POST'])
def editar_indicacion(indicacion_id):
    validar_sesion()
    indicacion = indications_collection.find_one({"_id": ObjectId(indicacion_id)})
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        indications_collection.update_one({"_id": ObjectId(indicacion_id)}, {"$set": {
            "nombre": nombre,
            "descripcion": descripcion
        }})
        flash('Indicación actualizada correctamente', 'success')
        return redirect(url_for('ver_indicaciones'))
    
    return render_template('editar_indicacion.html', indicacion=indicacion)

@app.route('/eliminar_indicacion/<indicacion_id>', methods=['POST'])
def eliminar_indicacion(indicacion_id):
    validar_sesion()
    indications_collection.delete_one({"_id": ObjectId(indicacion_id)})
    flash('Indicación eliminada correctamente', 'success')
    return redirect(url_for('ver_indicaciones'))

# Ruta para ver indicaciones en forma de tabla
@app.route('/ver_indicaciones', methods=['GET'])
def ver_indicaciones():
    validar_sesion()
    indicaciones = indications_collection.find()
    return render_template('ver_indicaciones.html', indicaciones=indicaciones)

# Ruta para el catálogo
@app.route('/catalogo', methods=['GET'])
def catalogo():
    validar_sesion()
    categoria_filtro = request.args.get('categoria')
    tipo_muestra_filtro = request.args.get('tipo_muestra')

    if categoria_filtro:
        exams = exams_collection.find({"categoria": categoria_filtro})
    elif tipo_muestra_filtro:
        exams = exams_collection.find({"tipo_muestra": tipo_muestra_filtro})
    else:
        exams = exams_collection.find()

    categorias = categories_collection.find()
    return render_template('catalogo.html', exams=exams, categorias=categorias)

# Ruta para ver un examen individual
@app.route('/ver_examen/<examen_id>', methods=['GET'])
def ver_examen(examen_id):
    validar_sesion()
    exam = exams_collection.find_one({"_id": ObjectId(examen_id)})
    return render_template('ver_examen.html', exam=exam)

# Ruta para ver todas las categorías en forma de tabla
"""@app.route('/ver_categorias', methods=['GET'])
def ver_categorias():
    validar_sesion()
    categorias = categories_collection.find()
    return render_template('ver_categorias.html', categorias=categorias)

# Ruta para ver todas las indicaciones en forma de tabla
@app.route('/ver_indicaciones', methods=['GET'])
def ver_indicaciones():
    validar_sesion()
    indicaciones = indications_collection.find()
    return render_template('ver_indicaciones.html', indicaciones=indicaciones)"""

# Ruta para generar el reporte
@app.route('/reporte', methods=['GET'])
def reporte():
    validar_sesion()
    # Obtener el número de exámenes por categoría
    categories_count = exams_collection.aggregate([
        {"$group": {"_id": "$categoria", "count": {"$sum": 1}}}
    ])
    # Obtener la indicación de examen más común
    common_indication = exams_collection.aggregate([
        {"$unwind": "$indicaciones"},
        {"$group": {"_id": "$indicaciones", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ])
    # Agrupar exámenes por precio en intervalos
    price_intervals = exams_collection.aggregate([
        {"$bucket": {
            "groupBy": "$precio",
            "boundaries": [0, 100, 200, 300, 500, float('inf')],
            "default": "Other",
            "output": {
                "count": {"$sum": 1}
            }
        }}
    ])

    return render_template('reporte.html', categories_count=categories_count,
                           common_indication=common_indication, price_intervals=price_intervals)

if __name__ == "__main__":
    app.run(debug=True)
