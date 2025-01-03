# create virutal enviroment = python3 -m venv venv
# open virtual environment = source venv/bin/activate
# install dependencies = pip install -r requirements.txt
# turn on the api = python3 main.py

import os
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
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            sslmode='require'
        )
        print("Connected to the database")
        return connection
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


# -- Tabla principal: Propiedades
# CREATE TABLE propiedades (
#     id SERIAL PRIMARY KEY,
#     proyecto_id INT NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
#     nombre VARCHAR(255) NOT NULL,
#     propietario VARCHAR(255),
#     clave_catastral VARCHAR(255) UNIQUE,
#     localizacion VARCHAR(255),
#     superficie_total_m2 DECIMAL(15, 2),
#     base_predial DECIMAL(10, 2),
#     adeudo_predial DECIMAL(10, 2),
#     valor_comercial DECIMAL(15, 2),
#     valor_comercial_usd DECIMAL(15, 2),
#     anio_valor_comercial INT,
#     participacion_porcentaje DECIMAL(3, 2),
#     anios_pend_predial INT,
#     comentarios TEXT,
#     fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
propiedades_parser = reqparse.RequestParser()
propiedades_parser.add_argument('clave_catastral', type=str, help='Opcional: Clave catastral de la propiedad')
propiedades_parser.add_argument('proyecto_id', type=int, help='Opcional: ID del proyecto')
propiedades_parser.add_argument('total_m2', type=bool, help='Opcional: Superficie total de todas las propiedades')
propiedades_parser.add_argument('adeudo_predial', type=int, help='Opcional: Propiedades con adeudo predial mayor a X')

propiedades_client = Namespace('propiedades', description='Propiedades de la base de datos')
@propiedades_client.route('/')
class Propiedades(Resource):
    @api.expect(generic_parser, propiedades_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = propiedades_parser.parse_args()

        total_m2 = another_args.get('total_m2')
        proyecto_id = another_args.get('proyecto_id')
        adeudo_predial = another_args.get('adeudo_predial')
        clave_catastral = another_args.get('clave_catastral')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        if total_m2:
            query = """
                SELECT 
                    SUM(superficie_total_m2) AS total_superficie_m2
                FROM propiedades;
            """

            columns = [
                'total_superficie_m2'
            ]

            params = ()
        else:
            columns = [
                'id',
                'proyecto_id',
                'nombre',
                'propietario',
                'clave_catastral',
                'localizacion',
                'superficie_total_m2',
                'base_predial',
                'adeudo_predial',
                'valor_comercial',
                'valor_comercial_usd',
                'anio_valor_comercial',
                'participacion_porcentaje',
                'anios_pend_predial',
                'comentarios',
                'fecha_registro'
            ]

            if adeudo_predial:
                query = """
                    SELECT
                        propiedades.id,
                        propiedades.proyecto_id,
                        propiedades.nombre,
                        propiedades.propietario,
                        propiedades.clave_catastral,
                        propiedades.localizacion,
                        propiedades.superficie_total_m2,
                        propiedades.base_predial,
                        propiedades.adeudo_predial,
                        propiedades.valor_comercial,
                        propiedades.valor_comercial_usd,
                        propiedades.anio_valor_comercial,
                        propiedades.participacion_porcentaje,
                        propiedades.anios_pend_predial,
                        propiedades.comentarios,
                        propiedades.fecha_registro
                    FROM propiedades
                    WHERE
                        propiedades.adeudo_predial > %s
                    LIMIT %s OFFSET %s;
                """

                params = (adeudo_predial, page_size, offset)
            else:
                query = """
                    SELECT
                        propiedades.id,
                        propiedades.proyecto_id,
                        propiedades.nombre,
                        propiedades.propietario,
                        propiedades.clave_catastral,
                        propiedades.localizacion,
                        propiedades.superficie_total_m2,
                        propiedades.base_predial,
                        propiedades.adeudo_predial,
                        propiedades.valor_comercial,
                        propiedades.valor_comercial_usd,
                        propiedades.anio_valor_comercial,
                        propiedades.participacion_porcentaje,
                        propiedades.anios_pend_predial,
                        propiedades.comentarios,
                        propiedades.fecha_registro
                    FROM propiedades
                    WHERE
                        (%s IS NULL OR propiedades.clave_catastral = %s)
                        AND (%s IS NULL OR propiedades.proyecto_id = %s)
                    LIMIT %s OFFSET %s;
                """

                params = (clave_catastral, clave_catastral, proyecto_id, proyecto_id, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Tabla Proyectos
# CREATE TABLE proyectos (
#     id SERIAL PRIMARY KEY,
#     nombre VARCHAR(255) NOT NULL,
#     propietario VARCHAR(255) NOT NULL,
#     ubicacion VARCHAR(255),
#     sociedad_id INT REFERENCES sociedades(id_sociedad) ON DELETE SET NULL
# );
proyectos_parser = reqparse.RequestParser()
proyectos_parser.add_argument('nombre', type=str, help='Opcional: Nombre del proyecto')
proyectos_parser.add_argument('sociedad_id', type=int, help='Opcional: ID de la sociedad')

proyectos_client = Namespace('proyectos', description='Proyectos de la base de datos')
@proyectos_client.route('/')
class Proyectos(Resource):
    @api.expect(generic_parser, proyectos_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = proyectos_parser.parse_args()

        nombre = another_args.get('nombre')
        sociedad_id = another_args.get('sociedad_id')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'nombre',
            'propietario',
            'ubicacion',
            'sociedad_id'
        ]

        query = """
            SELECT
                proyectos.id,
                proyectos.nombre,
                proyectos.propietario,
                proyectos.ubicacion,
                proyectos.sociedad_id
            FROM proyectos
            WHERE
                (%s IS NULL OR proyectos.nombre = %s)
                AND (%s IS NULL OR proyectos.sociedad_id = %s)
            LIMIT %s OFFSET %s;
        """

        params = (nombre, nombre, sociedad_id, sociedad_id, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Tabla Sociedades
# CREATE TABLE sociedades (
#     id_sociedad SERIAL PRIMARY KEY,
#     nombre VARCHAR(255),
#     ubicacion VARCHAR(255),
#     propietario VARCHAR(255),
#     sociedad VARCHAR(255) UNIQUE,
#     estatus_legal VARCHAR(255),
#     superficie_m2 DECIMAL(15, 2),
#     suma_superficie DECIMAL(15, 2),
#     participacion DECIMAL(15, 2),
#     comentarios TEXT
# );
sociedades_parser = reqparse.RequestParser()
sociedades_parser.add_argument('nombre', type=str, help='Opcional: Nombre de la sociedad')
sociedades_parser.add_argument('total_superficie', type=bool, help='Opcional: Superficie total de todas las sociedades')

sociedades_client = Namespace('sociedades', description='Sociedades de la base de datos')
@sociedades_client.route('/')
class Sociedades(Resource):
    @api.expect(generic_parser, sociedades_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = sociedades_parser.parse_args()

        nombre = another_args.get('nombre')
        total_superficie = another_args.get('total_superficie')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        if total_superficie:
            query = """
                SELECT 
                    SUM(superficie_m2) AS total_superficie_m2
                FROM sociedades;
            """

            columns = [
                'total_superficie_m2'
            ]

            params = ()
        else:
            columns = [
                'id_sociedad',
                'nombre',
                'ubicacion',
                'propietario',
                'sociedad',
                'estatus_legal',
                'superficie_m2',
                'suma_superficie',
                'participacion',
                'comentarios'
            ]

            query = """
                SELECT
                    sociedades.id_sociedad,
                    sociedades.nombre,
                    sociedades.ubicacion,
                    sociedades.propietario,
                    sociedades.sociedad,
                    sociedades.estatus_legal,
                    sociedades.superficie_m2,
                    sociedades.suma_superficie,
                    sociedades.participacion,
                    sociedades.comentarios
                FROM sociedades
                WHERE
                    (%s IS NULL OR sociedades.nombre = %s)
                LIMIT %s OFFSET %s;
            """

            params = (nombre, nombre, page_size, offset)
        
        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Tabla Contratos
# CREATE TABLE contratos (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id) ON DELETE CASCADE,
#     inquilino_nombre VARCHAR(255) NOT NULL,
#     fecha_inicio DATE NOT NULL,
#     fecha_fin_forzosa DATE,
#     fecha_fin_no_forzosa DATE,
#     duracion INTERVAL,
#     renta_mensual DECIMAL(15, 2),
#     politica_incrementos VARCHAR(255),
#     tiempo_restante INT
# );
contratos_parser = reqparse.RequestParser()
contratos_parser.add_argument('contratos_vigentes', type=bool, help='Opcional: Contratos vigentes')
contratos_parser.add_argument('renta_total', type=bool, help='Opcional: Renta total de todos los contratos')

contratos_client = Namespace('contratos', description='Contratos de la base de datos')
@contratos_client.route('/')
class Contratos(Resource):
    @api.expect(generic_parser, contratos_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = contratos_parser.parse_args()

        contratos_vigentes = another_args.get('contratos_vigentes')
        renta_total = another_args.get('renta_total')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        if renta_total:
            query = """
                SELECT 
                    SUM(renta_mensual) AS total_renta_mensual
                FROM contratos
                WHERE fecha_fin_forzosa > CURRENT_DATE OR fecha_fin_forzosa IS NULL;
            """

            columns = [
                'total_renta_mensual'
            ]

            params = ()
        else:
            if contratos_vigentes:
                query = """
                    SELECT *
                    FROM contratos
                    WHERE
                        fecha_inicio <= CURRENT_DATE AND (fecha_fin_forzosa IS NULL OR fecha_fin_forzosa > CURRENT_DATE)
                    LIMIT %s OFFSET %s;
                """
            else:
                query = """
                    SELECT *
                    FROM contratos
                    LIMIT %s OFFSET %s;
                """

            columns = [
                'id',
                'propiedad_id',
                'inquilino_nombre',
                'fecha_inicio',
                'fecha_fin_forzosa',
                'fecha_fin_no_forzosa',
                'duracion',
                'renta_mensual',
                'politica_incrementos',
                'tiempo_restante'
            ]

            params = (page_size,offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Tabla Finanzas
# CREATE TABLE financieros (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id) ON DELETE CASCADE,
#     renta_mensual DECIMAL(15, 2),
#     politica_incrementos VARCHAR(255),
#     renta_total DECIMAL(20, 2)
# );
finanzas_parser = reqparse.RequestParser()
finanzas_parser.add_argument('renta_total', type=bool, help='Opcional: Renta total de todas las propiedades')

finanzas_client = Namespace('finanzas', description='Finanzas de la base de datos')
@finanzas_client.route('/')
class Finanzas(Resource):
    @api.expect(generic_parser, finanzas_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = finanzas_parser.parse_args()

        renta_total = another_args.get('renta_total')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        if renta_total:
            query = """
                SELECT 
                    SUM(renta_total) AS total_renta_total
                FROM financieros;
            """

            columns = [
                'total_renta_total'
            ]

            params = ()
        else:
            columns = [
                'id',
                'propiedad_id',
                'renta_mensual',
                'politica_incrementos',
                'renta_total'
            ]

            query = """
                SELECT *
                FROM financieros
                LIMIT %s OFFSET %s;
            """

            params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Tabla Incidencias
# CREATE TABLE incidencias (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT REFERENCES propiedades(id) ON DELETE CASCADE,
#     contrato_id INT REFERENCES contratos(id) ON DELETE CASCADE,
#     descripcion TEXT NOT NULL,
#     fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
incidencias_parser = reqparse.RequestParser()
incidencias_parser.add_argument('propiedad_id', type=int, help='Opcional: ID de la propiedad')

incidencias_client = Namespace('incidencias', description='Incidencias de la base de datos')
@incidencias_client.route('/')
class Incidencias(Resource):
    @api.expect(generic_parser, incidencias_parser)
    def get(self):
        args = generic_parser.parse_args()
        another_args = incidencias_parser.parse_args()

        propiedad_id = another_args.get('propiedad_id')

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'id',
            'propiedad_id',
            'contrato_id',
            'descripcion',
            'fecha_creacion'
        ]

        query = """
            SELECT *
            FROM incidencias
            WHERE
                (%s IS NULL OR incidencias.propiedad_id = %s)
            LIMIT %s OFFSET %s;
        """

        params = (propiedad_id, propiedad_id, page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Ejemplo de tabla especializada: Bilbao Comercial
# CREATE TABLE bilbao_comercial (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id),
#     nombre_comercial VARCHAR(255),
#     predial_participacion DECIMAL(10, 2)
# );
bilbao_comercial_client = Namespace('bilbao_comercial', description='Bilbao Comercial de la base de datos')
@bilbao_comercial_client.route('/')
class BilbaoComercial(Resource):
    @api.expect(generic_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_nombre',
            'nombre_comercial',
            'predial_participacion'
        ]

        query = """
            SELECT p.nombre AS propiedad_nombre, b.nombre_comercial, b.predial_participacion
            FROM bilbao_comercial b
            JOIN propiedades p ON b.propiedad_id = p.id
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Ejemplo de tabla especializada: Andenes
# CREATE TABLE andenes (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id),
#     numero_andenes INT,
#     clave_andenes DECIMAL(3, 2),
#     nombre_andenes VARCHAR(255),
#     vocacion VARCHAR(255),
#     responsable VARCHAR(255),
#     categoria VARCHAR(255),
#     asesor VARCHAR(255),
#     rango_precio VARCHAR(255)
# );
andenes_client = Namespace('andenes', description='Andenes de la base de datos')
@andenes_client.route('/')
class Andenes(Resource):
    @api.expect(generic_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_nombre',
            'numero_andenes',
            'clave_andenes',
            'nombre_andenes',
            'vocacion',
            'responsable',
            'categoria',
            'asesor',
            'rango_precio'
        ]

        query = """
            SELECT p.nombre AS propiedad_nombre, a.numero_andenes, a.clave_andenes, a.nombre_andenes, a.vocacion, a.responsable, a.categoria, a.asesor, a.rango_precio
            FROM andenes a
            JOIN propiedades p ON a.propiedad_id = p.id
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Ejemplo de tabla especializada: Pto Peñasco
# CREATE TABLE pto_peniasco (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id),
#     terreno VARCHAR(255),
#     base_predial DECIMAL(10, 2),
#     adeudo_predial DECIMAL(10, 2),
#     participacion_porcentaje DECIMAL(3, 2)
# );
pto_peniasco_client = Namespace('pto_peniasco', description='Pto Peñasco de la base de datos')
@pto_peniasco_client.route('/')
class PtoPeniasco(Resource):
    @api.expect(generic_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_nombre',
            'terreno',
            'base_predial',
            'adeudo_predial',
            'participacion_porcentaje'
        ]

        query = """
            SELECT p.nombre AS propiedad_nombre, pp.terreno, pp.base_predial, pp.adeudo_predial, pp.participacion_porcentaje
            FROM pto_peniasco pp
            JOIN propiedades p ON pp.propiedad_id = p.id
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Ejemplo de tabla especializada: TWWG Las Palomas
# CREATE TABLE twwg_las_palomas (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id),
#     nombre VARCHAR(100),
#     participacion_porcentaje DECIMAL(3, 2),
#     comentarios TEXT
# );
twwg_las_palomas_client = Namespace('twwg_las_palomas', description='TWWG Las Palomas de la base de datos')
@twwg_las_palomas_client.route('/')
class TwwgLasPalomas(Resource):
    @api.expect(generic_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_nombre',
            'nombre',
            'participacion_porcentaje',
            'comentarios'
        ]

        query = """
            SELECT p.nombre AS propiedad_nombre, t.nombre, t.participacion_porcentaje, t.comentarios
            FROM twwg_las_palomas t
            JOIN propiedades p ON t.propiedad_id = p.id
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})

# -- Ejemplo de tabla especializada: SLRC 1
# CREATE TABLE slrc_1 (
#     id SERIAL PRIMARY KEY,
#     propiedad_id INT NOT NULL REFERENCES propiedades(id),
#     nombre_terreno VARCHAR(255),
#     numero_fraccion INT,
#     base_predial DECIMAL(10, 2),
#     adeudo_predial DECIMAL(10, 2),
#     anios_pend_predial INT,
#     comentarios TEXT
# );
slrc_1_client = Namespace('slrc_1', description='SLRC 1 de la base de datos')
@slrc_1_client.route('/')
class Slrc1(Resource):
    @api.expect(generic_parser)
    def get(self):
        args = generic_parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')
        offset = (page - 1) * page_size

        columns = [
            'propiedad_nombre',
            'nombre_terreno',
            'numero_fraccion',
            'base_predial',
            'adeudo_predial',
            'anios_pend_predial',
            'comentarios'
        ]

        query = """
            SELECT p.nombre AS propiedad_nombre, s.nombre_terreno, s.numero_fraccion, s.base_predial, s.adeudo_predial, s.anios_pend_predial, s.comentarios
            FROM slrc_1 s
            JOIN propiedades p ON s.propiedad_id = p.id
            LIMIT %s OFFSET %s;
        """

        params = (page_size, offset)

        try:
            result = execute_query(query, columns, params)
            return jsonify(result)
        except PGError as e:
            return jsonify({'message': str(e)})


api.add_namespace(propiedades_client)
api.add_namespace(proyectos_client)
api.add_namespace(sociedades_client)
api.add_namespace(contratos_client)
api.add_namespace(finanzas_client)
api.add_namespace(incidencias_client)
api.add_namespace(bilbao_comercial_client)
api.add_namespace(andenes_client)
api.add_namespace(pto_peniasco_client)
api.add_namespace(twwg_las_palomas_client)
api.add_namespace(slrc_1_client)

# app = WSGIMiddleware(app)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))  # Usa 5000 como valor predeterminado
#     app.run(host="0.0.0.0", port=port, debug=True)
