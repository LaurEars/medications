import MySQLdb as sql
import json

'''
Fields present:
  `SETID` varchar(64) NOT NULL DEFAULT '',
  `author_type` varchar(32) DEFAULT NULL,
  `FILE_NAME` varchar(64) DEFAULT NULL,
  `LABEL_EFFECTIVE_TIME` varchar(16) DEFAULT NULL,
  `PRODUCT_CODE` varchar(16) NOT NULL DEFAULT '',
  `NDC9` varchar(9) DEFAULT NULL,
  `PART_NUM` smallint(6) DEFAULT NULL,
  `MEDICINE_NAME` varchar(255) DEFAULT NULL,
  `PART_MEDICINE_NAME` varchar(255) DEFAULT NULL,
  `author` varchar(128) DEFAULT NULL,
  `SPLIMPRINT` varchar(64) DEFAULT NULL,
  `SPLCOLOR` varchar(32) DEFAULT NULL,
  `SPLSCORE` int(2) DEFAULT NULL,
  `SPLSHAPE` varchar(16) DEFAULT NULL,
  `SPLSIZE` decimal(7,2) DEFAULT NULL,
  `DEA_SCHEDULE_CODE` varchar(32) DEFAULT NULL,
  `SPL_INACTIVE_ING` longtext,
  `NO_RXCUI` int(1) DEFAULT NULL,
  `RXCUI` varchar(255) DEFAULT NULL,
  `RXTTY` varchar(8) DEFAULT NULL,
  `RXSTRING` varchar(512) DEFAULT NULL,
  `image_id` varchar(255) DEFAULT NULL,
  `HAS_IMAGE` int(1) DEFAULT NULL,
  `INGREDIENTS` varchar(2048) DEFAULT NULL,
  `FROM_SIS` int(1) DEFAULT NULL,
  `SPL_INGREDIENTS` varchar(2048) DEFAULT NULL,
  `PROD_MEDICINES_PRIKEY` int(10) unsigned DEFAULT NULL,
  `DOSAGE_FORM` varchar(10) DEFAULT NULL,
  `SPL_STRENGTH` varchar(2048) DEFAULT NULL,
  `RXNORM_SOURCE` varchar(10) DEFAULT NULL,
  `SPL_ID` int(8) NOT NULL DEFAULT '0',
  `source` varchar(20) DEFAULT NULL,
  `document_type` varchar(64) DEFAULT NULL,
  `ACTIVE_MOEITY` varchar(1024) DEFAULT NULL,
  `MARKETING_ACT_CODE` varchar(16) DEFAULT NULL,
  `APPROVAL_CODE` varchar(16) DEFAULT NULL,
  `IMAGE_SOURCE` varchar(10) DEFAULT NULL

DEA_SCHEDULE_CODE       DEA_schedule
color_number    color   SPL_code        hex_value
shape_number    shape_type      SPL_code
'''

# constants
name = {'color': 'color', 'shape': 'shape_type', 'dea': 'DEA_schedule'}
table_name = {'color': 'SPLCOLOR', 'shape': 'SPLSHAPE', 'dea': 'DEA_SCHEDULE_CODE'}
table = {'master':'pillbox_master', 'color':'SPL_color_lookup', 'shape':'SPL_shape_lookup', 'dea':'SPL_DEA_lookup'}

select_color = "SELECT * FROM " + table['color']
select_shape = "SELECT * FROM " + table['shape']

# read .settings file
with open('.settings','rb') as settings_file:
    settings = json.load(settings_file)

# set up database
db = sql.connect(host=settings['host'],
                 user=settings['user'],
                 passwd=settings['passwd'],
                 db=settings['db'])
cur = db.cursor()

# grab colors (by code), code (by color/shape), and
color = {}
code = {}
shape = {}

# get colors
cur.execute(select_color)
for row in cur.fetchall():
    color[row[2]] = row[1]
    code[row[1]] = row[2]
# get shapes
cur.execute(select_shape)
for row in cur.fetchall():
    shape[row[2]] = row[1]
    code[row[1]] = row[2]


# print colors/shapes/dea
def print_colors(cur):
    select_color = "SELECT * FROM " + table['color']
    cur.execute(select_color)
    print "-"*30
    print "Colors"
    print "-"*30
    for row in cur.fetchall():
        print row


def print_shapes(cur):
    print "-"*30
    print "Shapes"
    print "-"*30
    select_shape = "SELECT * FROM " + table['shape']
    cur.execute(select_shape)
    for row in cur.fetchall():
        print row


def print_dea(cur):
    print "-"*30
    print "DEA"
    print "-"*30
    cur.execute("SELECT * FROM " + table['dea'])
    for row in cur.fetchall():
        print row


def bad_replacement_string(query_string, replacement_items):
    # The escape sequence for mysqldb doesn't seem to work properly so i'll use this right now
    query = query_string % replacement_items
    return query


search_string = "SELECT %s FROM pillbox_master WHERE %s='%s' and %s='%s'"
search_tuple = ('MEDICINE_NAME', table_name['color'], code['Green'], table_name['shape'], code['Pentagon (5 sides)'],)
print search_string % search_tuple
print "All medicines that are green and have 5 sides"
cur.execute(bad_replacement_string(search_string,search_tuple))
for row in cur.fetchall():
    print row
cur.close()
db.close()