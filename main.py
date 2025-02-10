# create virutal enviroment = python3 -m venv venv
# open virtual environment = source venv/bin/activate
# install dependencies = pip install -r requirements.txt
# turn on the api = python3/hypercorn main.py

import os
import socket
import psycopg2
from flask_cors import CORS
from dotenv import load_dotenv
from psycopg2 import Error as PGError
from psycopg2.extras import DictCursor
from flask import Flask, jsonify, request
from psycopg2.errors import UndefinedTable
from flask_restx import Api, Namespace, Resource, reqparse

load_dotenv()

HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
USER = os.getenv('DB_USER')
DATABASE = os.getenv('DB_NAME')
PASSWORD = os.getenv('DB_PASSWORD')

if not all([HOST, PORT, USER, DATABASE, PASSWORD]):
    raise ValueError("Missing one or more required environment variables for database connection.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app, version='1.0', title='Banco de Tierras', description='API para obtener todos los datos de la base de datos de Banco de Tierras')

def create_connection():
    try:
        ipv4_address = socket.gethostbyname(HOST)
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=ipv4_address,
            port=PORT,
            dbname=DATABASE,
            sslmode='require'
        )
        print("Connected to the database")
        return connection
    except socket.gaierror as e:
        print(f"Error resolving the host: {e}")
        raise
    except PGError as e:
        print(f"Error connecting to the database: {e}")
        raise

@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        connection = create_connection()
        return {"message": "Connection successful"}
    except Exception as e:
        return {"message": f"Connection failed: {str(e)}"}, 500


def execute_query(query, columns, params=None):
    params = params or ()  # Evita problemas si params es None
    connection = create_connection()
    cursor = connection.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        if result:
            return [dict(zip(columns, row)) for row in result]
        else:
            return []  # O manejarlo como desees si no hay resultados
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        cursor.close()
        connection.close()  # O usa el connection pool si decides implementarlo

generic_parser = reqparse.RequestParser()
generic_parser.add_argument('page', type=int, help='Opcional: Número de página', default=1)
generic_parser.add_argument('page_size', type=int, help='Opcional: Cantidad de registros por página', default=100)


# CREATE TABLE sociedad (
#     id SERIAL PRIMARY KEY,
#     porcentaje_participacion FLOAT NOT NULL UNIQUE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
sociedades_parser = reqparse.RequestParser()
sociedades_parser.add_argument('porcentaje_participacion', type=float, help='Opcional: Porcentaje de participación')

sociedades_client = Namespace('sociedades', description='Sociedades de la base de datos')
@sociedades_client.route('/')
class Sociedades(Resource):
    @api.expect(generic_parser, sociedades_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = sociedades_parser.parse_args()

        porcentaje_participacion = another_args.get('porcentaje_participacion')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'porcentaje_participacion',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                porcentaje_participacion,
                created_at,
                updated_at
            FROM sociedad
            WHERE
                (%s IS NULL OR porcentaje_participacion = %s)
            LIMIT %s OFFSET %s;
        """

        params = (porcentaje_participacion, porcentaje_participacion, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE estatus_legal (
#     id SERIAL PRIMARY KEY,
#     nombre VARCHAR(255) NOT NULL UNIQUE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
estatus_legal_parser = reqparse.RequestParser()
estatus_legal_parser.add_argument('nombre', type=str, help='Opcional: Nombre del estatus legal')

estatus_legal_client = Namespace('estatus_legal', description='Estatus legal de la base de datos')
@estatus_legal_client.route('/')
class EstatusLegal(Resource):
    @api.expect(generic_parser, estatus_legal_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = estatus_legal_parser.parse_args()

        nombre = another_args.get('nombre')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'nombre',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                nombre,
                created_at,
                updated_at
            FROM estatus_legal
            WHERE
                (%s IS NULL OR nombre = %s)
            LIMIT %s OFFSET %s;
        """

        params = (nombre, nombre, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE ubicacion (
#     id SERIAL PRIMARY KEY,
#     nombre VARCHAR(255) NOT NULL UNIQUE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
ubicacion_parser = reqparse.RequestParser()
ubicacion_parser.add_argument('nombre', type=str, help='Opcional: Nombre de la ubicación')

ubicacion_client = Namespace('ubicacion', description='Ubicación de la base de datos')
@ubicacion_client.route('/')
class Ubicacion(Resource):
    @api.expect(generic_parser, ubicacion_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = ubicacion_parser.parse_args()

        nombre = another_args.get('nombre')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'nombre',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                nombre,
                created_at,
                updated_at
            FROM ubicacion
            WHERE
                (%s IS NULL OR nombre = %s)
            LIMIT %s OFFSET %s;
        """

        params = (nombre, nombre, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE proyecto (
#     id SERIAL PRIMARY KEY,
#     clave VARCHAR(255) NOT NULL UNIQUE,
#     prioridad INT,
#     nombre VARCHAR(255) NOT NULL UNIQUE,
#     superficie_total FLOAT NOT NULL,
#     propietario VARCHAR(255) NOT NULL,
#     tipo_propiedad VARCHAR(255) NOT NULL,
#     socios VARCHAR(255),
#     rfc VARCHAR(255),
#     tiene_garantia BOOLEAN,
#     vocacion VARCHAR(255) NOT NULL,
#     vocacion_especifica VARCHAR(255),
#     responsable VARCHAR(255),
#     estatus_activo_no_activo VARCHAR(255) NOT NULL,
#     categoria VARCHAR(255) NOT NULL,
#     comentarios TEXT,
#     abogado VARCHAR(255),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
proyectos_parser = reqparse.RequestParser()
proyectos_parser.add_argument('clave', type=str, help='Opcional: Clave del proyecto')
proyectos_parser.add_argument('prioridad', type=int, help='Opcional: Prioridad del proyecto')
proyectos_parser.add_argument('nombre', type=str, help='Opcional: Nombre del proyecto')
proyectos_parser.add_argument('superficie_total', type=float, help='Opcional: Superficie total del proyecto')
proyectos_parser.add_argument('propietario', type=str, help='Opcional: Propietario del proyecto')
proyectos_parser.add_argument('tipo_propiedad', type=str, help='Opcional: Tipo de propiedad del proyecto')
proyectos_parser.add_argument('socios', type=str, help='Opcional: Socios del proyecto')
proyectos_parser.add_argument('rfc', type=str, help='Opcional: RFC del proyecto')
proyectos_parser.add_argument('tiene_garantia', type=bool, help='Opcional: ¿Tiene garantía?')
proyectos_parser.add_argument('vocacion', type=str, help='Opcional: Vocación del proyecto')
proyectos_parser.add_argument('vocacion_especifica', type=str, help='Opcional: Vocación específica del proyecto')
proyectos_parser.add_argument('responsable', type=str, help='Opcional: Responsable del proyecto')
proyectos_parser.add_argument('estatus_activo_no_activo', type=str, help='Opcional: Estatus activo/no activo del proyecto')
proyectos_parser.add_argument('categoria', type=str, help='Opcional: Categoría del proyecto')
proyectos_parser.add_argument('abogado', type=str, help='Opcional: Abogado del proyecto')
proyectos_parser.add_argument('sociedad', type=int, help='Opcional: ID de la sociedad')
proyectos_parser.add_argument('estatus_legal', type=int, help='Opcional: ID del estatus legal')
proyectos_parser.add_argument('ubicacion', type=int, help='Opcional: ID de la ubicación')

proyectos_client = Namespace('proyectos', description='Proyectos de la base de datos')
@proyectos_client.route('/')
class Proyectos(Resource):
    @api.expect(generic_parser, proyectos_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = proyectos_parser.parse_args()

        clave = another_args.get('clave')
        prioridad = another_args.get('prioridad')
        nombre = another_args.get('nombre')
        superficie_total = another_args.get('superficie_total')
        propietario = another_args.get('propietario')
        tipo_propiedad = another_args.get('tipo_propiedad')
        socios = another_args.get('socios')
        rfc = another_args.get('rfc')
        tiene_garantia = another_args.get('tiene_garantia')
        vocacion = another_args.get('vocacion')
        vocacion_especifica = another_args.get('vocacion_especifica')
        responsable = another_args.get('responsable')
        estatus_activo_no_activo = another_args.get('estatus_activo_no_activo')
        categoria = another_args.get('categoria')
        abogado = another_args.get('abogado')
        sociedad = another_args.get('sociedad')
        estatus_legal = another_args.get('estatus_legal')
        ubicacion = another_args.get('ubicacion')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'clave',
            'prioridad',
            'nombre',
            'superficie_total',
            'propietario',
            'tipo_propiedad',
            'socios',
            'rfc',
            'tiene_garantia',
            'vocacion',
            'vocacion_especifica',
            'responsable',
            'estatus_activo_no_activo',
            'categoria',
            'comentarios',
            'abogado',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                p.id,
                p.clave,
                p.prioridad,
                p.nombre,
                p.superficie_total,
                p.propietario,
                p.tipo_propiedad,
                p.socios,
                p.rfc,
                p.tiene_garantia,
                p.vocacion,
                p.vocacion_especifica,
                p.responsable,
                p.estatus_activo_no_activo,
                p.categoria,
                p.comentarios,
                p.abogado,
                p.created_at,
                p.updated_at,
                s.id AS sociedad_id,
                s.porcentaje_participacion,
                u.id AS ubicacion_id,
                u.nombre AS ubicacion_nombre,
                e.id AS estatus_legal_id,
                e.nombre AS estatus_legal_nombre
            FROM proyecto p
            LEFT JOIN proyecto_sociedad ps ON p.id = ps.proyecto_id
            LEFT JOIN sociedad s ON ps.sociedad_id = s.id
            LEFT JOIN proyecto_estatus_ubicacion peu ON p.id = peu.proyecto_id
            LEFT JOIN ubicacion u ON peu.ubicacion_id = u.id
            LEFT JOIN estatus_legal e ON peu.estatus_legal_id = e.id
            WHERE
                (%s IS NULL OR p.clave = %s)
                AND (%s IS NULL OR p.prioridad = %s)
                AND (%s IS NULL OR p.nombre = %s)
                AND (%s IS NULL OR p.superficie_total = %s)
                AND (%s IS NULL OR p.propietario = %s)
                AND (%s IS NULL OR p.tipo_propiedad = %s)
                AND (%s IS NULL OR p.socios = %s)
                AND (%s IS NULL OR p.rfc = %s)
                AND (%s IS NULL OR p.tiene_garantia = %s)
                AND (%s IS NULL OR p.vocacion = %s)
                AND (%s IS NULL OR p.vocacion_especifica = %s)
                AND (%s IS NULL OR p.responsable = %s)
                AND (%s IS NULL OR p.estatus_activo_no_activo = %s)
                AND (%s IS NULL OR p.categoria = %s)
                AND (%s IS NULL OR p.abogado = %s)
                AND (%s IS NULL OR s.id = %s)
                AND (%s IS NULL OR u.id = %s)
                AND (%s IS NULL OR e.id = %s)
            LIMIT %s OFFSET %s;
        """

        params = (
            clave, clave,
            prioridad, prioridad,
            nombre, nombre,
            superficie_total, superficie_total,
            propietario, propietario,
            tipo_propiedad, tipo_propiedad,
            socios, socios,
            rfc, rfc,
            tiene_garantia, tiene_garantia,
            vocacion, vocacion,
            vocacion_especifica, vocacion_especifica,
            responsable, responsable,
            estatus_activo_no_activo, estatus_activo_no_activo,
            categoria, categoria,
            abogado, abogado,
            sociedad, sociedad,
            ubicacion, ubicacion,
            estatus_legal, estatus_legal,
            page_size, offset
        )

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE proyecto_sociedad (
#     id SERIAL PRIMARY KEY,
#     valor FLOAT NOT NULL,
#     proyecto_id INT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
#     sociedad_id INT NOT NULL REFERENCES sociedad(id) ON DELETE CASCADE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE (proyecto_id, sociedad_id)
# );
proyecto_sociedad_parser = reqparse.RequestParser()
proyecto_sociedad_parser.add_argument('valor', type=float, help='Opcional: Valor de la sociedad')

proyecto_sociedad_client = Namespace('proyecto_sociedad', description='Proyecto Sociedad de la base de datos')
@proyecto_sociedad_client.route('/')
class ProyectoSociedad(Resource):
    @api.expect(generic_parser, proyecto_sociedad_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = proyecto_sociedad_parser.parse_args()

        valor = another_args.get('valor')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'valor',
            'proyecto_id',
            'sociedad_id',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                valor,
                proyecto_id,
                sociedad_id,
                created_at,
                updated_at
            FROM proyecto_sociedad
            WHERE
                (%s IS NULL OR valor = %s)
            LIMIT %s OFFSET %s;
        """

        params = (valor, valor, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE proyecto_estatus_ubicacion (
#     id SERIAL PRIMARY KEY,
#     proyecto_id INT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
#     ubicacion_id INT NOT NULL REFERENCES ubicacion(id) ON DELETE CASCADE,
#     estatus_legal_id INT NOT NULL REFERENCES estatus_legal(id) ON DELETE CASCADE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE (
#         proyecto_id,
#         ubicacion_id,
#         estatus_legal_id
#     )
# );
proyecto_estatus_ubicacion_parser = reqparse.RequestParser()

proyecto_estatus_ubicacion_client = Namespace('proyecto_estatus_ubicacion', description='Proyecto Estatus Ubicación de la base de datos')
@proyecto_estatus_ubicacion_client.route('/')
class ProyectoEstatusUbicacion(Resource):
    @api.expect(generic_parser, proyecto_estatus_ubicacion_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'proyecto_id',
            'ubicacion_id',
            'estatus_legal_id',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                proyecto_id,
                ubicacion_id,
                estatus_legal_id,
                created_at,
                updated_at
            FROM proyecto_estatus_ubicacion
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE propiedad (
#     id SERIAL PRIMARY KEY,
#     clave VARCHAR(255) NOT NULL UNIQUE,
#     nombre VARCHAR(255) NOT NULL,
#     superficie FLOAT NOT NULL,
#     valor_comercial FLOAT NOT NULL,
#     valor_comercial_usd FLOAT NOT NULL,
#     anio_valor_comercial INT,
#     clave_catastral VARCHAR(255) NOT NULL,
#     base_predial FLOAT NOT NULL,
#     adeudo_predial FLOAT,
#     anios_pend_predial INT,
#     comentarios TEXT,
#     proyecto_id INT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
propiedades_parser = reqparse.RequestParser()
propiedades_parser.add_argument('clave', type=str, help='Opcional: Clave de la propiedad')
propiedades_parser.add_argument('nombre', type=str, help='Opcional: Nombre de la propiedad')
propiedades_parser.add_argument('superficie', type=float, help='Opcional: Superficie de la propiedad')
propiedades_parser.add_argument('valor_comercial', type=float, help='Opcional: Valor comercial de la propiedad')
propiedades_parser.add_argument('valor_comercial_usd', type=float, help='Opcional: Valor comercial en USD de la propiedad')
propiedades_parser.add_argument('anio_valor_comercial', type=int, help='Opcional: Año del valor comercial de la propiedad')
propiedades_parser.add_argument('clave_catastral', type=str, help='Opcional: Clave catastral de la propiedad')
propiedades_parser.add_argument('base_predial', type=float, help='Opcional: Base predial de la propiedad')
propiedades_parser.add_argument('adeudo_predial', type=float, help='Opcional: Adeudo predial de la propiedad')
propiedades_parser.add_argument('anios_pend_predial', type=int, help='Opcional: Años pendientes de predial de la propiedad')
propiedades_parser.add_argument('proyecto_id', type=int, help='Opcional: ID del proyecto')

propiedades_client = Namespace('propiedades', description='Propiedades de la base de datos')
@propiedades_client.route('/')
class Propiedades(Resource):
    @api.expect(generic_parser, propiedades_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = propiedades_parser.parse_args()

        clave = another_args.get('clave')
        nombre = another_args.get('nombre')
        superficie = another_args.get('superficie')
        valor_comercial = another_args.get('valor_comercial')
        valor_comercial_usd = another_args.get('valor_comercial_usd')
        anio_valor_comercial = another_args.get('anio_valor_comercial')
        clave_catastral = another_args.get('clave_catastral')
        base_predial = another_args.get('base_predial')
        adeudo_predial = another_args.get('adeudo_predial')
        anios_pend_predial = another_args.get('anios_pend_predial')
        proyecto_id = another_args.get('proyecto_id')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'clave',
            'nombre',
            'superficie',
            'valor_comercial',
            'valor_comercial_usd',
            'anio_valor_comercial',
            'clave_catastral',
            'base_predial',
            'adeudo_predial',
            'anios_pend_predial',
            'comentarios',
            'proyecto_id',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                id,
                clave,
                nombre,
                superficie,
                valor_comercial,
                valor_comercial_usd,
                anio_valor_comercial,
                clave_catastral,
                base_predial,
                adeudo_predial,
                anios_pend_predial,
                comentarios,
                proyecto_id,
                created_at,
                updated_at
            FROM propiedad
            WHERE
                (%s IS NULL OR clave = %s)
                AND (%s IS NULL OR nombre = %s)
                AND (%s IS NULL OR superficie = %s)
                AND (%s IS NULL OR valor_comercial = %s)
                AND (%s IS NULL OR valor_comercial_usd = %s)
                AND (%s IS NULL OR anio_valor_comercial = %s)
                AND (%s IS NULL OR clave_catastral = %s)
                AND (%s IS NULL OR base_predial = %s)
                AND (%s IS NULL OR adeudo_predial = %s)
                AND (%s IS NULL OR anios_pend_predial = %s)
                AND (%s IS NULL OR proyecto_id = %s)
            LIMIT %s OFFSET %s;
        """

        params = (
            clave, clave,
            nombre, nombre,
            superficie, superficie,
            valor_comercial, valor_comercial,
            valor_comercial_usd, valor_comercial_usd,
            anio_valor_comercial, anio_valor_comercial,
            clave_catastral, clave_catastral,
            base_predial, base_predial,
            adeudo_predial, adeudo_predial,
            anios_pend_predial, anios_pend_predial,
            proyecto_id, proyecto_id,
            page_size, offset
        )

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE renta(
#     id SERIAL PRIMARY KEY,
#     nombre_comercial VARCHAR(255) NOT NULL,
#     razon_social VARCHAR(255),
#     renta_iva_incluida FLOAT NOT NULL,
#     deposito_garantia_concepto VARCHAR(255),
#     deposito_garantia_renta FLOAT,
#     meses_gracia_concepto VARCHAR(255),
#     meses_gracia_fecha_inicio DATE,
#     meses_gracia_fecha_fin DATE,
#     renta_anticipada_concepto VARCHAR(255),
#     renta_anticipada_fecha_inicio DATE,
#     renta_anticipada_fecha_fin DATE,
#     renta_anticipada_renta_iva_incluida FLOAT,
#     incremento_mes VARCHAR(255),
#     incremento_descripcion VARCHAR(255),
#     inicio_vigencia DATE NOT NULL,
#     fin_vigencia_forzosa DATE NOT NULL,
#     fin_vigencia_no_forzosa DATE,
#     vigencia VARCHAR(255),
#     tiempo_restante VARCHAR(255),
#     incidencias TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
renta_parser = reqparse.RequestParser()
renta_parser.add_argument('nombre_comercial', type=str, help='Opcional: Nombre comercial de la renta')
renta_parser.add_argument('razon_social', type=str, help='Opcional: Razón social de la renta')
renta_parser.add_argument('renta_iva_incluida', type=float, help='Opcional: Renta con IVA incluido')
renta_parser.add_argument('deposito_garantia_renta', type=float, help='Opcional: Renta del depósito de garantía')
renta_parser.add_argument('meses_gracia_fecha_inicio', type=str, help='Opcional: Fecha de inicio de los meses de gracia')
renta_parser.add_argument('meses_gracia_fecha_fin', type=str, help='Opcional: Fecha de fin de los meses de gracia')
renta_parser.add_argument('renta_anticipada_fecha_inicio', type=str, help='Opcional: Fecha de inicio de la renta anticipada')
renta_parser.add_argument('renta_anticipada_fecha_fin', type=str, help='Opcional: Fecha de fin de la renta anticipada')
renta_parser.add_argument('renta_anticipada_renta_iva_incluida', type=float, help='Opcional: Renta con IVA incluido de la renta anticipada')
renta_parser.add_argument('incremento_mes', type=str, help='Opcional: Incremento por mes')
renta_parser.add_argument('inicio_vigencia', type=str, help='Opcional: Fecha de inicio de la vigencia')
renta_parser.add_argument('fin_vigencia_forzosa', type=str, help='Opcional: Fecha de fin de la vigencia forzosa')
renta_parser.add_argument('fin_vigencia_no_forzosa', type=str, help='Opcional: Fecha de fin de la vigencia no forzosa')
renta_parser.add_argument('vigencia', type=str, help='Opcional: Vigencia')
renta_parser.add_argument('tiempo_restante', type=str, help='Opcional: Tiempo restante')

renta_client = Namespace('renta', description='Renta de la base de datos')
@renta_client.route('/')
class Renta(Resource):
    @api.expect(generic_parser, renta_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = renta_parser.parse_args()

        nombre_comercial = another_args.get('nombre_comercial')
        razon_social = another_args.get('razon_social')
        renta_iva_incluida = another_args.get('renta_iva_incluida')
        deposito_garantia_renta = another_args.get('deposito_garantia_renta')
        meses_gracia_fecha_inicio = another_args.get('meses_gracia_fecha_inicio')
        meses_gracia_fecha_fin = another_args.get('meses_gracia_fecha_fin')
        renta_anticipada_fecha_inicio = another_args.get('renta_anticipada_fecha_inicio')
        renta_anticipada_fecha_fin = another_args.get('renta_anticipada_fecha_fin')
        renta_anticipada_renta_iva_incluida = another_args.get('renta_anticipada_renta_iva_incluida')
        incremento_mes = another_args.get('incremento_mes')
        inicio_vigencia = another_args.get('inicio_vigencia')
        fin_vigencia_forzosa = another_args.get('fin_vigencia_forzosa')
        fin_vigencia_no_forzosa = another_args.get('fin_vigencia_no_forzosa')
        vigencia = another_args.get('vigencia')
        tiempo_restante = another_args.get('tiempo_restante')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'nombre_comercial',
            'razon_social',
            'renta_iva_incluida',
            'deposito_garantia_concepto',
            'deposito_garantia_renta',
            'meses_gracia_concepto',
            'meses_gracia_fecha_inicio',
            'meses_gracia_fecha_fin',
            'renta_anticipada_concepto',
            'renta_anticipada_fecha_inicio',
            'renta_anticipada_fecha_fin',
            'renta_anticipada_renta_iva_incluida',
            'incremento_mes',
            'incremento_descripcion',
            'inicio_vigencia',
            'fin_vigencia_forzosa',
            'fin_vigencia_no_forzosa',
            'vigencia',
            'tiempo_restante',
            'incidencias',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT 
                id,
                nombre_comercial,
                razon_social,
                renta_iva_incluida,
                deposito_garantia_concepto,
                deposito_garantia_renta,
                meses_gracia_concepto,
                meses_gracia_fecha_inicio,
                meses_gracia_fecha_fin,
                renta_anticipada_concepto,
                renta_anticipada_fecha_inicio,
                renta_anticipada_fecha_fin,
                renta_anticipada_renta_iva_incluida,
                incremento_mes,
                incremento_descripcion,
                inicio_vigencia,
                fin_vigencia_forzosa,
                fin_vigencia_no_forzosa,
                vigencia,
                tiempo_restante,
                incidencias,
                created_at,
                updated_at
            FROM renta
            WHERE
                (%s IS NULL OR nombre_comercial = %s)
                AND (%s IS NULL OR razon_social = %s)
                AND (%s IS NULL OR renta_iva_incluida = %s)
                AND (%s IS NULL OR deposito_garantia_renta = %s)
                AND (%s IS NULL OR meses_gracia_fecha_inicio = %s)
                AND (%s IS NULL OR meses_gracia_fecha_fin = %s)
                AND (%s IS NULL OR renta_anticipada_fecha_inicio = %s)
                AND (%s IS NULL OR renta_anticipada_fecha_fin = %s)
                AND (%s IS NULL OR renta_anticipada_renta_iva_incluida = %s)
                AND (%s IS NULL OR incremento_mes = %s)
                AND (%s IS NULL OR inicio_vigencia = %s)
                AND (%s IS NULL OR fin_vigencia_forzosa = %s)
                AND (%s IS NULL OR fin_vigencia_no_forzosa = %s)
                AND (%s IS NULL OR vigencia = %s)
                AND (%s IS NULL OR tiempo_restante = %s)
            LIMIT %s OFFSET %s;
        """

        params = (
            nombre_comercial, nombre_comercial,
            razon_social, razon_social,
            renta_iva_incluida, renta_iva_incluida,
            deposito_garantia_renta, deposito_garantia_renta,
            meses_gracia_fecha_inicio, meses_gracia_fecha_inicio,
            meses_gracia_fecha_fin, meses_gracia_fecha_fin,
            renta_anticipada_fecha_inicio, renta_anticipada_fecha_inicio,
            renta_anticipada_fecha_fin, renta_anticipada_fecha_fin,
            renta_anticipada_renta_iva_incluida, renta_anticipada_renta_iva_incluida,
            incremento_mes, incremento_mes,
            inicio_vigencia, inicio_vigencia,
            fin_vigencia_forzosa, fin_vigencia_forzosa,
            fin_vigencia_no_forzosa, fin_vigencia_no_forzosa,
            vigencia, vigencia,
            tiempo_restante, tiempo_restante,
            page_size, offset
        )

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# CREATE TABLE propiedad_renta(
#     propiedad_id INT NOT NULL REFERENCES propiedad(id) ON DELETE CASCADE,
#     renta_id INT NOT NULL REFERENCES renta(id) ON DELETE CASCADE,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE (propiedad_id, renta_id)
# );
propiedad_renta_parser = reqparse.RequestParser()
propiedad_renta_parser.add_argument('propiedad_id', type=int, help='Opcional: ID de la propiedad')
propiedad_renta_parser.add_argument('renta_id', type=int, help='Opcional: ID de la renta')

propiedad_renta_client = Namespace('propiedad_renta', description='Propiedad Renta de la base de datos')
@propiedad_renta_client.route('/')
class PropiedadRenta(Resource):
    @api.expect(generic_parser, propiedad_renta_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = propiedad_renta_parser.parse_args()

        propiedad_id = another_args.get('propiedad_id')
        renta_id = another_args.get('renta_id')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_id',
            'renta_id',
            'created_at',
            'updated_at'
        ]

        query = """
            SELECT
                propiedad_id,
                renta_id,
                created_at,
                updated_at
            FROM propiedad_renta
            WHERE
                (%s IS NULL OR propiedad_id = %s)
                AND (%s IS NULL OR renta_id = %s)
            LIMIT %s OFFSET %s;
        """

        params = (propiedad_id, propiedad_id, renta_id, renta_id, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

api.add_namespace(sociedades_client)
api.add_namespace(estatus_legal_client)
api.add_namespace(ubicacion_client)
api.add_namespace(proyectos_client)
api.add_namespace(proyecto_sociedad_client)
api.add_namespace(proyecto_estatus_ubicacion_client)
api.add_namespace(propiedades_client)
api.add_namespace(renta_client)
api.add_namespace(propiedad_renta_client)