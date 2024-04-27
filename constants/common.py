import decimal
import os
import uuid
from enum import Enum
from datetime import date, time
from dateutil import parser


############################################################################################
# Global constants
##############################################
# Path
basedir = os.path.dirname(__file__)
basedir = os.path.abspath(os.path.join(basedir, ".."))

MASTER_PASSWORD_DB_PATH             = os.path.join(basedir, "database", "master_password.db")
CONNECTION_PROFILES_DATABASE_PATH   = os.path.join(basedir, "database", "connection_profiles.sqlite")
CONNECTION_WINDOW_UI_PATH           = os.path.join(basedir, "frontend", "connection_window.ui")
MAIN_WINDOW_UI_PATH                 = os.path.join(basedir, "frontend", "main_window.ui")
TABLE_UI_PATH                       = os.path.join(basedir, "frontend", "table.ui")
EXPORT_WINDOW_PATH                  = os.path.join(basedir, "frontend", "export_form.ui")
IMPORT_WINDOW_PATH                  = os.path.join(basedir, "frontend", "import_form.ui")
CQL_EDITOR_PATH                     = os.path.join(basedir, "frontend", "cql_editor.ui")
CREATE_TABLE_WINDOW_PATH            = os.path.join(basedir, "frontend", "create_table.ui")
CREATE_COLUMN_FRAME_PATH            = os.path.join(basedir, "frontend", "create_table_column.ui")
CREATE_KEY_SPACE_WINDOW_PATH        = os.path.join(basedir, "frontend", "create_key_space.ui")
DATACENTER_REPLICATION_FRAME_PATH   = os.path.join(basedir, "frontend", "datacenter_replication_factor.ui")
CREATE_MASTER_PASSWORD_WINDOW_PATH  = os.path.join(basedir, "frontend", "create_master_password.ui")
CHANGE_MASTER_PASSWORD_WINDOW_PATH  = os.path.join(basedir, "frontend", "change_master_password.ui")
AUTH_MASTER_PASSWORD_WINDOW_PATH    = os.path.join(basedir, "frontend", "authenticate_master_password.ui")

# Lables
DATABASE_NAVIGATION_HEADER          = "Database navigation"
RESULT_STATISTICS                   = "Result statistics:"
SUCCESS                             = "Success"
NO_TABLE                            = "No Table created."

##############################################
# Database tables
CONNECTION_PROFILES_TABLE   = "connection_profiles"
MASTER_PASSWORD_TABLE       = "master_password"

############################################################################################
# Enums
class ConfirmationMessages(Enum):
    DELETE = "Are you sure you want to delete it?"

class ErrorTitles(Enum):
    Error                   = "Error"
    Connection_profiles     = "Cassandra Tool - Connection profiles - Error!"
    Db_Connection_profiles  = "Database - Connection profiles - Error!"
    Db_Cassandra_error      = "Cassandra Database Error!"
    Failed                  = "Failed:"

class ExportTypes(Enum):
    CSV     = "CSV"
    JOSN    = "JSON"
    XML     = "XML"

class TreeViewDepthLevel(Enum):
    db_name     = 0
    key_space   = 1
    table       = 2

class TreeViewActionType(Enum):
    create_key_space = "Create Keyspace"
    refresh          = "Refresh"
    delete_key_space = "Delete Keyspace"
    create_table     = "Create Table"
    delete_table     = "Delete Table"

class OrderBy(Enum):
    ASC  = "ASC"
    DESC = "DESC"

class ReplicationClass(Enum):
    SimpleStrategy          = "SimpleStrategy"
    NetworkTopologyStrategy = "NetworkTopologyStrategy"

############################################################################################
# Mapping
CASSANDRA_TYPE_MAPPING = {
    'NULL': type(None),
    'boolean': bool,
    'double': float,
    'float': float,
    'int': int,
    'bigint': int,
    'varint': int,
    'smallint': int,
    'tinyint': int,
    'counter': int,
    'decimal': decimal.Decimal,
    'ascii': str,
    'varchar': str,
    'text': str,
    'blob': bytearray,
    'date': date,
    'timestamp': parser.parse,
    'time': time,
    'list': list,
    'set': set,
    'map': dict,
    'timeuuid': uuid.UUID,
    'uuid': uuid.UUID,
    'inet': str,
    'vector': float,
    'duration': str
}